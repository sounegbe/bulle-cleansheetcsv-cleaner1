import csv
from pathlib import Path


def clean_csv(input_file, output_file):
    """Clean whitespace and duplicate rows in a CSV file."""
    input_path = Path(input_file).resolve()
    output_path = Path(output_file).resolve()

    if input_path == output_path:
        raise ValueError("Input and output files must be different.")

    with input_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)

        try:
            original_headers = next(reader)
        except StopIteration:
            raise ValueError("The CSV file must contain a header row.")

        if not original_headers:
            raise ValueError("The CSV file must contain a header row.")

        fieldnames = [name.strip() for name in original_headers]

        if any(not name for name in fieldnames):
            raise ValueError("Column names cannot be empty.")

        if len(set(fieldnames)) != len(fieldnames):
            raise ValueError(
                "Column names must be unique after trimming spaces."
            )

        cleaned_rows = []
        seen_rows = set()
        duplicate_count = 0
        missing_value_count = 0
        input_row_count = 0

        for line_number, row in enumerate(reader, start=2):
            input_row_count += 1

            if len(row) != len(fieldnames):
                raise ValueError(
                    f"Malformed CSV row at line {line_number}: "
                    f"expected {len(fieldnames)} columns, got {len(row)}."
                )

            cleaned_values = [value.strip() for value in row]

            if any(value == "" for value in cleaned_values):
                missing_value_count += 1

            row_key = tuple(cleaned_values)

            if row_key in seen_rows:
                duplicate_count += 1
                continue

            seen_rows.add(row_key)
            cleaned_rows.append(
                dict(zip(fieldnames, cleaned_values))
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    return {
        "input_rows": input_row_count,
        "output_rows": len(cleaned_rows),
        "duplicates_removed": duplicate_count,
        "rows_with_missing_values": missing_value_count,
    }
