"""
Lightweight HTTP API Server for Griductive Web GUI.
Uses Python's standard library http.server (no external web frameworks required).
Serves:
- REST API for GameEngine, LogicAgent, SAT Solver, Uniqueness Checker.
- Static assets from the React build directory (web/dist).
"""

import sys
import os
import json
import mimetypes
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.game_engine import GameEngine
from agent.agent import LogicAgent
from agent.uniqueness import check_uniqueness_dpll
from logic.kb import build_kb


class GriductiveServerState:
    """Singleton managing active puzzle session for the web client."""

    def __init__(self):
        self.puzzles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "puzzles"))
        self.engine = GameEngine()
        self.agent: Optional[LogicAgent] = None
        self.current_puzzle_file: str = "puzzle_3x3_1.json"
        self.load_puzzle(self.current_puzzle_file)

    def load_puzzle(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(self.puzzles_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Puzzle file not found: {filename}")
        self.current_puzzle_file = filename
        self.engine.load_from_json(path)
        self.agent = LogicAgent(self.engine.var_map, self.engine.n)
        return self.get_state_payload()

    def restart(self) -> Dict[str, Any]:
        self.engine.restart()
        self.agent = LogicAgent(self.engine.var_map, self.engine.n)
        return self.get_state_payload()

    def get_state_payload(self) -> Dict[str, Any]:
        public = self.engine.get_public_state()
        kb = build_kb(
            public["revealed_clues"],
            public["proved_verdicts"],
            self.engine.var_map,
            self.engine.n
        )
        cards_payload = {}
        for coord, c_info in public["cards"].items():
            clue_obj = c_info["clue"]
            cards_payload[coord] = {
                "coord": c_info["coord"],
                "name": c_info["name"],
                "profession": c_info["profession"],
                "is_revealed": c_info["is_revealed"],
                "status": c_info["status"],
                "clue": clue_obj.to_dict() if clue_obj else None
            }

        return {
            "current_puzzle": self.current_puzzle_file,
            "size": self.engine.n,
            "is_won": self.engine.is_game_won(),
            "proved_count": len(public["proved_verdicts"]),
            "total_cells": len(self.engine.cells),
            "stats": {
                "num_primary_vars": self.engine.var_map.num_primary,
                "num_aux_vars": self.engine.var_map.num_aux,
                "num_clauses": len(kb.clauses),
            },
            "cards": cards_payload,
            "cells": public["cells"]
        }


SERVER_STATE = GriductiveServerState()
DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "dist"))


class GriductiveRequestHandler(SimpleHTTPRequestHandler):
    """Handles API requests and static file serving for React frontend."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/puzzles":
            # Return list of puzzle files
            p_files = sorted(os.listdir(SERVER_STATE.puzzles_dir))
            puzzles = []
            for pf in p_files:
                if pf.endswith(".json"):
                    full_p = os.path.join(SERVER_STATE.puzzles_dir, pf)
                    try:
                        with open(full_p, "r", encoding="utf-8") as f:
                            pdata = json.load(f)
                        puzzles.append({
                            "filename": pf,
                            "name": pdata.get("name", pf),
                            "size": pdata.get("size", 3)
                        })
                    except Exception:
                        pass
            self._send_json({"puzzles": puzzles})
            return

        elif path == "/api/state":
            query = urllib.parse.parse_qs(parsed.query)
            if "file" in query and query["file"][0]:
                target_file = query["file"][0]
                if target_file != SERVER_STATE.current_puzzle_file:
                    SERVER_STATE.load_puzzle(target_file)
            self._send_json(SERVER_STATE.get_state_payload())
            return

        # Fallback to static files
        if os.path.exists(DIST_DIR):
            file_path = os.path.join(DIST_DIR, path.lstrip("/"))
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return super().do_GET()
            # SPA Fallback to index.html
            index_path = os.path.join(DIST_DIR, "index.html")
            if os.path.exists(index_path):
                self.path = "/index.html"
                return super().do_GET()

        self.send_error(404, "Frontend build not found. Run npm run build in web/ directory.")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            body = {}

        if path == "/api/verdict":
            coord = body.get("coord", "").upper()
            status = body.get("status", "").upper()
            code, msg, clue = SERVER_STATE.engine.submit_verdict(coord, status)
            payload = {
                "code": code,
                "message": msg,
                "revealed_clue": clue.to_dict() if clue else None,
                "state": SERVER_STATE.get_state_payload()
            }
            self._send_json(payload)
            return

        elif path == "/api/hint":
            public_state = SERVER_STATE.engine.get_public_state()
            unresolved = [c for c in SERVER_STATE.engine.cells if c not in public_state["proved_verdicts"]]
            hint_info = SERVER_STATE.agent.get_hint(
                unresolved,
                public_state["revealed_clues"],
                public_state["proved_verdicts"]
            )
            self._send_json({"hint": hint_info})
            return

        elif path == "/api/step":
            step_record = SERVER_STATE.agent.step_deduce(SERVER_STATE.engine)
            self._send_json({
                "step": step_record.to_dict() if step_record else None,
                "state": SERVER_STATE.get_state_payload()
            })
            return

        elif path == "/api/solve_all":
            trace = SERVER_STATE.agent.solve_all(SERVER_STATE.engine)
            self._send_json({
                "trace": trace.to_dict(),
                "state": SERVER_STATE.get_state_payload()
            })
            return

        elif path == "/api/restart":
            SERVER_STATE.restart()
            self._send_json(SERVER_STATE.get_state_payload())
            return

        elif path == "/api/check_uniqueness":
            all_clues = SERVER_STATE.engine.get_all_clues()
            is_u, msg, models = check_uniqueness_dpll(all_clues, SERVER_STATE.engine.var_map, SERVER_STATE.engine.n)
            self._send_json({
                "is_unique": is_u,
                "message": msg,
                "model_count": len(models)
            })
            return

        elif path == "/api/load":
            fname = body.get("filename")
            if fname:
                SERVER_STATE.load_puzzle(fname)
            self._send_json(SERVER_STATE.get_state_payload())
            return

        self.send_error(404, "Endpoint not found")


def start_server(port: int = 8000, open_browser: bool = True):
    """Starts the HTTP server and optionally launches browser."""
    import webbrowser
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, GriductiveRequestHandler)
    url = f"http://localhost:{port}"
    print(f"[*] Griductive Web Server started at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping server...")
        httpd.server_close()


if __name__ == "__main__":
    start_server(port=8000, open_browser=True)
