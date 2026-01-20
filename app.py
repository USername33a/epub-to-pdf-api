from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import uuid
import subprocess

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def find_ebook_convert():
    """
    Try to find ebook-convert binary in common locations.
    """
    possible_paths = [
        "ebook-convert",
        "/usr/bin/ebook-convert",
        "/usr/local/bin/ebook-convert"
    ]

    for path in possible_paths:
        try:
            result = subprocess.run(
                ["which", path],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                print("Found ebook-convert at:", result.stdout.strip())
                return result.stdout.strip()
        except:
            pass

    return None

@app.route("/")
def home():
    return jsonify({"status": "EPUB to PDF API running"})

@app.route("/convert", methods=["POST"])
def convert_epub_to_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file.filename.lower().endswith(".epub"):
        return jsonify({"error": "Only EPUB files allowed"}), 400

    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{uid}.epub")
    output_path = os.path.join(OUTPUT_FOLDER, f"{uid}.pdf")

    file.save(input_path)

    try:
        # Find ebook-convert
        ebook_convert_path = find_ebook_convert()

        if not ebook_convert_path:
            return jsonify({
                "error": "ebook-convert not found on server"
            }), 500

        print("Using ebook-convert:", ebook_convert_path)

        # Run conversion
        command = [
            ebook_convert_path,
            input_path,
            output_path
        ]

        proc = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        print("ebook-convert STDOUT:\n", proc.stdout)
        print("ebook-convert STDERR:\n", proc.stderr)
        print("Return code:", proc.returncode)

        if proc.returncode != 0:
            return jsonify({
                "error": "Conversion failed",
                "stderr": proc.stderr
            }), 500

        # Check output file really exists and is not tiny
        if not os.path.exists(output_path):
            return jsonify({"error": "PDF not created"}), 500

        if os.path.getsize(output_path) < 10 * 1024:  # less than 10 KB
            return jsonify({"error": "Generated PDF is too small / corrupt"}), 500

        return send_file(
            output_path,
            as_attachment=True,
            download_name="converted.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print("EXCEPTION:", str(e))
        return jsonify({"error": "Exception", "details": str(e)}), 500

    finally:
        # Clean input file
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
