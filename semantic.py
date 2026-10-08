"""Comprueba ámbitos y tipos sin ejecutar el programa analizado."""

from dataclasses import dataclass
from lexer import Diagnostic
from parser import (Assignment, Binary, Block, Declaration, Identifier, If,
                    Literal, Print, Unary, While)


@dataclass
class Symbol:
    name: str
    data_type: str
    line: int
    scope: str


class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
        self.symbols = []
        self.scopes = []
        self.block_number = 0

    def analyze(self, program):
        self.errors = []
        self.symbols = []
        self.scopes = [{}]
        self.block_number = 0
        self.scope_names = ["global"]
        for statement in program.statements:
            self.visit(statement)
        return self.errors

    def error(self, token, message):
        self.errors.append(Diagnostic("semántico", message, token.line, token.column))

    def lookup(self, token):
        # Se busca primero en el bloque actual y después en los ámbitos exteriores.
        for scope in reversed(self.scopes):
            if token.value in scope:
                return scope[token.value]
        self.error(token, f"La variable '{token.value}' no ha sido declarada.")
        return None

    @staticmethod
    def compatible(destination, source):
        return destination == source or (destination == "float" and source == "int")

    def check_assignment(self, symbol, expression_type, token):
        if expression_type is not None and not self.compatible(symbol.data_type, expression_type):
            self.error(token,
                       f"No se puede asignar un valor de tipo {expression_type} "
                       f"a la variable '{symbol.name}' de tipo {symbol.data_type}.")

    def visit(self, statement):
        if isinstance(statement, Declaration):
            name = statement.name.value
            if name in self.scopes[-1]:
                previous = self.scopes[-1][name]
                self.error(statement.name,
                           f"La variable '{name}' ya fue declarada en este ámbito "
                           f"en la línea {previous.line}.")
                if statement.initializer is not None:
                    self.expression_type(statement.initializer)
                return
            symbol = Symbol(name, statement.data_type, statement.name.line, self.scope_names[-1])
            self.scopes[-1][name] = symbol
            self.symbols.append(symbol)
            if statement.initializer is not None:
                self.check_assignment(symbol, self.expression_type(statement.initializer), statement.name)
        elif isinstance(statement, Assignment):
            symbol = self.lookup(statement.name)
            expression_type = self.expression_type(statement.expression)
            if symbol is not None:
                self.check_assignment(symbol, expression_type, statement.name)
        elif isinstance(statement, Print):
            self.expression_type(statement.expression)
        elif isinstance(statement, Block):
            self.block_number += 1
            self.scopes.append({})
            self.scope_names.append(f"bloque {self.block_number}")
            for child in statement.statements:
                self.visit(child)
            self.scope_names.pop()
            self.scopes.pop()
        elif isinstance(statement, (If, While)):
            condition_type = self.expression_type(statement.condition)
            if condition_type is not None and condition_type != "bool":
                self.error(statement.keyword,
                           f"La condición de {statement.keyword.value} debe producir "
                           f"un valor booleano (bool); se obtuvo {condition_type}.")
            if isinstance(statement, If):
                self.visit(statement.then_block)
                if statement.else_block is not None:
                    self.visit(statement.else_block)
            else:
                self.visit(statement.body)

    def expression_type(self, expression):
        if isinstance(expression, Literal):
            return expression.data_type
        if isinstance(expression, Identifier):
            symbol = self.lookup(expression.token)
            return symbol.data_type if symbol is not None else None
        if isinstance(expression, Unary):
            operand = self.expression_type(expression.operand)
            if operand is None:
                return None
            operator = expression.operator.value
            if operator == "!" and operand == "bool":
                return "bool"
            if operator in ("+", "-") and operand in ("int", "float"):
                return operand
            requirement = "un valor booleano (bool)" if operator == "!" else "un valor numérico (int o float)"
            self.error(expression.operator,
                       f"El operador '{operator}' requiere {requirement}; se obtuvo {operand}.")
            return None
        if isinstance(expression, Binary):
            left = self.expression_type(expression.left)
            right = self.expression_type(expression.right)
            # Un tipo desconocido ya tiene su propio error; evita mensajes en cascada.
            if left is None or right is None:
                return None
            operator = expression.operator.value
            numeric = left in ("int", "float") and right in ("int", "float")
            if operator in ("+", "-", "*", "/"):
                if numeric:
                    return "float" if operator == "/" or "float" in (left, right) else "int"
                message = (f"El operador '{operator}' requiere valores numéricos (int o float); "
                           f"se obtuvo {left} y {right}.")
            elif operator == "%":
                if left == right == "int":
                    return "int"
                message = f"El operador '%' requiere dos valores int; se obtuvo {left} y {right}."
            elif operator in (">", "<", ">=", "<="):
                if numeric:
                    return "bool"
                message = (f"El operador '{operator}' requiere valores numéricos (int o float); "
                           f"se obtuvo {left} y {right}.")
            elif operator in ("==", "!="):
                if left == right or numeric:
                    return "bool"
                message = f"No se pueden comparar valores de tipo {left} y {right} con '{operator}'."
            elif operator in ("&&", "||"):
                if left == right == "bool":
                    return "bool"
                message = (f"El operador '{operator}' requiere dos valores booleanos (bool); "
                           f"se obtuvo {left} y {right}.")
            else:
                raise ValueError(f"Operador desconocido: {operator}")
            self.error(expression.operator, message)
            return None
        raise TypeError(f"Expresión no reconocida: {type(expression).__name__}")
