from flask import Flask, request, jsonify, render_template
from pathlib import Path
import traceback
from werkzeug.utils import secure_filename

from user_pipeline import user_query_pipeline
from admin_pipeline import process_document
from get_directory_documents import get_documents
import json 

from feedback_store import (
    initialize_feedback_db,
    save_interaction,
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
        json_llm_response = user_query_pipeline(query.strip())

        # Convert structured LLM response into JSON string for database storage.
        answer_json = json.dumps(json_llm_response, ensure_ascii=False)

        # Store question, structured answer, and filtered citations.
        interaction_id = save_interaction(
            question=json_llm_response["query"],
            answer=answer_json,
            sources=json_llm_response["citation_list"],
        )

        # Return the complete response to the frontend.
        return jsonify({
            "success": True,
            "result": json_llm_response,
            "interaction_id": interaction_id,
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
# Feedback Rating API
# --------------------------------------------------

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(silent=True) or {}

    interaction_id = data.get("interaction_id")
    rating = data.get("rating")

    if (
        isinstance(interaction_id, bool)
        or not isinstance(interaction_id, int)
        or interaction_id <= 0
    ):
        return jsonify({
            "success": False,
            "error": "Invalid interaction ID",
        }), 400

    if isinstance(rating, bool) or rating not in (1, -1):
        return jsonify({
            "success": False,
            "error": "Invalid rating",
        }), 400

    try:
        save_feedback(interaction_id, rating)
        return jsonify({
            "success": True,
            "message": "Rating saved successfully",
        })

    except Exception:
        app.logger.exception("Unable to save rating")
        return jsonify({
            "success": False,
            "error": "Unable to save rating",
        }), 500


# --------------------------------------------------
# Feedback Comment API
# --------------------------------------------------

@app.route("/feedback/comment", methods=["POST"])
def submit_feedback_comment():
    data = request.get_json(silent=True) or {}

    interaction_id = data.get("interaction_id")
    comment = data.get("comment", "")

    if (
        isinstance(interaction_id, bool)
        or not isinstance(interaction_id, int)
        or interaction_id <= 0
    ):
        return jsonify({
            "success": False,
            "error": "Invalid interaction ID",
        }), 400

    if not isinstance(comment, str) or not comment.strip():
        return jsonify({
            "success": False,
            "error": "Please enter a comment",
        }), 400

    try:
        save_feedback(interaction_id, comment.strip())
        return jsonify({
            "success": True,
            "message": "Comment saved successfully",
        })

    except ValueError as error:
        return jsonify({
            "success": False,
            "error": str(error),
        }), 400

    except Exception:
        app.logger.exception("Unable to save feedback comment")
        return jsonify({
            "success": False,
            "error": "Unable to save comment",
        }), 500


# --------------------------------------------------
# Start Flask Server
# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
