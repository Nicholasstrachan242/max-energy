from app import create_app
import platform
import sys

app = create_app()

# Entry point for server.
# Cross-platform logic to determine which server to use. 
# Option to use Waitress for windows, Gunicorn for Linux.

# to run windows: waitress-serve --host=127.0.0.1 --port=8000 wsgi:app
def run_windows_server(app):
    try:
        from waitress import serve
        print("Running on Windows - using Waitress server")
        serve(app, host='127.0.0.1', port=8080)
    except ImportError:
        print("Waitress is not installed. Please run: pip install waitress")
        sys.exit(1)

# to run linux: gunicorn wsgi:app
def run_linux_server(app):
    print("Gunicorn is not meant to be run from this file. Please run from command line:" + "\n" + 
          "gunicorn --bind *ip*:*port* wsgi:app" + "OR use flask run for development")

# run the server
if __name__ == "__main__":
    system = platform.system()
    if system == "Windows":
        run_windows_server(app)
    elif system == "Linux":
        run_linux_server(app)