from __future__ import annotations

import argparse
from pathlib import Path
import sys

from logger_config import configure_logging
from processor import process_csv_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Procesa, transforma y consolida archivos CSV."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Carpeta que contiene los archivos CSV de entrada.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Carpeta donde se guardarán los archivos procesados.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding usado para leer los archivos CSV. Por defecto: utf-8.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    log_path = configure_logging(args.output)

    try:
        consolidated_df, report, summary = process_csv_files(
            args.input,
            args.output,
            encoding=args.encoding,
        )
    except Exception as exc:
        print(f"Error durante el procesamiento: {exc}")
        print(f"Revisá el log en: {log_path}")
        sys.exit(1)

    print("Proceso finalizado correctamente.")
    print(f"Archivos procesados: {summary.files_processed}")
    print(f"Filas originales totales: {summary.total_original_rows}")
    print(f"Filas consolidadas: {len(consolidated_df)}")
    print(f"Duplicados removidos: {summary.total_duplicates_removed}")
    print(f"Filas vacías removidas: {summary.total_empty_rows_removed}")
    print(f"Reporte: {args.output / 'processing_report.csv'}")
    print(f"Log: {log_path}")

    for item in report:
        print(
            f"- {item.file_name}: {item.original_rows} filas originales | "
            f"{item.final_rows} finales | {item.duplicates_removed} duplicados removidos | "
            f"{item.empty_rows_removed} filas vacías removidas"
        )


if __name__ == "__main__":
    main()
