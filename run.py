#!/usr/bin/env python3

import os
import subprocess

def build_frontend():
    os.chdir('./pilih-frontend/')
    res = subprocess.run(['npm', 'run', 'build'])
    os.chdir('..')

def run_backend():
    subprocess.run(['python3', './backend/backend.py'])

if __name__ == "__main__":
    build_frontend()
    run_backend()
