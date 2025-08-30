from app.db_setup import init_db
from app import create_app
#from migrations.extensions import socketio

app = create_app()

if __name__ == "__main__":
    init_db()
    #socketio.run(app, debug=True)
    app.run(debug=True)
