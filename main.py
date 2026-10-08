"""Interfaz gráfica del Analizador Semántico. Ejecutar: python main.py."""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from lexer import Lexer
from parser import Parser, ParseError
from semantic import SemanticAnalyzer


EXAMPLE = '''int edad = 20;
float promedio = 85.5;
string nombre = "Erick";
bool activo = true;
int contador = 0;

if (edad >= 18 && activo) {
    print(nombre);
}

while (contador < 10) {
    contador = contador + 1;
}
'''


class Application:
    def __init__(self, root):
        self.root = root
        root.title("Analizador Semántico")
        root.geometry("1050x750")
        root.minsize(780, 580)
        root.configure(bg="#f2f4f7")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f2f4f7")
        style.configure("TLabel", background="#f2f4f7", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 19, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 6))
        style.configure("Analyze.TButton", background="#d8e9fa")
        style.configure("Treeview", rowheight=25, font=("Segoe UI", 10))

        container = ttk.Frame(root, padding=16)
        container.pack(fill="both", expand=True)
        ttk.Label(container, text="Analizador Semántico", style="Title.TLabel").pack(anchor="w")
        ttk.Label(container, text="Código fuente → análisis léxico → análisis sintáctico → análisis semántico → resultado").pack(anchor="w", pady=(4, 12))
        toolbar = ttk.Frame(container)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Button(toolbar, text="Analizar", command=self.analyze, style="Analyze.TButton").pack(side="left")
        ttk.Button(toolbar, text="Limpiar", command=self.clear).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Cargar ejemplo", command=self.load_example).pack(side="left")
        ttk.Label(toolbar, text="Ctrl+Enter: analizar").pack(side="right")

        panes = ttk.Panedwindow(container, orient="vertical")
        panes.pack(fill="both", expand=True)
        editor_panel = ttk.Frame(panes)
        panes.add(editor_panel, weight=3)
        ttk.Label(editor_panel, text="Código fuente").pack(anchor="w", pady=(0, 6))
        editor_frame = ttk.Frame(editor_panel)
        editor_frame.pack(fill="both", expand=True)
        self.line_numbers = tk.Canvas(editor_frame, width=48, bg="#e9edf2", highlightthickness=0)
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        self.editor = tk.Text(editor_frame, wrap="none", undo=True, font=("Consolas", 11),
                              bg="white", fg="#202a35", padx=8, pady=6, relief="flat",
                              tabs=(32,), insertbackground="#202a35")
        self.editor.grid(row=0, column=1, sticky="nsew")
        vertical = ttk.Scrollbar(editor_frame, orient="vertical", command=self.editor.yview)
        vertical.grid(row=0, column=2, sticky="ns")
        horizontal = ttk.Scrollbar(editor_frame, orient="horizontal", command=self.editor.xview)
        horizontal.grid(row=1, column=1, sticky="ew")
        self.editor.configure(yscrollcommand=lambda first, last: self.on_scroll(vertical, first, last),
                              xscrollcommand=horizontal.set)
        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)
        self.editor.bind("<<Modified>>", self.on_modified)
        self.editor.bind("<Configure>", self.draw_line_numbers)
        self.editor.bind("<Control-Return>", self.analyze_shortcut)

        lower = ttk.Panedwindow(panes, orient="horizontal")
        panes.add(lower, weight=2)
        result_panel = ttk.Frame(lower, padding=(0, 10, 8, 0))
        lower.add(result_panel, weight=3)
        ttk.Label(result_panel, text="Resultado del análisis").pack(anchor="w", pady=(0, 6))
        self.results = ScrolledText(result_panel, wrap="word", font=("Consolas", 10),
                                    bg="white", relief="flat", padx=8, pady=8, width=45, height=10,
                                    state="disabled")
        self.results.pack(fill="both", expand=True)
        self.results.tag_configure("success", foreground="#21633b")
        self.results.tag_configure("error", foreground="#a32525")

        symbols_panel = ttk.Frame(lower, padding=(8, 10, 0, 0))
        lower.add(symbols_panel, weight=2)
        ttk.Label(symbols_panel, text="Tabla de símbolos").pack(anchor="w", pady=(0, 6))
        table_frame = ttk.Frame(symbols_panel)
        table_frame.pack(fill="both", expand=True)
        columns = ("name", "type", "line", "scope")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        for column, label, width in zip(columns, ("Variable", "Tipo", "Línea", "Ámbito"), (110, 60, 50, 100)):
            self.table.heading(column, text=label)
            self.table.column(column, width=width, minwidth=45, anchor="w")
        table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=table_scroll.set)
        table_scroll.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True)

        self.status = tk.StringVar(value="Escriba código o cargue el ejemplo.")
        ttk.Label(container, textvariable=self.status).pack(anchor="w", pady=(10, 0))
        self.editor.focus_set()
        self.root.after_idle(self.draw_line_numbers)

    def on_scroll(self, scrollbar, first, last):
        scrollbar.set(first, last)
        self.draw_line_numbers()

    def draw_line_numbers(self, event=None):
        self.line_numbers.delete("all")
        index = self.editor.index("@0,0")
        while True:
            position = self.editor.dlineinfo(index)
            if position is None:
                break
            self.line_numbers.create_text(39, position[1], anchor="ne", text=index.split(".")[0],
                                          font=("Consolas", 11), fill="#667586")
            index = self.editor.index(f"{index}+1line")

    def on_modified(self, event=None):
        if self.editor.edit_modified():
            self.status.set("Código modificado. Pulse Analizar para actualizar los resultados.")
            self.editor.edit_modified(False)
            self.draw_line_numbers()

    def write_result(self, text, tag=None):
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", text, (tag,) if tag else ())
        self.results.configure(state="disabled")

    def clear_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

    def clear(self):
        self.editor.delete("1.0", "end")
        self.editor.edit_reset()
        self.editor.edit_modified(False)
        self.write_result("")
        self.clear_table()
        self.status.set("Escriba código o cargue el ejemplo.")
        self.editor.focus_set()
        self.draw_line_numbers()

    def load_example(self):
        self.clear()
        self.editor.insert("1.0", EXAMPLE)
        self.editor.edit_modified(False)
        self.status.set("Ejemplo cargado. Pulse Analizar.")
        self.draw_line_numbers()

    def analyze_shortcut(self, event):
        self.analyze()
        return "break"

    def analyze(self):
        self.clear_table()
        source = self.editor.get("1.0", "end-1c")
        if not source.strip():
            self.write_result("Escriba código fuente antes de analizar.")
            self.status.set("No hay código para analizar.")
            return
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        if lexer.errors:
            self.show_errors(lexer.errors, "léxico")
            return
        try:
            program = Parser(tokens).parse()
        except ParseError as error:
            self.show_errors([error.diagnostic], "sintáctico")
            return
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(program)
        for symbol in analyzer.symbols:
            self.table.insert("", "end", values=(symbol.name, symbol.data_type, symbol.line, symbol.scope))
        if errors:
            self.show_errors(errors, "semántico")
        else:
            self.write_result("Análisis semántico correcto.\nNo se encontraron errores semánticos.", "success")
            self.status.set(f"Todas las etapas completadas. Variables registradas: {len(analyzer.symbols)}.")

    def show_errors(self, errors, stage):
        self.write_result("\n\n".join(str(error) for error in errors), "error")
        self.status.set(f"Análisis {stage}: {len(errors)} error(es).")


if __name__ == "__main__":
    window = tk.Tk()
    Application(window)
    window.mainloop()
