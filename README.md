# Analizador Semántico

Proyecto académico para la asignatura de Compiladores: una aplicación de escritorio en Python y Tkinter que revisa un lenguaje pequeño con variables, expresiones, `print`, `if/else` y `while`.

El análisis semántico comprueba el significado del código después de verificar sus tokens y su estructura. Por ejemplo, `int edad = "Erick";` tiene una estructura válida, pero su tipo es incorrecto.

## Objetivo y proceso

Comprender cómo una tabla de símbolos y las reglas de tipos permiten detectar errores antes de ejecutar un programa.

```text
Código fuente → lexer → tokens → parser → AST → analizador semántico → resultado
```

El AST es un árbol de objetos sencillos que representa declaraciones, asignaciones, bloques y expresiones. El analizador lo recorre y consulta los nombres en la tabla de símbolos.

**La aplicación analiza código; no lo ejecuta.** `print` se revisa, pero no imprime el valor de su argumento. Los ciclos no se ejecutan y ambos bloques de un `if/else` se revisan.

## Tecnologías

- Python 3.10 o posterior (probado con Python 3.12).
- Tkinter y `ttk` para la ventana, el editor y la tabla.
- `dataclasses` y `re` de la biblioteca estándar.
- Windows 11 como plataforma objetivo.

No requiere instalar paquetes externos. La instalación habitual de Python para Windows incluye Tkinter; mantenga activada la opción Tcl/Tk al instalar Python.

## Estructura de archivos

| Archivo | Función |
| --- | --- |
| `main.py` | Ventana, editor con números de línea, botones, resultados y tabla de símbolos. Coordina las tres etapas. |
| `lexer.py` | Reconoce tokens y registra su tipo, valor, línea y columna. Detecta caracteres y cadenas inválidos. |
| `parser.py` | Comprueba la sintaxis mediante descenso recursivo y construye un AST sencillo. |
| `semantic.py` | Recorre el AST, administra ámbitos y comprueba declaraciones, asignaciones y operadores. |
| `README.md` | Presentación, instrucciones de ejecución y explicación del proyecto. |
| `PRUEBAS.md` | Ejemplos correctos e incorrectos con resultados esperados. |
| `GRAMATICA.md` | Sintaxis, precedencia y reglas del lenguaje. |

## Cómo ejecutar

Abra una terminal en la carpeta actual del proyecto y ejecute:

```powershell
python main.py
```

Se abre una ventana titulada **Analizador Semántico**. La terminal sirve para iniciar la aplicación; la interacción se realiza en la ventana. En Windows también puede utilizar `py main.py` si ese es el comando disponible para su instalación.

1. Escriba código o pulse **Cargar ejemplo**.
2. Pulse **Analizar** o `Ctrl+Enter`.
3. Revise el resultado y la tabla de símbolos.
4. Pulse **Limpiar** para vaciar el editor, los resultados y la tabla.

El editor permite deshacer con `Ctrl+Z`. Después de modificar el código, pulse nuevamente **Analizar**: el estado inferior indica que los resultados anteriores necesitan actualizarse.

No se ha generado un `.exe`. El proyecto mantiene un punto de entrada habitual para un empaquetado posterior con PyInstaller.

## Errores detectados

- Uso o asignación de una variable no declarada.
- Dos declaraciones del mismo nombre dentro del mismo ámbito.
- Inicialización o asignación incompatible con el tipo de la variable.
- Operaciones aritméticas y relacionales con tipos inválidos.
- Uso de `&&`, `||` o `!` con valores que no sean `bool`.
- Condiciones de `if` o `while` que no produzcan `bool`.
- Comparaciones de igualdad entre tipos incompatibles.
- Uso de una variable fuera del bloque donde se declaró.

También se muestran errores léxicos y sintácticos. Si hay errores léxicos, las etapas siguientes no se ejecutan. El parser informa el primer error sintáctico; el analizador semántico acumula los errores que encuentra en un programa sintácticamente válido. Un tipo desconocido por un error previo no genera errores derivados innecesarios.

Los mensajes incluyen línea y columna, contadas desde 1. La tabla muestra variable, tipo, línea de declaración y ámbito. Con errores semánticos, muestra las declaraciones registradas, incluso aquellas cuya inicialización es incorrecta. Una redeclaración no agrega una segunda entrada. Si falla el lexer o el parser, la tabla queda vacía.

## Ejemplo correcto

```text
int edad = 20;
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
```

Resultado:

```text
Análisis semántico correcto.
No se encontraron errores semánticos.
```

La tabla contiene `edad: int`, `promedio: float`, `nombre: string`, `activo: bool` y `contador: int`, todas en el ámbito global.

## Ejemplo con error

```text
int edad = 20;
edad = "Hola";
```

Resultado:

```text
Error semántico en línea 2, columna 1:
No se puede asignar un valor de tipo string a la variable 'edad' de tipo int.
```

## Alcance académico

Se permite convertir implícitamente `int` a `float`; no se permite `float` a `int`. No se implementa sintaxis de conversiones explícitas. Una división produce `float`, por lo que `int n = 4 / 2;` se rechaza y `float n = 4 / 2;` se acepta.

Las declaraciones sin inicialización son válidas. Este proyecto comprueba declaraciones y tipos, pero no hace análisis de inicialización definida: no detecta una lectura antes de asignar un valor, ni una referencia a la propia variable en su inicializador. Tampoco calcula valores, comprueba divisiones por cero ni detecta ciclos infinitos. No incluye funciones, arreglos, conversiones, `for`, `break` ni ejecución de código.

Para explicar el proyecto en clase, siga el recorrido `Lexer.tokenize()` → `Parser.parse()` → `SemanticAnalyzer.analyze()` y muestre cómo `expression_type()` obtiene el tipo de una expresión antes de asignarla a una variable.
