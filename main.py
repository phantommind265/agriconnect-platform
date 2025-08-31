from agriplatform.db_setup import init_db
from agriplatform import create_app

app = create_app()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
