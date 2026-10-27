import csv
import tempfile
import unittest
from pathlib import Path

from main import clean_csv


class TestCleanCSV(unittest.TestCase):
    def test_removes_duplicates_and_trims_spaces(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source = folder / "input.csv"
            output = folder / "output.csv"

            source.write_text(
                "name,email\n"
                " Ada , ada@example.com \n"
                "Ada,ada@example.com\n"
                "Grace,grace@example.com\n",
                encoding="utf-8",
            )

            report = clean_csv(source, output)

            self.assertEqual(report["input_rows"], 3)
            self.assertEqual(report["output_rows"], 2)
            self.assertEqual(report["duplicates_removed"], 1)

            with output.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(rows[0]["name"], "Ada")
            self.assertEqual(rows[0]["email"], "ada@example.com")

    def test_keeps_rows_with_missing_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source = folder / "input.csv"
            output = folder / "output.csv"

            source.write_text(
                "name,email\n"
                "Alan,\n"
                "Grace,grace@example.com\n",
                encoding="utf-8",
            )

            report = clean_csv(source, output)

            self.assertEqual(report["output_rows"], 2)
            self.assertEqual(report["rows_with_missing_values"], 1)

    def test_original_file_is_not_modified(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source = folder / "input.csv"
            output = folder / "output.csv"
            original = "name,email\n Ada , ada@example.com \n"
            source.write_text(original, encoding="utf-8")

            clean_csv(source, output)

            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_rejects_same_input_and_output_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "input.csv"
            original = "name,email\nAda,ada@example.com\n"
            source.write_text(original, encoding="utf-8")

            with self.assertRaises(ValueError):
                clean_csv(source, source)

            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_rejects_row_with_too_few_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source = folder / "input.csv"
            output = folder / "output.csv"

            source.write_text(
                "name,email,city\n"
                "Ada,ada@example.com,Lagos\n"
                "12345\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError, "line 3: expected 3 columns, got 1"
            ):
                clean_csv(source, output)

    def test_rejects_row_with_too_many_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source = folder / "input.csv"
            output = folder / "output.csv"

            source.write_text(
                "name,email\n"
                "Ada,ada@example.com,unexpected\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError, "line 2: expected 2 columns, got 3"
            ):
                clean_csv(source, output)

    def test_malformed_input_does_not_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source = folder / "input.csv"
            output = folder / "output.csv"
            original_output = "previous output\nkeep this file\n"

            source.write_text(
                "name,email\n"
                "Ada,ada@example.com,extra\n",
                encoding="utf-8",
            )
            output.write_text(original_output, encoding="utf-8")

            with self.assertRaises(ValueError):
                clean_csv(source, output)

            self.assertEqual(
                output.read_text(encoding="utf-8"),
                original_output,
            )

    def test_preserves_numeric_values_and_removes_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source = folder / "input.csv"
            output = folder / "output.csv"

            source.write_text(
                "id,amount\n"
                "12345,100.50\n"
                "12345,100.50\n"
                "34563,0\n",
                encoding="utf-8",
            )

            report = clean_csv(source, output)

            self.assertEqual(report["input_rows"], 3)
            self.assertEqual(report["output_rows"], 2)
            self.assertEqual(report["duplicates_removed"], 1)

            with output.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(rows[0]["id"], "12345")
            self.assertEqual(rows[0]["amount"], "100.50")
            self.assertEqual(rows[1]["amount"], "0")


if __name__ == "__main__":
    unittest.main()
