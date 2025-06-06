"""The main file of the robot which will install all requirements in
a virtual environment and then start the actual process, using uv.
"""

import subprocess
import os
import sys

script_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_directory)

venv_name = ".venv"

# 1) Ensure 'uv' is installed into this same interpreter
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "uv"], check=True)

# 2) Create (or update) the virtual environment under ".venv" via uv
subprocess.run([sys.executable, "-m", "uv", "venv", venv_name], check=True)

# Path to the venv's python executable
venv_python = os.path.join(venv_name, "Scripts", "python")

# 3) Bootstrap pip inside the new venv
subprocess.run([venv_python, "-m", "ensurepip", "--upgrade"], check=True)

# 4) Upgrade pip itself in the venv
subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)

# 5) Install 'uv' into the new venv so that subsequent uv commands run inside it
subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "uv"], check=True)

# 6) Use the venv’s uv to install our package into that venv,
#    forcing copy mode to avoid hardlink errors under OneDrive.
subprocess.run(
    [venv_python, "-m", "uv", "pip", "install", ".", "--link-mode=copy"],
    check=True
)

# 7) Finally, run Robot Framework inside the newly created (or updated) venv
command_args = [venv_python, "-m", "robot_framework"] + sys.argv[1:]
subprocess.run(command_args, check=True)
