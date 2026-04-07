"""Direct Flask runner — bypasses `flask run` CLI."""
import sys
sys.path.insert(0, r"D:\gov-project")

from dotenv import load_dotenv
load_dotenv(r"D:\gov-project\opinion_sim_system\.env", override=True)

from opinion_sim_system.flask_app import app
app.run(host="127.0.0.1", port=5000, debug=False)
