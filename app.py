from flask import Flask, request, jsonify, render_template
from pathlib import Path

from user_pipeline import user_query_pipeline
from admin_pipeline import process_document
from get_directory_documents import get_documents

from feedback_store import (
    initialize_feedback_db,
    save_interaction,
    save_feedback,
    save_feedback_comment
)

initialize_feedback_db()

import traceback

app = Flask(
    __name__,
    template_folder="gui"
)


# --------------------------------------------------
# Login GUI
# --------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "login.html"
    )


# --------------------------------------------------
# Admin GUI
# --------------------------------------------------

@app.route("/admin")
def admin_page():

    documents = get_documents()

    return render_template(
        "admin.html",
        documents=documents
    )


# --------------------------------------------------
# User GUI
# --------------------------------------------------

@app.route("/user")
def user_page():

    return render_template(
        "user.html"
    )


# --------------------------------------------------
# Login API
# --------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    user_id = data.get("id")
    password = data.get("password")

    if user_id == "user" and password == "user":

        return jsonify({
            "success": True,
            "role": "user"
        })

    elif user_id == "admin" and password == "admin":

        return jsonify({
            "success": True,
            "role": "admin"
        })

    else:

        return jsonify({
            "success": False,
            "message": "Invalid ID or password"
        }), 401


# --------------------------------------------------
# User Query API
# --------------------------------------------------


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
            "message": "Query cannot be empty"
        }), 400

    try:
        result = user_query_pipeline(query.strip())

        # Save the question, answer, and retrieved sources.
        interaction_id = save_interaction(
            question=result["query"],
            answer=result["answer"],
            sources=result["sources"]
        )

        return jsonify({
            "success": True,
            "result": result,
            "interaction_id": interaction_id
        })

    except Exception as e:
        app.logger.exception("Error processing user query")

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# --------------------------------------------------
# Admin Document Processing API
# --------------------------------------------------

@app.route("/admin/process", methods=["POST"])
def admin_process():

    if "document" not in request.files:

        return jsonify({
            "success": False,
            "message": "No document selected"
        }), 400


    document = request.files["document"]


    if document.filename == "":

        return jsonify({
            "success": False,
            "message": "No document selected"
        }), 400


    allowed_extensions = [
        ".pdf",
        ".docx",
        ".txt"
    ]

    extension = Path(document.filename).suffix.lower()


    if extension not in allowed_extensions:

        return jsonify({
            "success": False,
            "message": (
                "Invalid document type. "
                "Only PDF, DOCX and TXT are allowed."
            )
        }), 400


    document_path = (
        Path("data/documents")
        / document.filename
    )


    document.save(document_path)


    try:

        result = process_document(str(document_path))
             
        if result["success"] :            
           return jsonify({
            "success": True,
            "result": result
            })
           
        else :
            
            return jsonify({
                "success" : False,
                "result" : result
            })


    except Exception as e:

        print("Error processing document:")
        traceback.print_exc()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
        

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
        return jsonify({"error": "Invalid interaction ID"}), 400

    if isinstance(rating, bool) or rating not in (1, -1):
        return jsonify({"error": "Invalid rating"}), 400

    try:
        save_feedback(interaction_id, rating)
        return jsonify({
            "success": True,
            "message": "Rating saved successfully"
        })

    except Exception:
        app.logger.exception("Unable to save rating")
        return jsonify({"error": "Unable to save rating"}), 500


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
        return jsonify({"error": "Invalid interaction ID"}), 400

    if not isinstance(comment, str) or not comment.strip():
        return jsonify({"error": "Please enter a comment"}), 400

    try:
        save_feedback_comment(interaction_id, comment)

        return jsonify({
            "success": True,
            "message": "Comment saved successfully"
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception:
        app.logger.exception("Unable to save comment")
        return jsonify({"error": "Unable to save comment"}), 500


# --------------------------------------------------
# Start Flask Server
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )