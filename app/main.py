import os
import sys
import subprocess

# Secure the root path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(__file__), "ui", "streamlit_app.py")
    
    # Inject ROOT_DIR into PYTHONPATH for the Streamlit subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = root_path + os.pathsep + env.get("PYTHONPATH", "")
    
    # Run streamlit via sys.executable to ensure it uses your virtual environment correctly
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], env=env)
