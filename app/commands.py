from sqlalchemy import text

def register_commands(app):
    @app.cli.command('test-connection')
    def test_connection():
        try:
            from app import db  # Import existing db instance inside the function to avoid circular import
            with app.app_context():
                query = text("SELECT 1 FROM testing_1")
                db.session.execute(query)
                print("Database connection successful")
        except Exception as e:
            print(f"Error: {e}")

