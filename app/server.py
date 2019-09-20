"""
Server Module
"""
from flask import Flask, Blueprint, request, jsonify, abort

from datetime import datetime

app = Flask(__name__)

stored_events = []

def get_next_id():
    if stored_events:
        next_id = max([event.id for event in stored_events]) + 1
    else:
        next_id = 1
    return next_id

def remove_event(event):
    stored_events.remove(event)

def get_stored_event(event_id):
    event = [event for event in stored_events if event.id == event_id]
    if event:
        return event[0]
    else:
        return None

class Event:

    def __init__(self, name, description, organizer, datetime_of_event):
        self.name = name
        self.description = description
        self.organizer = organizer
        self.datetime_of_event = datetime_of_event
        self.id = get_next_id()

    def __str__(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            organizer=self.organizer,
            datetime_of_event=self.datetime_of_event
        )

events = Blueprint('events', __name__, url_prefix='/api/events')

@events.route('/', methods=['GET'])
def get_all_events():
    all_events = [event.__str__() for event in stored_events]
    return jsonify(all_events), 200

@events.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = get_stored_event(event_id)
    if event:
        response = jsonify(event.__str__()), 200
    else:
        response = jsonify('Event not found'), 404
    return response

@events.route('', methods=['POST'])
def create_event():
    data = request.get_json()
    if not (name := data.get('name', None)) or len(name) > 100:
        abort(400)
    if not (description := data.get('description', None)) \
        or len(description) > 1000:
        abort(400)
    if (organizer := data.get('organizer', None)) and len(organizer) > 100:
        abort(400)
    if not (datetime_of_event := data.get('datetime_of_event', None)) \
        or not datetime.strptime(datetime_of_event, '%Y-%m-%d %H:%M:%S'):
        abort(400)
    event = Event(
        name,
        description,
        organizer,
        datetime_of_event
        )
    stored_events.append(event)
    return jsonify(event.__str__()), 201


@events.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()
    event = get_stored_event(event_id)
    if event:
        if (name:= data.get('name', None)):
            if len(name) < 100:
                event.name = name
            else:
                abort(400)
        if (description:= data.get('description', None)):
            if len(description) < 1000:
                event.description = description
            else:
                abort(400)
        if (organizer:= data.get('organizer', None)):
            if len(organizer) < 100:
                event.organizer = organizer
            else:
                abort(400)
        if (datetime_of_event:= data.get('datetime_of_event', None)):
            if datetime.strptime(datetime_of_event, '%Y-%m-%d %H:%M:%S'):
                event.datetime_of_event = datetime_of_event
            else:
                abort(400)
        response = jsonify(event.__str__()), 200
    else:
        response = jsonify('Event not found'), 404
    return response


@events.route('/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = get_stored_event(event_id)
    if event:
        remove_event(event)
        response = jsonify('Event removed'), 200
    else:
        response = jsonify('Event not found'), 404
    return response

app.register_blueprint(events)

if __name__ == '__main__':
    app.run()
