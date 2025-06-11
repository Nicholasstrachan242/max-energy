from app import create_app
import platform
import sys

app = create_app()

# Cross-platform logic to determine which server to use. Option to use Waitress for windows, Gunicorn for Linux.
def run_windows_server(app):
    try:
        from waitress import serve
        print("Running on Windows - using Waitress server")
        serve(app, host='localhost', port=8000)
    except ImportError:
        print("Waitress is not installed. Please run: pip install waitress")
        sys.exit(1)

def run_linux_server(app):
    try:
        import gunicorn
        print("Running on Linux - using Gunicorn server")
        gunicorn.run(app, host='localhost', port=8000)
    except ImportError:
        print("Gunicorn is not installed. Please run: pip install gunicorn")
        sys.exit(1)

# run the server
if __name__ == "__main__":
    system = platform.system()
    if system == "Windows":
        run_windows_server(app)
    elif system == "Linux":
        run_linux_server(app)