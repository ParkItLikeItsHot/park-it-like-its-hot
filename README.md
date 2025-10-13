# park-it-like-its-hot

## Documentation 
    
- All code should be properly documented using respective standard
- Python code uses RST or reStructuredText
- typescript/javascript uses JSDoc (similar to javadoc)

## Building

I highly recommend you install just and use the just file however if you
want to do it manually skip the "Using Just File" section and start at "Creating venv"

NOTE: any `npm` are being either being run from inside `pilih-frontend` or are using `npm --prefix pilih-frontend/`
NOTE: also any `python` commands are either being run after the venv has been activated or being run from their respective binary
in the `.venv` folder

### Requirements 
- [nodejs](https://nodejs.org/en) - for npm and running front end dev 
- [python](https://www.python.org/) - used for backend
- (optional) [just](https://github.com/casey/just) - one command setup and running

### Using just file
- run `just install` to install requirements

### Creating venv

- run `python -m venv .venv` to create the venv 
- then `source .venv/bin/activate` on macos or linux or `.venv\Scripts\Activate.ps1` on windows to activate
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
- run `python -m flask --app backend/backend.py --debug run` to start the flask app

NOTE: When working on the frontend i recommend you use the vite dev server as it comes with 
some nice features including hot reloading. If you do this however, you'll need to start 
the backend separately.
