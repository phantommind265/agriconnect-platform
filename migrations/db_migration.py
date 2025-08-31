from agriconnect_web.config import DB_PATH
from agriplatform.models.message_model import Message

DB_PATH.create_all()
print("Messages table created successfully in Agriconnect.db")
