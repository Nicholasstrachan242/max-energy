from app import create_app
import platform
import sys

app = create_app()

# Entry point for server.
# python wsgi.py to run locally.
# It ultimately just calls waitress-serve but without the logging provided by running it from command line.
# [Windows && Waitress && Test Environment] is the only condition that results in a server being started.

# wsgi.py filename is standard naming convention used by various deployment tools.
# Cross-platform and test/prod logic.
# This file covers use cases for test and prod for Windows and Linux and recommends best practices.

# tuple for easy reference to ip and port for testing
test_ip_port = ('127.0.0.1', '8080')

# Windows:
def run_windows_server(app):
    try:
        print("Currently using Windows - starting Waitress server FOR TESTING ONLY...")
        from waitress import serve
        if app.config['TESTING']:
            try:
                print("Server starting..." + "\n" + 
                      f"Navigate to http://{test_ip_port[0]}:{test_ip_port[1]} to test.")
                serve(app, host=test_ip_port[0], port=test_ip_port[1])
            except Exception as e:
                print(f"Error starting server: {e}")
                sys.exit(1)
        else:
            print("If running in production, please run from command line for proper logging.\n" + 
                  "waitress-serve --host=*ip-here* --port=*port-here* wsgi:app")
            sys.exit(1)
    except ImportError:
        print("Waitress is not installed. Please run: pip install waitress")
        sys.exit(1)

# Linux:
def run_linux_server(app):
    if app.config['TESTING']:
        print("Gunicorn is not meant to be run from file. For development, please run from command line:\n" + 
              "flask run \n" +
               "Or, if development but allowing access to the rest of the network:\n"+
                "flask run --host:0.0.0.0 --port=8080" )
    else:
        print("Gunicorn is not meant to be run from file. For production, please run from command line:" + "\n" + 
              "gunicorn --bind 0.0.0.0:8000 wsgi:app --workers=4")
        sys.exit(1)

# run the server
if __name__ == "__main__":
    system = platform.system()
    if system == "Windows":
        run_windows_server(app)
    elif system == "Linux":
        run_linux_server(app)