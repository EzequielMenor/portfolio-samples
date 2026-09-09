# Muestra: limpieza de listas de clientes en CSV

Ejemplo ejecutable de limpieza y normalización de una lista de clientes sucia
(típica de un CRM, un formulario web o una exportación a mano): emails rotos,
teléfonos en diez formatos distintos, nombres gritados en mayúsculas, ciudades
sin acentos, duplicados y filas vacías.

**Datos 100% sintéticos.** Los 200 registros de `messy_customers.csv` son
inventados por un script con semilla fija (ninguna persona real). La limpieza
es real: el resumen de abajo es la salida literal del script, no una estimación.

## Qué hace

`clean_customers.py` (solo stdlib, Python 3, sin dependencias):

1. **Trim y colapso de espacios** en todos los campos.
2. **Filas vacías** → eliminadas.
3. **Nombres** → capitalización homogénea, con partículas en minúscula:
   `pilar gómez DE LA torre` → `Pilar Gómez de la Torre`.
4. **Emails** → minúsculas + validación con regex. Si el campo trae varios
   emails pegados (`uno@x.es,otro@x.es`) rescata el primero válido. Los
   inválidos **no se borran ni se inventan**: se conservan tal cual y se
   listan en el reporte para que el cliente decida.
5. **Teléfonos** → formato español legible `+34 6XX XXX XXX`. Tolera
   `600-123-456`, `0034 600123456`, `(+34) 600 123 456`, `Tel. 600 123 456`,
   letras coladas (`96158x6578`), etc. Los no válidos (incompletos, prefijo
   imposible) se conservan y se listan.
6. **Ciudades** → forma canónica con acentos y capitalización correcta
   (`malaga` → `Málaga`, `la coruna` → `A Coruña`) mediante un mapa de alias
   ampliable.
7. **Duplicados** → eliminados conservando la primera aparición. La clave de
   deduplicación se calcula sobre los valores ya normalizados, así que detecta
   tanto copias idénticas como la misma persona escrita con distinta suciedad.

## Cómo usarlo

```bash
# Limpiar el CSV de ejemplo (lee messy_customers.csv, escribe cleaned_customers.csv):
python3 clean_customers.py

# Con tus propios archivos:
python3 clean_customers.py entrada.csv salida.csv

# Regenerar el CSV sucio de ejemplo (determinista, semilla 42):
python3 gen_messy_customers.py
```

## Resumen real de la última ejecución

Salida literal de `python3 clean_customers.py` sobre las 200 filas sintéticas:

```
=== Resumen de limpieza ===
Filas de entrada           : 200
Filas vacías eliminadas    : 6
Duplicados eliminados      : 14
Filas de salida            : 180
Teléfonos normalizados     : 187
Teléfonos no válidos       : 7
Ciudades corregidas        : 83
Emails rescatados (varios) : 6
Emails inválidos           : 53

Cuadre: 200 entrada = 6 vacías + 14 duplicadas + 180 salida
```

De los 14 duplicados, 7 eran copias idénticas y 7 eran la misma persona con
otro formato de suciedad (detectadas solo tras normalizar). Los 53 emails
inválidos y los 7 teléfonos no válidos quedan listados fila a fila al final del
reporte del script y se conservan en el CSV de salida sin tocar.

## Antes / después (ejemplos reales del run)

| messy_customers.csv | cleaned_customers.csv |
|---|---|
| `pilar gómez DE LA torre` · `PILAR.GOMEZ@OUTLOOK.COM` · `(+34) 602 578 729` | `Pilar Gómez de la Torre` · `pilar.gomez@outlook.com` · `+34 602 578 729` |
| `PEDRO CASTRO ORTEGA` · `pedro.castro.ortega@yahoo.es,pedro.castro.ortega.backup@yahoo.es` · `698-358-416` | `Pedro Castro Ortega` · `pedro.castro.ortega@yahoo.es` · `+34 698 358 416` |
| `Pilar López de la Fuente` · `96158x6578` · `Alicante` | `Pilar López de la Fuente` · `+34 961 586 578` · `Alicante` |
| `FERNANDO gil gómez` · `malaga` | `Fernando Gil Gómez` · `Málaga` |
| `Rafael Pérez Iglesias` · `rafael.perez(at)yahoo.es` · `12345` | se conserva y se reporta: email irrecuperable y teléfono incompleto |

## Archivos

- `gen_messy_customers.py` — generador del CSV sucio sintético (semilla fija).
- `messy_customers.csv` — 200 filas sucias de ejemplo.
- `clean_customers.py` — el limpiador.
- `cleaned_customers.csv` — resultado: 180 filas limpias y deduplicadas.
