from flask import Flask, g
import sqlite3
import config
from config import DB_PATH
from flask_wtf.csrf import CSRFProtect
from agriplatform.utils.translator import t
from flask_cors import CORS
from agriplatform.routes.ai_routes import ai_bp, chat
from flask_login import LoginManager, current_user
import config
from config import DB_PATH
from flask_mail import Mail, Message
from agriplatform.models.models import User

csrf = CSRFProtect()

def get_unread_notifications(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Fetch unread notifications for this user or global ones (user_id IS NULL)
    cursor.execute("""
        SELECT id, message, link, created_at 
        FROM notifications 
        WHERE (user_id = ? OR user_id IS NULL) AND is_read = 0
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def count_unread_notifications(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE (user_id = ? OR user_id IS NULL) AND is_read = 0
    """, (user_id,))
    unread = cursor.fetchone()[0]
    conn.close()
    return unread


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
    from agriplatform.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    #Inject translator globally
    @app.context_processor
    def inject_translator():
        return dict(t=t)


    from agriplatform.routes.crop_routes import crop_bp
    app.register_blueprint(crop_bp)

    from agriplatform.routes.market import market_bp
    app.register_blueprint(market_bp)

    from agriplatform.routes.pests import pest_bp
    app.register_blueprint(pest_bp)

    from agriplatform.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from agriplatform.routes.ai_routes import ai_bp
    app.register_blueprint(ai_bp)

    from agriplatform.routes.weather import weather_bp
    app.register_blueprint(weather_bp)

    from agriplatform.routes.market_place import marketplace_bp
    app.register_blueprint(marketplace_bp)

    from agriplatform.routes.forum import forum_bp
    app.register_blueprint(forum_bp)

    from agriplatform.routes.farmer import farmer_bp
    app.register_blueprint(farmer_bp)

    from agriplatform.routes.message import message_bp
    app.register_blueprint(message_bp)

    from agriplatform.routes.soil import soil_bp
    app.register_blueprint(soil_bp)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    from agriplatform.routes.agrishare import agrishare_bp
    app.register_blueprint(agrishare_bp)

    from agriplatform.routes.equipment import equipment_bp
    app.register_blueprint(equipment_bp)

    from agriplatform.routes.events import events_bp
    app.register_blueprint(events_bp)

    from agriplatform.routes.notification import notifications_bp
    app.register_blueprint(notifications_bp)

    from agriplatform.routes.knowledge import knowledge_bp
    app.register_blueprint(knowledge_bp)

    from agriplatform.routes.profile import profile_bp
    app.register_blueprint(profile_bp)

    from agriplatform.routes.farmer_management import ext_bp
    app.register_blueprint(ext_bp)

    from agriplatform.routes.field import field_bp
    app.register_blueprint(field_bp)

    from agriplatform.routes.advisory import advisory_bp
    app.register_blueprint(advisory_bp)

    from agriplatform.routes.farmer_advisory import farmer_advisory_bp
    app.register_blueprint(farmer_advisory_bp)

    from agriplatform.routes.services import services_bp
    app.register_blueprint(services_bp)

    from agriplatform.routes.reports import reports_bp
    app.register_blueprint(reports_bp)

    from agriplatform.routes.data_submission import data_bp
    app.register_blueprint(data_bp)

    from agriplatform.routes.market_linkage import linkage_bp
    app.register_blueprint(linkage_bp)

    from agriplatform.routes.donation import donation_bp
    app.register_blueprint(donation_bp)

    from agriplatform.routes.transport import transport_bp
    app.register_blueprint(transport_bp)

    from agriplatform.routes.warehouse import warehouse_bp
    app.register_blueprint(warehouse_bp)

    from agriplatform.routes.extension_routes import extension_bp
    app.register_blueprint(extension_bp)

    from agriplatform.routes.data_collection import collection_bp
    app.register_blueprint(collection_bp)

    from agriplatform.routes.analytics import extension_analytics_bp
    app.register_blueprint(extension_analytics_bp)

    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            unread = count_unread_notifications(current_user.id)
            recent = get_unread_notifications(current_user.id)
            return dict(notif_unread=unread, recent_notifs=recent)
        return dict(notif_unread=0, recent_notifs=[])

    return app
