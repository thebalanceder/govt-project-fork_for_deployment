import sys
import os
import json
import traceback
from io import BytesIO
from urllib.parse import urlencode

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(_project_root, '.env'), override=True)
load_dotenv(override=True)

from opinion_sim_system.flask_app import app


_ENCODED = frozenset({"application/x-www-form-urlencoded", "multipart/form-data"})


def handler(event, context):
    try:
        method = event.get("httpMethod", "GET")
        raw_path = event.get("path", "/")
        headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
        query = event.get("queryStringParameters") or {}
        body = event.get("body") or ""
        is_b64 = event.get("isBase64Encoded", False)

        if is_b64:
            import base64
            body = base64.b64decode(body)

        raw_path = raw_path.replace("/.netlify/functions/api", "").rstrip("/") or "/"

        if isinstance(body, str):
            body_bytes = body.encode("utf-8")
        else:
            body_bytes = body

        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": raw_path,
            "QUERY_STRING": urlencode(query, doseq=True) if query else "",
            "CONTENT_TYPE": headers.get("content-type", ""),
            "CONTENT_LENGTH": str(len(body_bytes)),
            "SERVER_NAME": headers.get("host", "localhost"),
            "SERVER_PORT": "443",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": headers.get("x-forwarded-proto", "https"),
            "wsgi.input": BytesIO(body_bytes),
            "wsgi.errors": sys.stderr,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": True,
        }

        for key, value in headers.items():
            wsgi_key = "HTTP_" + key.upper().replace("-", "_")
            if wsgi_key not in ("HTTP_CONTENT_TYPE", "HTTP_CONTENT_LENGTH"):
                environ[wsgi_key] = value

        status_text = "200 OK"
        resp_headers = []

        def start_response(status, response_headers, exc_info=None):
            nonlocal status_text
            status_text = status
            resp_headers.extend(response_headers)

        chunks = app.wsgi_app(environ, start_response)
        response_body = b"".join(chunks)

        status_code = int(status_text.split(" ", 1)[0])

        out_headers = {}
        for name, value in resp_headers:
            if name.lower() == "set-cookie":
                out_headers.setdefault("set-cookie", []).append(value)
            elif name.lower() not in out_headers:
                out_headers[name] = value

        for name in list(out_headers):
            if isinstance(out_headers[name], list):
                out_headers[name] = ", ".join(out_headers[name])

        ctype = out_headers.get("content-type", "")
        is_binary = not ctype.startswith(("text/", "application/json", "application/javascript"))

        if is_binary:
            import base64
            return {
                "statusCode": status_code,
                "headers": out_headers,
                "body": base64.b64encode(response_body).decode("ascii"),
                "isBase64Encoded": True,
            }
        else:
            return {
                "statusCode": status_code,
                "headers": out_headers,
                "body": response_body.decode("utf-8"),
            }

    except Exception:
        tb = traceback.format_exc()
        return {
            "statusCode": 500,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": "internal handler error", "traceback": tb}),
        }
