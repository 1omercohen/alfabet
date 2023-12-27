from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, default=db.func.now())
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100))
    venue = db.Column(db.String(100))
    participants = db.Column(db.Integer, default=0)

userEvents = db.Table(
    "user_events",
    db.Column("userId", db.ForeignKey(User.id), primary_key=True),
    db.Column("eventId", db.ForeignKey(Event.id), primary_key=True),
)