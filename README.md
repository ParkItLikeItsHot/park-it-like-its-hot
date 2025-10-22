# park-it-like-its-hot

## Code Standards

### Python

- In code documentation should be done using RST or reStructuredText
- ALL classes, functions, and variables are type annotated
- Indentation is 4 spaces
- Class and top level functions are surrounded by 2 blank lines
- Methods are surrounded by a single blank line
- Class names should be `PascalCase`
- Function, method, and variable names are `snake_case`
- Constant and enum member names are `UPPER_SNAKE_CASE`
- file names are `kebab-case`
- Other guidelines can be found [here](https://peps.python.org/pep-0008/)

### Javascript / Typescript 

- In code documentation should be done using JSDoc 
- ALL classes, functions, and variables are type annotated
- Indentation is 4 spaces
- Class and top level functions are surrounded by 2 blank lines
- Methods are surrounded by a single blank line
- Class names should be `PascalCase`
- function, method, and variable names are `camelCase`
- Constant and enum member names are `UPPER_SNAKE_CASE`
- file names are `kebab-case`
- Other guidelines can be found [here](https://peps.python.org/pep-0008/)

## Building

### Windows

- install wsl by running `wsl`
- run `wsl --install Ubuntu`
- run `wsl` again to enter the ubuntu and setup account
- in the ubuntu shell run `sudo apt install -y python npm nodejs just`
- follow the rest of the instructions

### Important 

NOTE: any `npm`  commands are being either being run from inside `pilih-frontend` or are using `npm --prefix pilih-frontend/`
also any `python` commands are either being run after the venv has been activated or being run from their respective binary
in the `.venv` folder

### Requirements 
- [nodejs](https://nodejs.org/en) - for npm and running front end dev 
- [python](https://www.python.org/) - used for backend
- [just](https://github.com/casey/just) - one command setup and running

### Using just file
- run `just install` to install requirements

### Doing it manually

### Creating venv

- run `python -m venv .venv` to create the venv 
- then `source .venv/bin/activate` on macos and linux or `.venv\Scripts\Activate.ps1` on windows to activate
- run `pip install -r requirements.txt` to install the requirements

### Building front end

- go to `pilih-frontend` and run `npm install` to install required libraries (vite, react, and typescript) 
- run `npm run build` to generate static files into `dist` directory which will be hosted by the flask backend

## Running

### Using Just File
- run `just frontend` to start a vite dev server and the flask backend
- run `just backend`  to just start the backend flask server

### Manually
- run `npm run dev` to start the vite dev server
- run `python -m flask --app backend/backend.py --debug run` or simply `python backend/backend.py` to start the flask app

NOTE: When working on the frontend i recommend you use the vite dev server as it comes with 
some nice features including hot reloading. If you do this however, you'll need to start 
the backend separately.
