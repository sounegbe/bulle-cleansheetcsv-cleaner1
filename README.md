# CleanSheet — CSV Cleaner

CleanSheet is a small Python tool that cleans CSV files by trimming
unnecessary whitespace, removing duplicate rows, and reporting missing
values.

It validates the number of columns in each row and reports malformed
rows instead of silently accepting them.

## Features

- Removes leading and trailing whitespace from values.
- Removes exact duplicate rows after trimming whitespace.
- Reports the number of input rows, output rows, duplicates removed,
  and rows containing missing values.
- Keeps rows with missing values instead of deleting them.
- Rejects rows with too few or too many columns.
- Protects the input file by writing cleaned data to a separate output.
- Uses Python's standard library; no third-party packages are required.

## Requirements

- Python 3.10 or newer.

## Project structure

```text
cleansheet-csv-cleaner/
├── main.py
├── README.md
├── sample_data/
│   └── customers.csv
├── output/
└── tests/
    └── test_main.py
```

## Setup

Clone the repository and enter the project directory:

```bash
git clone YOUR_REPOSITORY_URL
cd cleansheet-csv-cleaner
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

No extra packages need to be installed.

## Run the cleaner

Use the sample CSV file:

```bash
python -c "from main import clean_csv; print(clean_csv('sample_data/customers.csv', 'output/customers_cleaned.csv'))"
```

The cleaned file is written to `output/customers_cleaned.csv`.

The report includes:

- `input_rows`: number of data rows read.
- `output_rows`: number of unique rows written.
- `duplicates_removed`: number of duplicate rows removed.
- `rows_with_missing_values`: number of rows containing at least one empty value.

If a row has the wrong number of columns, the cleaner raises a
`ValueError` identifying the row's line number.

## Run the tests

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

The tests cover whitespace trimming, duplicate removal, missing values,
malformed rows, numeric-looking values, and file protection.

## Important behavior

- The original input file is not modified.
- The input and output paths must be different.
- Numeric-looking CSV values are preserved as text; the tool does not
  perform mathematical calculations.
- Missing values are reported but are not automatically filled or removed.
- If malformed input is detected, cleaning stops with an error.

## Current status

CleanSheet is an early-stage project. The current automated test suite
passes, but additional testing and improvements are needed before it
should be relied on for important production data.
