import tempfile
import time
import uuid
from pathlib import Path

from flask import Flask, abort, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from main import clean_csv


app = Flask(__name__)

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
OUTPUT_LIFETIME_SECONDS = 60 * 60

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

OUTPUT_DIR = Path(tempfile.gettempdir()) / "cleansheet-csv-cleaner-outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def remove_expired_outputs():
    """Delete generated downloads older than one hour."""
    cutoff = time.time() - OUTPUT_LIFETIME_SECONDS

    for path in OUTPUT_DIR.glob("*.csv"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except FileNotFoundError:
            pass


@app.get("/")
def index():
    remove_expired_outputs()
    return render_template("index.html")


@app.post("/clean")
def clean_upload():
    remove_expired_outputs()

    uploaded_file = request.files.get("file")

    if uploaded_file is None or not uploaded_file.filename:
        return render_template(
            "index.html",
            error="Choose a CSV file before uploading.",
        ), 400

    if not uploaded_file.filename.lower().endswith(".csv"):
        return render_template(
            "index.html",
            error="Only .csv files are accepted.",
        ), 400

    file_id = uuid.uuid4().hex
    output_path = OUTPUT_DIR / f"{file_id}.csv"

    try:
        with tempfile.TemporaryDirectory(prefix="cleansheet-upload-") as temp_dir:
            input_path = Path(temp_dir) / "upload.csv"
            uploaded_file.save(input_path)

            stats = clean_csv(input_path, output_path)

    except ValueError as error:
        output_path.unlink(missing_ok=True)
        return render_template("index.html", error=str(error)), 400
    except Exception:
        output_path.unlink(missing_ok=True)
        app.logger.exception("CSV cleaning failed")
        return render_template(
            "index.html",
            error="We could not process this file. Check the CSV and try again.",
        ), 500

    return render_template(
        "result.html",
        stats=stats,
        file_id=file_id,
    )


@app.get("/download/<file_id>")
def download_cleaned_file(file_id):
    try:
        parsed_id = uuid.UUID(hex=file_id)
    except (ValueError, AttributeError):
        abort(404)

    if parsed_id.hex != file_id:
        abort(404)

    output_path = OUTPUT_DIR / f"{file_id}.csv"

    if not output_path.is_file():
        abort(404)

    return send_file(
        output_path,
        as_attachment=True,
        download_name="customers_cleaned.csv",
        mimetype="text/csv",
    )


@app.errorhandler(RequestEntityTooLarge)
def handle_large_upload(_error):
    return render_template(
        "index.html",
        error="This file is too large. The maximum upload size is 5 MB.",
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
