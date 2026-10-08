"""Analizador descendente recursivo y nodos sencillos del AST."""

from dataclasses import dataclass
from lexer import Diagnostic, Token


@dataclass
class Program:
    statements: list


@dataclass
class Block:
    statements: list


@dataclass
class Declaration:
    name: Token
    data_type: str
    initializer: object = None


@dataclass
class Assignment:
    name: Token
    expression: object


@dataclass
class Print:
    expression: object


@dataclass
class If:
    keyword: Token
    condition: object
    then_block: Block
    else_block: object = None


@dataclass
class While:
    keyword: Token
    condition: object
    body: Block


@dataclass
class Binary:
    left: object
    operator: Token
    right: object


@dataclass
class Unary:
    operator: Token
    operand: object


@dataclass
class Identifier:
    token: Token


@dataclass
class Literal:
    token: Token
    data_type: str


class ParseError(Exception):
    def __init__(self, diagnostic):
        self.diagnostic = diagnostic
        super().__init__(str(diagnostic))


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current
        if token.type != "EOF":
            self.position += 1
        return token

    def accept(self, kind):
        if self.current.type == kind:
            return self.advance()
        return None

    def expect(self, kind, message):
        if self.current.type != kind:
            self.fail(message)
        return self.advance()

    def fail(self, message):
        token = self.current
        found = "fin del código" if token.type == "EOF" else repr(token.value)
        raise ParseError(Diagnostic(
            "sintáctico", f"{message} Se encontró {found}.", token.line, token.column))

    def parse(self):
        self.position = 0
        statements = []
        while self.current.type != "EOF":
            statements.append(self.statement())
        return Program(statements)

    def statement(self):
        kind = self.current.type
        if kind == "TYPE":
            data_type = self.advance().value
            name = self.expect("IDENTIFIER", "Se esperaba un nombre de variable.")
            initializer = self.expression() if self.accept("=") else None
            self.expect(";", "Se esperaba ';' después de la declaración.")
            return Declaration(name, data_type, initializer)
        if kind == "IDENTIFIER":
            name = self.advance()
            self.expect("=", "Se esperaba '=' en la asignación.")
            expression = self.expression()
            self.expect(";", "Se esperaba ';' después de la asignación.")
            return Assignment(name, expression)
        if kind == "PRINT":
            self.advance()
            self.expect("(", "Se esperaba '(' después de print.")
            expression = self.expression()
            self.expect(")", "Se esperaba ')' después de la expresión.")
            self.expect(";", "Se esperaba ';' después de print.")
            return Print(expression)
        if kind in ("IF", "WHILE"):
            keyword = self.advance()
            self.expect("(", f"Se esperaba '(' después de {keyword.value}.")
            condition = self.expression()
            self.expect(")", "Se esperaba ')' después de la condición.")
            body = self.block()
            if kind == "WHILE":
                return While(keyword, condition, body)
            else_block = self.block() if self.accept("ELSE") else None
            return If(keyword, condition, body, else_block)
        if kind == "{":
            return self.block()
        self.fail("Se esperaba una declaración, asignación, print, if, while o bloque.")

    def block(self):
        self.expect("{", "Se esperaba '{' para iniciar el bloque.")
        statements = []
        while self.current.type not in ("}", "EOF"):
            statements.append(self.statement())
        self.expect("}", "Se esperaba '}' para cerrar el bloque.")
        return Block(statements)

    # Cada nivel llama al siguiente: así se respeta la precedencia.
    def expression(self):
        return self.binary(self.logical_and, ("||",))

    def logical_and(self):
        return self.binary(self.equality, ("&&",))

    def equality(self):
        return self.binary(self.comparison, ("==", "!="))

    def comparison(self):
        return self.binary(self.addition, (">", "<", ">=", "<="))

    def addition(self):
        return self.binary(self.multiplication, ("+", "-"))

    def multiplication(self):
        return self.binary(self.unary, ("*", "/", "%"))

    def binary(self, next_level, operators):
        expression = next_level()
        while self.current.type in operators:
            operator = self.advance()
            expression = Binary(expression, operator, next_level())
        return expression

    def unary(self):
        if self.current.type in ("!", "-", "+"):
            operator = self.advance()
            return Unary(operator, self.unary())
        return self.primary()

    def primary(self):
        token = self.current
        literal_types = {"INT": "int", "FLOAT": "float", "STRING": "string", "BOOL": "bool"}
        if token.type in literal_types:
            self.advance()
            return Literal(token, literal_types[token.type])
        if self.accept("IDENTIFIER"):
            return Identifier(token)
        if self.accept("("):
            expression = self.expression()
            self.expect(")", "Se esperaba ')' para cerrar la expresión.")
            return expression
        self.fail("Se esperaba una expresión (literal, variable o paréntesis).")
