import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
import uvicorn
from app import app
uvicorn.run(app, host="0.0.0.0", port=8000)
