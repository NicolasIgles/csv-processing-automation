from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from processor import clean_text_values, process_csv_files, to_snake_case  # noqa: E402


def test_to_snake_case_normalizes_text() -> None:
    assert to_snake_case("Customer Name") == "customer_name"
    assert to_snake_case("Order-ID") == "order_id"
    assert to_snake_case("  Total Amount $") == "total_amount"


def test_clean_text_values_normalizes_common_null_markers() -> None:
    df = pd.DataFrame({"city": [" Buenos Aires ", "NULL", "none", "n/a", "NA", " "]})
    cleaned = clean_text_values(df)

    assert cleaned.loc[0, "city"] == "buenos aires"
    assert pd.isna(cleaned.loc[1, "city"])
    assert pd.isna(cleaned.loc[2, "city"])
    assert pd.isna(cleaned.loc[3, "city"])
    assert pd.isna(cleaned.loc[4, "city"])
    assert pd.isna(cleaned.loc[5, "city"])


def test_process_csv_files_creates_outputs_and_report(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    file_one = pd.DataFrame(
        {
            "Customer Name": ["Ana", "Ana", "Luis", None],
            "Amount": [100, 100, 200, None],
        }
    )
    file_two = pd.DataFrame(
        {
            "Customer Name": ["Marta"],
            "Amount": [300],
        }
    )

    file_one.to_csv(input_dir / "sales_1.csv", index=False)
    file_two.to_csv(input_dir / "sales_2.csv", index=False)

    consolidated_df, report, summary = process_csv_files(input_dir, output_dir)

    assert len(report) == 2
    assert len(consolidated_df) == 3
    assert summary.files_processed == 2
    assert summary.total_duplicates_removed == 1
    assert summary.total_empty_rows_removed == 1
    assert "customer_name" in consolidated_df.columns
    assert "source_file" in consolidated_df.columns
    assert (output_dir / "consolidated.csv").exists()
    assert (output_dir / "processing_report.csv").exists()
    assert (output_dir / "transformed" / "processed_sales_1.csv").exists()


def test_process_csv_files_raises_when_no_csv_found(tmp_path: Path) -> None:
    input_dir = tmp_path / "empty_input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        process_csv_files(input_dir, output_dir)
