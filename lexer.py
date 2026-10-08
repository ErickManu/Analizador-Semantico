"""Convierte el código fuente en tokens con su ubicación."""

from dataclasses import dataclass
import re


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


@dataclass
class Diagnostic:
    stage: str
    message: str
    line: int
    column: int

    def __str__(self):
        return (f"Error {self.stage} en línea {self.line}, columna {self.column}:\n"
                f"{self.message}")


KEYWORDS = {
    "int": "TYPE", "float": "TYPE", "string": "TYPE", "bool": "TYPE",
    "print": "PRINT", "if": "IF", "else": "ELSE", "while": "WHILE",
    "true": "BOOL", "false": "BOOL",
}

# Los operadores de dos caracteres se reconocen antes que los de uno.
TOKEN_PATTERN = re.compile(
    r'(?P<SPACE>[ \t\r]+)|(?P<NEWLINE>\n)|(?P<COMMENT>//[^\n]*)'
    r'|(?P<FLOAT>\d+\.\d+)|(?P<INT>\d+)'
    r'|(?P<IDENTIFIER>[a-zA-Z_][a-zA-Z_0-9]*)'
    r'|(?P<OPERATOR>>=|<=|==|!=|&&|\|\||[+\-*/%><=!])'
    r'|(?P<PUNCTUATION>[;(){}])'
)


class Lexer:
    def __init__(self, source):
        self.source = source
        self.errors = []

    def tokenize(self):
        self.errors = []
        tokens = []
        index, line, column = 0, 1, 1
        while index < len(self.source):
            char = self.source[index]
            if char == '"':
                start, start_column = index, column
                index += 1
                column += 1
                closed = False
                while index < len(self.source) and self.source[index] != '\n':
                    current = self.source[index]
                    if current == '"':
                        index += 1
                        column += 1
                        closed = True
                        break
                    if current == "\\":
                        if index + 1 >= len(self.source) or self.source[index + 1] == '\n':
                            index += 1
                            column += 1
                            break
                        if self.source[index + 1] not in ('"', "\\", "n", "t", "r"):
                            self.errors.append(Diagnostic(
                                "léxico", "Secuencia de escape no reconocida.", line, column))
                        index += 2
                        column += 2
                    else:
                        index += 1
                        column += 1
                if closed:
                    tokens.append(Token("STRING", self.source[start:index], line, start_column))
                else:
                    self.errors.append(Diagnostic(
                        "léxico", "Cadena de texto sin comillas de cierre.", line, start_column))
                continue

            match = TOKEN_PATTERN.match(self.source, index)
            if match is None:
                self.errors.append(Diagnostic(
                    "léxico", f"Carácter no reconocido: {char!r}.", line, column))
                index += 1
                column += 1
                continue
            kind, value = match.lastgroup, match.group()
            if kind == "NEWLINE":
                line += 1
                column = 1
            else:
                if kind not in ("SPACE", "COMMENT"):
                    if kind == "IDENTIFIER":
                        kind = KEYWORDS.get(value, kind)
                    elif kind in ("OPERATOR", "PUNCTUATION"):
                        kind = value
                    tokens.append(Token(kind, value, line, column))
                column += len(value)
            index = match.end()
        tokens.append(Token("EOF", "", line, column))
        return tokens
