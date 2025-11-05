root_dir := justfile_directory()
frontend_dir := root_dir / "/pilih-frontend"
backend_file := root_dir / "/backend/backend.py"
python_exe :=  root_dir / "/.venv/bin/python"
docker_dir := root_dir / "/dockerfiles"
frontend_docker_image_name := "pilih-frontend"
backend_docker_image_name := "pilih-backend"

default: install frontend-dev


build-dockerfiles: build-frontend-dockerfile build-backend-dockerfile

build-frontend-dockerfile:
  npm --prefix {{ frontend_dir }} run build
  cp {{ frontend_dir / "dist" }} {{ docker_dir / "/pilih-frontend" }}
  docker build -t {{ frontend_docker_image_name }} {{ docker_dir / "pilih-frontend" }}
  
build-backend-dockerfile:
  cp {{ backend_file }} {{ docker_dir / "/pilih-backend" }}
  docker build -t {{ backend_docker_image_name }} {{ docker_dir / "pilih-backend" }}


[parallel]
run-dev: frontend-dev backend-dev

install: setup-python setup-npm

frontend-dev:
  npm --prefix {{ frontend_dir }} run dev

backend-dev: build-frontend
  {{ python_exe }} -m flask --app {{backend_file}} --debug run

build-frontend:
  npm --prefix {{ frontend_dir }} run build

setup-python:
  python -m venv .venv
  {{ python_exe }} -m pip install -r requirements.txt

setup-npm:
  npm --prefix {{ frontend_dir }} install
