from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Event
from app.remainder import schedule_reminder

bp = Blueprint('routes', __name__)

@bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'email already exists'}), 400

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.email or not auth.password:
        return jsonify({'error': 'Missing email or password'}), 401

    user = User.query.filter_by(email=auth.email).first()
    if not user or not check_password_hash(user.password, auth.password):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)


@bp.route(rule="/events", methods=["GET"])
@jwt_required()
def get_events():
    query = Event.query
    sort_by = request.args.get('sort_by', 'creation_time')
    if sort_by == 'event_date':
        query = query.order_by(Event.date)
    elif sort_by == 'popularity':
        query = query.order_by(Event.participants.desc())
    elif sort_by == 'creation_time':
        query = query.order_by(Event.id)
    events = query.all()
    event_list = [{'id': event.id, 'name': event.name, 'event_date': event.event_date, 'location': event.location, 'venue': event.venue, 'participants': event.get("participants")} for event in events]
    return jsonify({'events': event_list}), 200

@bp.route(rule="/events", methods=["POST"])
@jwt_required()
def create_event():
    data = request.get_json()
    new_event = Event(name=data.get('name'), event_date=data.get('event_date'), location=data.get('location'), venue=data.get('venue'), participants=data.get("participants", 0))
    db.session.add(new_event)
    db.session.commit()
    schedule_reminder(new_event.id, new_event.event_date)
    return jsonify({'message': 'Event scheduled successfully'}), 200


@bp.route(rule="/events/<event_id>", methods=["GET"])
@jwt_required()
def get_event(event_id: str):
    event = db.get_or_404(Event, event_id)
    if event:
        event_details = {'id': event.id, 'name': event.name, 'event_date': event.event_date, 'created_date': event.created_date, 'location': event.location, 'venue': event.venue, 'participants': event.get("participants")}
        return jsonify(event_details), 200
    else:
        return jsonify({'error': 'Event not found'}), 404

@bp.route(rule="/events/<event_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_event(event_id: str):
    event = db.get_or_404(Event, event_id)
    if event:
        updated_event = request.get_json()
        event.name = updated_event.get('name', event.name)
        event.event_date = updated_event.get('event_date', event.event_date)
        event.location = updated_event.get('location', event.location)
        event.venue = updated_event.get('venue', event.venue)
        event.participants = update_event.get('participants', event.participants)
        db.session.commit()
        return jsonify({'message': 'Event updated successfully'}), 200
    else:
        return jsonify({'error': 'Event not found'}), 404



@bp.route(rule="/events/<event_id>", methods=["DELETE"])
def delete_event(event_id: str):
    event = db.get_or_404(Event, event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
    else:
        return jsonify({'error': 'Event not found'}), 404
