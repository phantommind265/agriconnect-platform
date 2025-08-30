import os

DB_PATH = os.path.join("app", "agriconnect.db")
PESTS_DATA_PATH = os.path.join("app", "data", "pests.json")
CROPS_DATA_PATH = os.path.join("app", "data", "crops.json")
PRICES_DATA_PATH = os.path.join("app", "data", "market_prices.json")
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max 5MB
UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'chikusehopeson@gmail.com'
MAIL_PASSWORD = 'app_password'
MAIL_DEFAULT_SENDER = ('AgriConnect Support', 'chikusehopeson@gmail.com')


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "hopeson-chikuse-the-ceo")
    #SECRET_KEY = os.environ.get("SECRET_KEY", "this-is-a-dev-secret")
    LANGUAGES = ["en", "ny"]

    """
    later work

    STATIC_FOLDER = 'app/static'
    TEMPLATES_FOLDER = 'app/templates'
    """
