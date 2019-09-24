"""
Server Module
"""
from flask import Flask, Blueprint, request, jsonify, abort
from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length

from datetime import datetime
from dateutil.relativedelta import relativedelta

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


class BaseSchema(Schema):
    @validates("datetime_of_event")
    def validate_date(self, date):
        if date > datetime.now() + relativedelta(years=1):
            raise ValidationError(
                "The event can not be organized more than one year in advance."
                )
        if date < datetime.now():
            raise ValidationError(
                "You can not organize an event in a passed day"
            )

    class Meta:
        dateformat = '%Y-%m-%d %H:%M:%S'


class CreateEventSchema(BaseSchema):
    name = fields.Str(required=True, validate=Length(max=100))
    description = fields.Str(required=True, validate=Length(max=1000))
    organizer = fields.Str(required=False, validate=Length(max=100))
    datetime_of_event = fields.DateTime(required=True)


class UpdateEventSchema(BaseSchema):
    name = fields.Str(required=False, validate=Length(max=100))
    description = fields.Str(required=False, validate=Length(max=1000))
    organizer = fields.Str(required=False, validate=Length(max=100))
    datetime_of_event = fields.DateTime(required=False)


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
    event_schema = CreateEventSchema()
    errors = event_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    event = Event(
        data['name'],
        data['description'],
        data.get('organizer', None),
        data['datetime_of_event']
        )
    stored_events.append(event)
    return jsonify(event.__str__()), 201


@events.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()
    event_schema = UpdateEventSchema()
    errors = event_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    event = get_stored_event(event_id)
    if event:
        if (name:= data.get('name', None)):
            event.name = name
        if (description:= data.get('description', None)):
            event.description = description
        if (organizer:= data.get('organizer', None)):
            event.organizer = organizer
        if (datetime_of_event:= data.get('datetime_of_event', None)):
            event.datetime_of_event = datetime_of_event
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
