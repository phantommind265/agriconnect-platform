from datetime import datetime
from config import DB_PATH

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_keys=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    attachment = db.Column(db.String(255)) # for file/image name/path
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[sender_id], backref='received_messages')
