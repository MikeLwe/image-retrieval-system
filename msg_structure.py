"""
File that structures messages sent between services
"""

from dataclasses import dataclass, asdict
# import datetime
import json

@dataclass
class ImageData:
    image_id: str
    path: str
    encoding: str | None = None

@dataclass
class ImagePayload:
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