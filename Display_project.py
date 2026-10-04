import json
import os
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "tasks.json"


def load_tasks():
    if not DATA.exists():
        return []

    items = json.loads(DATA.read_text(encoding="utf-8"))

    if not isinstance(items, list) or any(
        not isinstance(task, dict)
        or not isinstance(task.get("id"), str)
        or not isinstance(task.get("task"), str)
        or not isinstance(task.get("Done"), bool)
        for task in items
    ):
        raise ValueError("tasks.json contains invalid task data.")

    return items


tasks = load_tasks()


def save_tasks(updated):
    temporary_file = DATA.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(updated, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    os.replace(temporary_file, DATA)
    tasks[:] = updated


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type="application/json"):
        if content_type == "application/json":
            data = json.dumps(body).encode("utf-8")
        else:
            data = body

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/tasks":
            self.respond(200, tasks)
            return

        files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/style.css": ("style.css", "text/css; charset=utf-8"),
            "/script.js": (
                "script.js",
                "text/javascript; charset=utf-8",
            ),
        }

        if self.path not in files:
            self.respond(404, {"error": "Not found"})
            return

        filename, content_type = files[self.path]
        file_path = ROOT / "static" / filename

        if not file_path.is_file():
            self.respond(
                404,
                {"error": f"Missing file: static/{filename}"},
            )
            return

        self.respond(200, file_path.read_bytes(), content_type)

    def do_POST(self):
        content_type = self.headers.get("Content-Type", "")
        if content_type.split(";")[0].strip() != "application/json":
            self.respond(415, {"error": "JSON required"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))

            if not 0 < length <= 4096:
                self.respond(400, {"error": "Invalid request size"})
                return

            body = json.loads(self.rfile.read(length))

            if not isinstance(body, dict):
                self.respond(400, {"error": "Invalid request"})
                return

            updated = [dict(task) for task in tasks]

            if self.path == "/api/tasks":
                title = body.get("task", "")

                if (
                    not isinstance(title, str)
                    or not 1 <= len(title.strip()) <= 200
                ):
                    self.respond(
                        400,
                        {"error": "Enter a task of 1–200 characters."},
                    )
                    return

                updated.append(
                    {
                        "id": uuid.uuid4().hex,
                        "task": title.strip(),
                        "Done": False,
                    }
                )

            elif self.path in ("/api/complete", "/api/delete"):
                selected_task = next(
                    (
                        task
                        for task in updated
                        if task["id"] == body.get("id")
                    ),
                    None,
                )

                if selected_task is None:
                    self.respond(
                        404,
                        {"error": "Task not found. Refresh the page."},
                    )
                    return

                if self.path == "/api/complete":
                    selected_task["Done"] = not selected_task["Done"]
                else:
                    updated.remove(selected_task)

            else:
                self.respond(404, {"error": "Not found"})
                return

            save_tasks(updated)
            self.respond(200, tasks)

        except (ValueError, TypeError):
            self.respond(400, {"error": "Invalid request"})

        except OSError:
            self.respond(
                500,
                {"error": "Could not save tasks. Check folder permissions."},
            )

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    required_files = ["index.html", "style.css", "script.js"]

    missing_files = [
        filename
        for filename in required_files
        if not (ROOT / "static" / filename).is_file()
    ]

    if missing_files:
        print("Missing files in the static folder:")
        for filename in missing_files:
            print(f"  - {filename}")
        print("Extract the complete ZIP and keep its folders together.")

    else:
        server = HTTPServer(("127.0.0.1", 0), Handler)
        url = f"http://127.0.0.1:{server.server_port}"

        print(f"Your To-Do List is running at: {url}", flush=True)
        print("Keep this terminal open while using the app.")
        print("Press Ctrl+C to stop.")

        try:
            webbrowser.open(url, new=1)
        except webbrowser.Error:
            print("Open the address above in your browser.")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nGoodbye! Your tasks have been saved.")
        finally:
            server.server_close()