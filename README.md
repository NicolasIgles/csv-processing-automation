# CSV Processing Automation

Proyecto en Python para leer, transformar y consolidar múltiples archivos CSV. El objetivo es automatizar tareas repetitivas de procesamiento de datos, reducir trabajo manual y dejar trazabilidad del flujo.

## Qué resuelve

Muchos procesos operativos trabajan con varios CSV que llegan con nombres de columnas inconsistentes, valores vacíos mal representados y filas duplicadas. Este proyecto automatiza:

- lectura masiva de archivos CSV desde una carpeta
- normalización de columnas a `snake_case`
- limpieza básica de valores de texto
- eliminación de filas completamente vacías
- eliminación de duplicados exactos
- consolidación en un único archivo final
- generación de un reporte por archivo
- logging de la ejecución

## Estructura del proyecto

```text
csv-processing-automation/
├── .gitignore
├── README.md
├── requirements.txt
├── sample_input/
│   ├── customers_a.csv
│   └── customers_b.csv
├── src/
│   ├── logger_config.py
│   ├── main.py
│   └── processor.py
└── tests/
    └── test_processor.py
```

## Requisitos

- Python 3.11 o superior

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

```bash
python src/main.py --input sample_input --output output
```

También podés indicar encoding si lo necesitás:

```bash
python src/main.py --input sample_input --output output --encoding utf-8
```

## Salidas esperadas

Después de ejecutar el proyecto se generan estos archivos dentro de `output/`:

- `consolidated.csv`: consolidado final con todos los registros procesados
- `processing_report.csv`: reporte por archivo con filas originales, finales y duplicados removidos
- `processing.log`: log de ejecución
- `transformed/`: un CSV procesado por cada archivo de entrada

## Ejemplo de flujo

1. El script detecta todos los `.csv` en la carpeta de entrada.
2. Lee cada archivo.
3. Normaliza los nombres de columnas.
4. Limpia valores vacíos como `""`, `null`, `none`, `nan`, `n/a` y `na`.
5. Elimina filas completamente vacías.
6. Elimina duplicados exactos.
7. Agrega trazabilidad con `source_file` y `processed_at`.
8. Guarda el archivo procesado individual.
9. Une todos los archivos en un consolidado final.
10. Genera reporte y log.

## Ejecutar tests

```bash
pytest
```

## Mejoras posibles

- mapeo de columnas equivalentes entre archivos
- validación de esquemas obligatorios
- conversión automática de tipos
- CLI empaquetada con `argparse` o `typer`
- configuración por archivo `.yaml` o `.json`
- reporte de calidad de datos más detallado
