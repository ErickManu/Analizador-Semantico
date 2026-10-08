# Gramática del lenguaje

El lenguaje usa las palabras reservadas `int`, `float`, `string`, `bool`, `true`, `false`, `print`, `if`, `else` y `while`. Distingue mayúsculas de minúsculas: `edad` y `Edad` son variables diferentes.

## Tipos y valores

| Tipo | Valores de ejemplo | Regla |
| --- | --- | --- |
| `int` | `0`, `20`, `-5` | Enteros decimales; el signo es un operador unario. |
| `float` | `85.5`, `0.5`, `-2.0` | Parte entera y parte decimal obligatorias. |
| `string` | `"Hola"`, `"Erick"` | Texto entre comillas dobles, sin saltos de línea literales. |
| `bool` | `true`, `false` | Valores booleanos en minúsculas. |

Las cadenas permiten los escapes `\n`, `\t`, `\r`, `\"` y `\\`. El lexer conserva el texto del literal porque la aplicación solo necesita determinar su tipo. No se admiten cadenas con comillas simples, números con coma decimal, notación científica ni literales como `.5` o `5.`.

Los identificadores comienzan con una letra ASCII o `_` y continúan con letras ASCII, dígitos o `_`. Ejemplos: `edad`, `promedio_1`, `_contador`. No pueden ser palabras reservadas.

Los espacios y saltos de línea no alteran la estructura. `//` inicia un comentario que termina al final de la línea; los comentarios de bloque `/* ... */` no forman parte del lenguaje.

## Declaraciones y asignaciones

```text
int edad = 20;
float promedio = 90.5;
string nombre = "Erick";
bool activo = true;
int contador;
contador = 5;
contador = contador + 1;
```

Cada declaración, asignación y llamada a `print` termina con `;`. Solo se declara una variable por sentencia. Una asignación es una sentencia; no puede utilizarse como expresión. No se admiten `++`, `+=` ni declaraciones como `int a, b;`.

## Operadores y reglas de tipos

| Operadores | Tipos admitidos | Tipo del resultado |
| --- | --- | --- |
| `+`, `-`, `*` binarios | Dos valores numéricos (`int` o `float`) | `int` si ambos son `int`; en otro caso, `float`. |
| `/` | Dos valores numéricos | Siempre `float`. |
| `%` | Dos `int` | `int`. |
| `+`, `-` unarios | Un valor numérico | El mismo tipo del operando. |
| `>`, `<`, `>=`, `<=` | Dos valores numéricos | `bool`. |
| `==`, `!=` | Dos valores del mismo tipo, o una pareja numérica `int`/`float` | `bool`. |
| `&&`, `\|\|` | Dos `bool` | `bool`. |
| `!` | Un `bool` | `bool`. |

`+` no concatena cadenas. Tampoco se permite sumar booleanos ni ordenar cadenas con `<` o `>`.

Una variable de tipo `float` acepta una expresión `int`:

```text
float promedio = 20;
```

Una variable `int` no acepta una expresión `float`:

```text
int numero = 20.5; // Error semántico.
```

No se implementan conversiones explícitas. Los demás tipos exigen coincidencia exacta.

### Precedencia, de mayor a menor

1. Paréntesis y valores primarios.
2. Unarios `!`, `-`, `+`.
3. `*`, `/`, `%`.
4. `+`, `-`.
5. `>`, `<`, `>=`, `<=`.
6. `==`, `!=`.
7. `&&`.
8. `||`.

Los operadores binarios de un mismo nivel se agrupan de izquierda a derecha. Los unarios se agrupan desde la derecha. Por ejemplo, `2 + 3 * 4` equivale a `2 + (3 * 4)`. Para verificar dos comparaciones escriba `a < b && b < c`; `a < b < c` se interpreta como `(a < b) < c` y produce un error de tipos.

## Impresión

```text
print(contador);
print("Hola");
print(2 + 3);
```

`print` acepta una sola expresión de cualquier tipo válido. El analizador comprueba esa expresión, sin ejecutarla.

## Condicional if/else

```text
if (edad >= 18) {
    print("Mayor");
} else {
    print("Menor");
}
```

La condición debe ser `bool`. Los paréntesis y las llaves son obligatorios. `else` es opcional. Puede anidar otro `if` dentro de un bloque; `else if` directo no está incluido. No se escribe `;` después de un bloque.

## Ciclo while

```text
while (contador < 10) {
    contador = contador + 1;
}
```

La condición debe ser `bool` y el cuerpo debe estar entre llaves. El cuerpo se analiza una vez; el ciclo no se ejecuta.

## Ámbitos

El programa tiene un ámbito global. Cada bloque `{ ... }` crea un ámbito local. Una variable se puede consultar en su bloque y en los bloques interiores, después de su declaración. Al salir del bloque deja de estar disponible. No se permite repetir una declaración dentro del mismo ámbito.

Se admite un mismo nombre en ámbitos diferentes. El nombre local oculta al exterior hasta salir del bloque:

```text
int valor = 10;
if (true) {
    string valor = "local";
    print(valor); // string en este bloque.
}
print(valor); // int en el ámbito global.
```

La tabla conserva ambos registros y muestra su ámbito. Las variables declaradas dentro de un `if` no son visibles en el bloque `else`. Los bloques independientes también están permitidos.

La comprobación es de tipos y declaraciones, sin comprobar que una variable haya recibido un valor antes de ser leída. Una declaración se registra antes de analizar su inicializador.

## Gramática resumida (EBNF)

En esta notación, `{ X }` significa repetición y `[ X ]` significa opcional. Las llaves literales del lenguaje aparecen entre comillas.

```text
programa       = { sentencia } ;
sentencia      = declaracion | asignacion | impresion | condicional | ciclo | bloque ;
declaracion    = tipo, identificador, [ "=", expresion ], ";" ;
tipo           = "int" | "float" | "string" | "bool" ;
asignacion     = identificador, "=", expresion, ";" ;
impresion      = "print", "(", expresion, ")", ";" ;
condicional    = "if", "(", expresion, ")", bloque, [ "else", bloque ] ;
ciclo          = "while", "(", expresion, ")", bloque ;
bloque         = "{", { sentencia }, "}" ;
expresion      = disyuncion ;
disyuncion     = conjuncion, { "||", conjuncion } ;
conjuncion     = igualdad, { "&&", igualdad } ;
igualdad       = comparacion, { ( "==" | "!=" ), comparacion } ;
comparacion    = suma, { ( ">" | "<" | ">=" | "<=" ), suma } ;
suma           = producto, { ( "+" | "-" ), producto } ;
producto       = unaria, { ( "*" | "/" | "%" ), unaria } ;
unaria         = ( "!" | "-" | "+" ), unaria | primaria ;
primaria       = identificador | literal | "(", expresion, ")" ;
literal        = entero | decimal | cadena | "true" | "false" ;
```
