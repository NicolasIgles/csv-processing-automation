from __future__ import annotations

from dataclasses import asdict, dataclass
import logging
from pathlib import Path
import re

import pandas as pd


logger = logging.getLogger(__name__)


@dataclass
class FileProcessingResult:
    file_name: str
    original_rows: int
    final_rows: int
    duplicates_removed: int
    empty_rows_removed: int
    columns: list[str]
    output_path: str


@dataclass
class ProcessingSummary:
    files_processed: int
    total_original_rows: int
    total_final_rows: int
    total_duplicates_removed: int
    total_empty_rows_removed: int


def to_snake_case(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {column: to_snake_case(str(column)) for column in df.columns}
    return df.rename(columns=renamed)


def clean_text_values(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    object_columns = result.select_dtypes(include=["object", "string"]).columns
    null_markers = {"": pd.NA, "null": pd.NA, "none": pd.NA, "nan": pd.NA, "n/a": pd.NA, "na": pd.NA}

    for column in object_columns:
        result[column] = result[column].astype("string").str.strip().str.lower().replace(null_markers)

    return result


def drop_fully_empty_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    filtered = df.dropna(how="all").copy()
    removed = len(df) - len(filtered)
    return filtered, removed


def process_dataframe(
    df: pd.DataFrame,
    source_file: str,
) -> tuple[pd.DataFrame, int, int]:
    result = normalize_columns(df)
    result = clean_text_values(result)
    result, empty_rows_removed = drop_fully_empty_rows(result)

    original_rows_after_cleaning = len(result)
    result = result.drop_duplicates().copy()
    duplicates_removed = original_rows_after_cleaning - len(result)

    result["source_file"] = source_file
    result["processed_at"] = pd.Timestamp.utcnow().isoformat()

    return result, duplicates_removed, empty_rows_removed


def ensure_directories(*directories: Path) -> None:
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def validate_input_directory(input_dir: Path) -> None:
    if not input_dir.exists():
        raise FileNotFoundError(f"La carpeta de entrada no existe: {input_dir.resolve()}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"La ruta de entrada no es una carpeta: {input_dir.resolve()}")


def list_csv_files(input_dir: Path) -> list[Path]:
    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No se encontraron archivos CSV en: {input_dir.resolve()}")
    return csv_files


def read_csv_file(file_path: Path, encoding: str = "utf-8") -> pd.DataFrame:
    logger.info("Leyendo archivo: %s", file_path.name)
    return pd.read_csv(file_path, encoding=encoding)


def build_summary(report: list[FileProcessingResult]) -> ProcessingSummary:
    return ProcessingSummary(
        files_processed=len(report),
        total_original_rows=sum(item.original_rows for item in report),
        total_final_rows=sum(item.final_rows for item in report),
        total_duplicates_removed=sum(item.duplicates_removed for item in report),
        total_empty_rows_removed=sum(item.empty_rows_removed for item in report),
    )


def save_processing_report(report: list[FileProcessingResult], output_path: Path) -> None:
    report_df = pd.DataFrame([asdict(item) for item in report])
    report_df.to_csv(output_path, index=False)


def process_csv_files(
    input_dir: Path,
    output_dir: Path,
    transformed_dir_name: str = "transformed",
    consolidated_file_name: str = "consolidated.csv",
    report_file_name: str = "processing_report.csv",
    encoding: str = "utf-8",
) -> tuple[pd.DataFrame, list[FileProcessingResult], ProcessingSummary]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    transformed_dir = output_dir / transformed_dir_name

    validate_input_directory(input_dir)
    ensure_directories(output_dir, transformed_dir)

    csv_files = list_csv_files(input_dir)
    logger.info("Inicio de procesamiento. Archivos detectados: %s", len(csv_files))

    processed_frames: list[pd.DataFrame] = []
    report: list[FileProcessingResult] = []

    for file_path in csv_files:
        raw_df = read_csv_file(file_path, encoding=encoding)
        processed_df, duplicates_removed, empty_rows_removed = process_dataframe(raw_df, file_path.name)

        transformed_output = transformed_dir / f"processed_{file_path.name}"
        processed_df.to_csv(transformed_output, index=False)

        processed_frames.append(processed_df)
        file_result = FileProcessingResult(
            file_name=file_path.name,
            original_rows=len(raw_df),
            final_rows=len(processed_df),
            duplicates_removed=duplicates_removed,
            empty_rows_removed=empty_rows_removed,
            columns=list(processed_df.columns),
            output_path=str(transformed_output),
        )
        report.append(file_result)

        logger.info(
            "Archivo procesado: %s | filas originales=%s | filas finales=%s | duplicados removidos=%s | filas vacías removidas=%s",
            file_result.file_name,
            file_result.original_rows,
            file_result.final_rows,
            file_result.duplicates_removed,
            file_result.empty_rows_removed,
        )

    consolidated_df = pd.concat(processed_frames, ignore_index=True, sort=False)
    consolidated_output = output_dir / consolidated_file_name
    consolidated_df.to_csv(consolidated_output, index=False)
    logger.info("Consolidado guardado en: %s", consolidated_output)

    report_output = output_dir / report_file_name
    save_processing_report(report, report_output)
    logger.info("Reporte guardado en: %s", report_output)

    summary = build_summary(report)
    return consolidated_df, report, summary
