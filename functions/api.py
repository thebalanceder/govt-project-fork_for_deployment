import sys
import os
import json

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(_project_root, '.env'), override=True)

from serverless_wsgi import handle as serverless_handle
from opinion_sim_system.flask_app import app


def handler(event, context):
    return serverless_handle(app, event, context)
