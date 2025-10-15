frontend_dir := justfile_directory() / "/pilih-frontend"
backend_file := justfile_directory() / "/backend/backend.py"

python_exe := if os_family() == "windows" { 
  ".venv\\Scripts\\python.exe"
} else {
  ".venv/bin/python"
}

default: install frontend

[parallel]
frontend: run-dev backend

install: setup-python setup-npm

run-dev:
  npm --prefix {{ frontend_dir }} run dev

backend: build-frontend
  {{ python_exe }} -m flask --app {{backend_file}} --debug run

build-frontend:
  npm --prefix {{ frontend_dir }} run build

setup-python:
  python -m venv .venv
  {{ python_exe }} -m pip install -r requirements.txt

setup-npm:
  npm --prefix {{ frontend_dir }} install
