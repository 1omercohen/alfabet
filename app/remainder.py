from celery import Celery
from datetime import timedelta
from app.models import db, Event

app = Celery('reminders', broker='redis://localhost:6379/0')

class ContextTask(app.Task):
    def __call__(self, *args, **kwargs):
        with app.app.app_context():
            return self.run(*args, **kwargs)

app.Task = ContextTask

# Celery task to send reminders
@app.task
def send_reminder(event_id):
    event = Event.query.get(event_id)
    if event:
        print(f"Reminder for event '{event.name}' scheduled at {event.date}")
        # Implement your reminder mechanism here (e.g., send an email, notification, etc.)


def schedule_reminder(event_id, event_date):
    reminder_time = event_date - timedelta(minutes=30)
    send_reminder.apply_async(args=[event_id], eta=reminder_time)
