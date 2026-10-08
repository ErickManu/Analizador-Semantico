# Pruebas del Analizador Semántico

Pegue cada ejemplo por separado en la ventana y pulse **Analizar**. Los casos correctos deben mostrar:

```text
Análisis semántico correcto.
No se encontraron errores semánticos.
```

Las líneas indicadas se cuentan desde la primera línea del código de cada ejemplo. Los mensajes incluyen también la columna.

## Casos semánticamente correctos

### 1. Cuatro tipos

```text
int edad = 20;
float promedio = 85.5;
string nombre = "Erick";
bool activo = true;
print(nombre);
```

Esperado: sin errores; cuatro símbolos globales con sus tipos y líneas.

### 2. Declaración sin inicialización y asignación posterior

```text
int contador;
contador = 0;
contador = contador + 1;
print(contador);
```

Esperado: sin errores; `contador` de tipo `int`, declarado en línea 1.

### 3. Promoción numérica, precedencia y división

```text
float promedio = 20;
int puntos = 2 + 3 * 4;
float mitad = puntos / 2;
float total = promedio + puntos;
int resto = puntos % 3;
```

Esperado: sin errores; asignación `int` a `float` permitida, `/` produce `float` y `%` produce `int`.

### 4. Condicional con lógica y else

```text
int edad = 20;
bool activo = true;
if (edad >= 18 && activo) {
    print("Mayor");
} else {
    print("Menor");
}
```

Esperado: sin errores; condición `bool`, dos símbolos globales.

### 5. While y operadores unarios

```text
int contador = 0;
bool detener = false;
while (contador < 10 && !detener) {
    contador = contador + 1;
}
int negativo = -(2 + 3);
```

Esperado: sin errores; `contador`, `detener` y `negativo` en la tabla.

### 6. Ámbitos distintos y ocultamiento

```text
int dato = 10;
if (true) {
    string dato = "local";
    print(dato);
}
print(dato);
```

Esperado: sin errores; dos filas `dato`: `int` en `global` y `string` en `bloque 1`.

### 7. Comparación y disyunción

```text
string nombre = "Erick";
bool coincide = nombre == "Erick";
bool resultado = coincide || (2 != 3 && 1 <= 2);
print(resultado);
```

Esperado: sin errores; las igualdades compatibles y los operadores lógicos producen `bool`.

## Casos con errores semánticos

### 1. Variable no declarada

```text
print(nombre);
```

Esperado en línea 1: `La variable 'nombre' no ha sido declarada.` La tabla queda vacía.

### 2. Variable duplicada

```text
int edad = 20;
int edad = 30;
```

Esperado en línea 2: `La variable 'edad' ya fue declarada en este ámbito en la línea 1.` La tabla mantiene una sola entrada.

### 3. Inicialización con tipo incorrecto

```text
int edad = "Erick";
```

Esperado en línea 1: `No se puede asignar un valor de tipo string a la variable 'edad' de tipo int.` La declaración aparece en la tabla.

### 4. Asignación con tipo incorrecto

```text
int edad = 20;
edad = "Hola";
```

Esperado en línea 2: incompatibilidad `string` → `int` para `edad`.

### 5. Operación aritmética incompatible

```text
string nombre = "Erick";
int numero = 10;
numero = nombre + 5;
```

Esperado en línea 3: `El operador '+' requiere valores numéricos (int o float); se obtuvo string y int.` No se agrega un error de asignación derivado de la operación inválida.

### 6. Condición de if no booleana

```text
int edad = 20;
if (edad) {
    print(edad);
}
```

Esperado en línea 2: `La condición de if debe producir un valor booleano (bool); se obtuvo int.`

### 7. Operador lógico con tipos incorrectos

```text
int edad = 20;
if (edad && true) {
    print(edad);
}
```

Esperado en línea 2: `El operador '&&' requiere dos valores booleanos (bool); se obtuvo int y bool.`

### 8. Conversión float a int no permitida

```text
int numero = 20.5;
```

Esperado en línea 1: incompatibilidad `float` → `int` para `numero`.

### 9. Condición de while no booleana

```text
int contador = 0;
while (contador) {
    contador = contador + 1;
}
```

Esperado en línea 2: la condición de `while` debe producir `bool`; se obtuvo `int`.

### 10. Variable fuera de su ámbito

```text
if (true) {
    int local = 1;
}
print(local);
```

Esperado en línea 4: `La variable 'local' no ha sido declarada.` La tabla conserva la declaración local en `bloque 1`.

### 11. Resto con float

```text
float resto = 5.5 % 2;
```

Esperado en línea 1: `%` requiere dos valores `int`.

### 12. Varios errores independientes

```text
int edad = "texto";
print(nombre);
bool activo = 1;
```

Esperado: tres errores semánticos, en líneas 1, 2 y 3. La tabla incluye `edad` y `activo`.

## Verificación de las etapas anteriores

### Carácter inválido (léxico)

```text
int edad = 20;
@
```

Esperado: error léxico en línea 2, columna 1; se detiene el proceso y la tabla queda vacía.

### Cadena sin cerrar (léxico)

```text
string nombre = "Erick;
```

Esperado: error léxico en línea 1, columna 17 por falta de comillas de cierre.

### Falta de punto y coma (sintáctico)

```text
int edad = 20
print(edad);
```

Esperado: error sintáctico en línea 2, columna 1 indicando que se esperaba `;`. No se ejecuta el análisis semántico.

### Falta de llave (sintáctico)

```text
if (true) {
    print("Hola");
```

Esperado: error sintáctico al final del código indicando que se esperaba `}`.

## Verificación de la interfaz

1. Ejecutar `python main.py`: aparece la ventana con el título correcto.
2. Pulsar **Cargar ejemplo** y **Analizar**: resultado correcto y cinco variables globales.
3. Cambiar `int edad = 20;` por `int edad = "Hola";` y analizar: error en línea 1 y tabla visible.
4. Añadir un carácter `@` y analizar: error léxico y tabla vacía.
5. Quitar el carácter inválido y un `;`: error sintáctico y tabla vacía.
6. Pulsar **Limpiar**: se vacían editor, resultado y tabla.
7. Analizar sin código: mensaje `Escriba código fuente antes de analizar.`
8. Escribir varias líneas y desplazar el editor: los números de línea acompañan el desplazamiento.
9. Modificar el código después de analizar: el estado pide actualizar los resultados.

La comprobación interna adicional utiliza solo la biblioteca estándar de Python y revisa las tres etapas, la precedencia del AST, ubicaciones, ámbitos, errores acumulados y acciones básicas de la ventana.
