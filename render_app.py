from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
import uuid
import Display_project as backend

ROOT = Path(__file__).resolve().parent

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 4096


@app.after_request
def prevent_caching(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    return send_from_directory(ROOT / "static", "index.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory(ROOT / "static", "style.css")


@app.get("/script.js")
def javascript():
    return send_from_directory(ROOT / "static", "script.js")


@app.get("/api/tasks")
def view_tasks():
    return jsonify(backend.tasks)


@app.post("/api/tasks")
@app.post("/api/complete")
@app.post("/api/delete")
def update_tasks():
    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return jsonify(error="Invalid request."), 400

    updated = [dict(task) for task in backend.tasks]

    if request.path == "/api/tasks":
        title = body.get("task", "")

        if (
            not isinstance(title, str)
            or not 1 <= len(title.strip()) <= 200
        ):
            return jsonify(
                error="Enter a task of 1–200 characters."
            ), 400

        updated.append({
            "id": uuid.uuid4().hex,
            "task": title.strip(),
            "Done": False
        })

    else:
        selected = next(
            (task for task in updated if task["id"] == body.get("id")),
            None
        )

        if selected is None:
            return jsonify(
                error="Task not found. Refresh the page."
            ), 404

        if request.path == "/api/complete":
            selected["Done"] = not selected["Done"]
        else:
            updated.remove(selected)

    try:
        backend.save_tasks(updated)
    except OSError:
        return jsonify(error="Could not save tasks."), 500

    return jsonify(backend.tasks)


@app.errorhandler(413)
def request_too_large(error):
    return jsonify(error="The request is too large."), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)