from flask import Flask, request, jsonify, render_template
from pathlib import Path
import traceback
from werkzeug.utils import secure_filename

from user_pipeline import user_query_pipeline
from admin_pipeline import process_document
from get_directory_documents import get_documents

from feedback_store import (
    initialize_feedback_db,
    save_feedback
)

# Initialize the feedback database when the application starts.
initialize_feedback_db()

app = Flask(__name__, template_folder="gui")


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


# --------------------------------------------------
# Login GUI
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("login.html")


# --------------------------------------------------
# Admin GUI
# --------------------------------------------------

@app.route("/admin")
def admin_page():
    documents = get_documents()
    return render_template("admin.html", documents=documents)


# --------------------------------------------------
# User GUI
# --------------------------------------------------

@app.route("/user")
def user_page():
    return render_template("user.html")


# --------------------------------------------------
# Login API
# --------------------------------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    user_id = data.get("id")
    password = data.get("password")

    if user_id == "user" and password == "user":
        return jsonify({"success": True, "role": "user"})

    if user_id == "admin" and password == "admin":
        return jsonify({"success": True, "role": "admin"})

    return jsonify({
        "success": False,
        "message": "Invalid ID or password",
    }), 401


# --------------------------------------------------
# User Query API
# --------------------------------------------------

@app.route("/user/query", methods=["POST"])
def user_query():
    data = request.get_json(silent=True) or {}
    query = data.get("query")

    if not isinstance(query, str) or not query.strip():
        return jsonify({
            "success": False,
            "message": "Query cannot be empty",
        }), 400

    try:
        # user_pipeline stores the interaction and retrieved chunks.
        # app.py only forwards the pipeline output to the frontend.
        pipeline_output = user_query_pipeline(query.strip())

        return jsonify({
            "success": True,
            "interaction_id": pipeline_output["interaction_id"],
            "result": pipeline_output["result"]
        })

    except Exception:
        app.logger.exception(
            "User query processing or interaction storage failed"
        )
        return jsonify({
            "success": False,
            "message": (
                "Unable to process the query. "
                "Please check the server logs."
            ),
        }), 500


# --------------------------------------------------
# Admin Document Processing API
# --------------------------------------------------

@app.route("/admin/process", methods=["POST"])
def admin_process():
    if "document" not in request.files:
        return jsonify({
            "success": False,
            "message": "No document selected",
        }), 400

    document = request.files["document"]

    if not document.filename:
        return jsonify({
            "success": False,
            "message": "No document selected",
        }), 400

    # Validate and sanitize the uploaded filename.
    safe_filename = secure_filename(document.filename)

    if not safe_filename:
        return jsonify({
            "success": False,
            "message": "Invalid document filename",
        }), 400

    extension = Path(safe_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            "success": False,
            "message": (
                "Invalid document type. "
                "Only PDF, DOCX and TXT are allowed."
            ),
        }), 400

    document_path = DOCUMENTS_DIR / safe_filename

    try:
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

        # Check if a document with the same filename already exists
        if document_path.exists():
            return jsonify({
                "success": False,
                "message": f"Duplicate file: {safe_filename} is already uploaded.",
            }), 409

        document.save(str(document_path))

        result = process_document(document_path)

        # Validate the processing result before reporting success.
        if result is None or result is False:
            return jsonify({
                "success": False,
                "message": (
                    "Document processing failed. "
                    "No successful processing result was returned."
                ),
            }), 500

        if isinstance(result, dict):
            if result.get("success") is False:
                return jsonify({
                    "success": False,
                    "message": result.get(
                        "message",
                        "Document processing failed.",
                    ),
                    "result": result,
                }), 500

            chunks_created = result.get("chunks_created")

            # The ingestion pipeline returns status="skipped" with
            # chunks_created=0 when the document is unchanged. That is
            # successful and must not be treated as an empty extraction.
            if (
                result.get("status") == "empty"
                or (
                    chunks_created is not None
                    and chunks_created <= 0
                    and result.get("status") != "skipped"
                )
            ):
                return jsonify({
                    "success": False,
                    "message": (
                        result.get("message")
                        or "No text chunks were extracted from the document. "
                        "For scanned PDFs, verify that OCR is installed "
                        "and configured correctly."
                    ),
                    "result": result,
                }), 422

        return jsonify({
            "success": True,
            "message": (
                "Document processed successfully. "
                "OCR is used by the document-processing pipeline "
                "when required."
            ),
            "result": result,
        })

    except Exception as error:
        print(f"Error processing document {safe_filename}: {error}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": (
                "Document processing failed. Check the Flask "
                "server terminal for the detailed error."
            ),
        }), 500


# --------------------------------------------------
# Feedback API
# --------------------------------------------------

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(silent=True) or {}

    interaction_id = data.get("interaction_id")
    is_helpful = data.get("is_helpful")
    comment = data.get("comment")

    if (
        isinstance(interaction_id, bool)
        or not isinstance(interaction_id, int)
        or interaction_id <= 0
    ):
        return jsonify({
            "success": False,
            "error": "Invalid interaction ID",
        }), 400

    if not isinstance(is_helpful, bool):
        return jsonify({
            "success": False,
            "error": "is_helpful must be true or false",
        }), 400

    if comment is not None and not isinstance(comment, str):
        return jsonify({
            "success": False,
            "error": "Comment must be text",
        }), 400

    try:
        save_feedback(interaction_id, is_helpful, comment)
        return jsonify({
            "success": True,
            "message": "Feedback saved successfully",
        })

    except ValueError as error:
        return jsonify({
            "success": False,
            "error": str(error),
        }), 400

    except Exception:
        app.logger.exception("Unable to save feedback")
        return jsonify({
            "success": False,
            "error": "Unable to save feedback. Check the Flask server log.",
        }), 500


# --------------------------------------------------
# Start Flask Server
# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
