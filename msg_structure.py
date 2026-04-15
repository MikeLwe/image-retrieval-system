"""
File that structures messages sent between services
"""

from dataclasses import dataclass, asdict
# import datetime
import json

@dataclass
class ImageData:
    """
    Information about the image
    """
    image_id: int
    path: str
    objects: dict | None = None
    encoding: str | None = None

@dataclass
class ImagePayload:
    """
    Payload of image sent between services
    """
    type: str
    event_id: str
    timestamp: str
    source: str
    data: ImageData

    def to_json(self):
        return json.dumps(asdict(self))
    
    @staticmethod
    def from_json(json_str: str):
        d = json.loads(json_str)
        d["data"] = ImageData(**d["data"])
        return ImagePayload(**d)

@dataclass
#temporary code... might change later as development happens
class RequestPayload:
    """
    Payload of a request
    """
    type: str
    event_id: str
    timestamp: str
    query: str

    def to_json(self):
        return json.dumps(asdict(self))
    
    @staticmethod
    def from_json(json_str: str):
        d = json.loads(json_str)
        d["data"] = ImageData(**d["data"])
        return ImagePayload(**d)