from flask import Flask
import sqlite3
from config import DB_PATH
from flask_wtf.csrf import CSRFProtect
from app.utils.translator import t
from flask_cors import CORS
from app.routes.ai_routes import ai_bp, chat
from flask_login import LoginManager
import config
from flask_mail import Mail, Message
from app.models.models import User

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    
    mail = Mail(app)

    #setup flask-login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"  # Redirect to login if not authenticated
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(
                    id=row["id"],
                    username=row["username"],
                    password_hash=row["password"],
                    role=row["role"],
                    language=row["language"],
                    profile_pic=row["profile_pic"] if row["profile_pic"] else "default.png"
            )
        return None
        #return User.get(user_id)

    app.secret_key = app.config["SECRET_KEY"]

    csrf.init_app(app)
    CORS(app)

    csrf.exempt(chat)
    
    #Register routes
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    #Inject translator globally
    @app.context_processor
    def inject_translator():
        return dict(t=t)

    from app.routes.crop_routes import crop_bp
    app.register_blueprint(crop_bp)

    from app.routes.market import market_bp
    app.register_blueprint(market_bp)

    from app.routes.pests import pest_bp
    app.register_blueprint(pest_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.ai_routes import ai_bp
    app.register_blueprint(ai_bp)

    from app.routes.weather import weather_bp
    app.register_blueprint(weather_bp)

    from app.routes.market_place import marketplace_bp
    app.register_blueprint(marketplace_bp)

    from app.routes.forum import forum_bp
    app.register_blueprint(forum_bp)

    from app.routes.farmer import farmer_bp
    app.register_blueprint(farmer_bp)

    from app.routes.message import message_bp
    app.register_blueprint(message_bp)

    from app.routes.soil import soil_bp
    app.register_blueprint(soil_bp)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    from app.routes.agrishare import agrishare_bp
    app.register_blueprint(agrishare_bp)

    from app.routes.equipment import equipment_bp
    app.register_blueprint(equipment_bp)

    from app.routes.events import events_bp
    app.register_blueprint(events_bp)

    from app.routes.notifications import notifications_bp
    app.register_blueprint(notifications_bp)

    from app.routes.knowledge import knowledge_bp
    app.register_blueprint(knowledge_bp)

    from app.routes.profile import profile_bp
    app.register_blueprint(profile_bp)

    from app.routes.farmer_management import ext_bp
    app.register_blueprint(ext_bp)

    from app.routes.field import field_bp
    app.register_blueprint(field_bp)

    return app
