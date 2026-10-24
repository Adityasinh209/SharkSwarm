import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.crew import MISSING_KEY, api_key, run_evaluation
from src.serialize import to_response


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        _json_response(
            self,
            200,
            {
                "service": "SharkSwarm",
                "ready": bool(api_key()),
                "message": None if api_key() else MISSING_KEY,
            },
        )

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            data = json.loads(raw.decode("utf-8") or "{}")
            idea = str(data.get("idea", "")).strip()
            if not idea:
                _json_response(self, 400, {"error": "Enter a startup idea before running the crew."})
                return
            if not api_key():
                _json_response(self, 503, {"error": MISSING_KEY})
                return

            pitch, financials, evaluation = run_evaluation(idea)
            _json_response(self, 200, to_response(pitch, financials, evaluation))
        except Exception as exc:
            message = str(exc)
            key = api_key()
            if key:
                message = message.replace(key, "[redacted]")
            _json_response(
                self,
                500,
                {"error": message, "detail": traceback.format_exc() if os.getenv("VERCEL_ENV") == "development" else None},
            )
