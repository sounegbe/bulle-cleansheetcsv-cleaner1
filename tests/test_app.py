import io
import unittest

import app as web_app


class TestCleanSheetWebApp(unittest.TestCase):
    def setUp(self):
        web_app.app.config["TESTING"] = True
        self.client = web_app.app.test_client()

    def upload(self, filename, content):
        return self.client.post(
            "/clean",
            data={
                "file": (
                    io.BytesIO(content.encode("utf-8")),
                    filename,
                )
            },
            content_type="multipart/form-data",
        )

    def test_homepage_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CleanSheet", response.data)
        self.assertIn(b"Choose a CSV file", response.data)

    def test_valid_csv_shows_cleaning_statistics(self):
        content = (
            "name,email,city\n"
            " Ada Lovelace ,ada@example.com,Lagos\n"
            "Grace Hopper,grace@example.com,Abuja\n"
            "Ada Lovelace,ada@example.com,Lagos\n"
        )

        response = self.upload("customers.csv", content)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Cleaning Results", response.data)
        self.assertIn(b"Duplicates removed", response.data)
        self.assertIn(b"1", response.data)

    def test_download_returns_cleaned_csv(self):
        content = (
            "name,email,city\n"
            "Ada,ada@example.com,Lagos\n"
            "Ada,ada@example.com,Lagos\n"
        )

        response = self.upload("customers.csv", content)
        self.assertEqual(response.status_code, 200)

        import re

        match = re.search(
            rb'<a class="button" href="([^"]+)">\s*Download cleaned CSV',
            response.data,
        )
        self.assertIsNotNone(match)
        download_url = match.group(1).decode("utf-8")

        with self.client.get(download_url) as download:
            self.assertEqual(download.status_code, 200)
            self.assertIn("Content-Disposition", download.headers)
            self.assertIn("attachment", download.headers["Content-Disposition"])
            self.assertEqual(
                download.data.decode("utf-8").count("Ada,ada@example.com,Lagos"),
                1,
            )

    def test_rejects_non_csv_file(self):
        response = self.upload("notes.txt", "hello")

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Only .csv files are accepted", response.data)

    def test_rejects_missing_file(self):
        response = self.client.post("/clean", data={})

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Choose a CSV file", response.data)

    def test_rejects_malformed_csv(self):
        content = "name,email,city\nAda,ada@example.com\n"

        response = self.upload("broken.csv", content)

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Malformed CSV row", response.data)

    def test_rejects_oversized_upload(self):
        large_content = "name,email,city\n" + ("A" * (5 * 1024 * 1024))

        response = self.upload("large.csv", large_content)

        self.assertEqual(response.status_code, 413)
        self.assertIn(b"maximum upload size is 5 MB", response.data)

    def test_rejects_invalid_download_id(self):
        response = self.client.get("/download/not-a-valid-id")

        self.assertEqual(response.status_code, 404)

    def test_rejects_nul_byte_in_uploaded_csv(self):
        response = self.client.post(
            "/clean",
            data={
                "file": (
                    io.BytesIO(b"name,email\nAda,ada\x00@example.com\n"),
                    "nul_byte.csv",
                )
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"NUL bytes are not allowed", response.data)


if __name__ == "__main__":
    unittest.main()
