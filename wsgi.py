from app import create_app

# entry point for gunicorn WSGI server. pass wsgi:app into gunicorn
app = create_app()

if __name__ == "__main__":
    app.run() 