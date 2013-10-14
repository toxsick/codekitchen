import datetime
import json
from bson.objectid import ObjectId
from utils import date_to_str

class APIEncoder(json.JSONEncoder):
    """ Propretary JSONEconder subclass used by the json render function.
    This is needed to address the encoding of special values.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # convert any datetime to RFC 1123 format
            return date_to_str(obj)
        elif isinstance(obj, (datetime.time, datetime.date)):
            # should not happen since the only supported date-like format
            # supported at dmain schema level is 'datetime' .
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            # BSON/Mongo ObjectId is rendered as a string
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def render_json(data):
    """ JSON render function

    .. versionchanged:: 0.1.0
       Support for optional HATEOAS.
    """
    return json.dumps(data, cls=APIEncoder, sort_keys=True)
