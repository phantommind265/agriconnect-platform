from agriconnect_web.config import DB_PATH
from app.models.message_model import Message

db.create_all()
print("Messages table created successfully in Agriconnect.db")
