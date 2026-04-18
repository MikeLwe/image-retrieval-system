"""
File that structures messages sent between services
"""

from dataclasses import dataclass, asdict
import uuid
from datetime import datetime, timezone
import mimetypes
import json
# from typing import Optional
 
@dataclass
class DetectedObject:
    """
    Information about the objects detected in an image
    """
    label: str
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float | None = None #in case confidence isn't provided

@dataclass
class ImageData:
    """
    Information about the image
    """
    encoded_data: bytes
    encoding: str
    objects: list[DetectedObject] #no objects detected -> size = 0

    @classmethod
    async def create(cls, init_encoded_data, init_objects = [], init_encoding = "base64"):
        """
        Create an Image Data Object async
        """

        return cls(
            encoded_data = init_encoded_data,
            objects = init_objects,
            encoding = init_encoding
        )

@dataclass
class ImagePayload:
    """
    Payload of image sent between services
    """
    type: str #image file type
    event_id: str #id for this event
    image_id: str #id associated with this image
    timestamp: str #time event created (MAY REMOVE)
    path: str #file path where image was uploaded from
    data: ImageData | None = None

    #AI assisted with implementing this function
    @classmethod
    async def create(cls, init_path: str, init_image_id: str):
        """
        Create an Image Payload Object async
        """

        mime, _ = mimetypes.guess_type(init_path)

        return cls(
            path=init_path,
            image_id=init_image_id,
            type=mime or "application/octet-stream",
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            data = None
        )

    def to_json(self):
        return json.dumps(asdict(self), default=str)
    
    @staticmethod
    def from_json(json_str: str) -> "ImagePayload":
        d = json.loads(json_str)

        data = d.get("data")
        if data is not None:
            objects = data.get("objects", [])

            data = ImageData(
                encoded_data=data["encoded_data"],
                encoding=data["encoding"],
                objects=[
                    DetectedObject(**obj) for obj in objects
                ]
            )

        return ImagePayload(
            type=d["type"],
            event_id=d["event_id"],
            image_id=d["image_id"],
            timestamp=d["timestamp"],
            path=d["path"],
            data=data
        )

@dataclass
#temporary code... might change later as development happens
class RequestPayload:
    """
    Payload of a request
    """

    query: str
    labels: list[str]
    event_id: str
    timestamp: str

    @classmethod
    async def create(cls, init_query, init_labels = None):
        """
        Create an Request Payload Object async
        """

        if init_labels is None:
            init_labels = []

        return cls(
            query = init_query,
            labels = init_labels, #embedding will look for words, this is where that is stored
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def to_json(self):
        return json.dumps(asdict(self), default=str)
    
    # @staticmethod
    # #BUG MAY EXIST IF MISSING FIELDS, WRONG TYPES, PARTIAL PAYLOAD
    # def from_json(json_str: str):
    #     d = json.loads(json_str)
    #     d = json.loads(json_str)
    #     return RequestPayload(**d)

    #SOLUTION:
    @staticmethod
    def from_json(json_str: str):
        d = json.loads(json_str)

        return RequestPayload(
            query=d["query"],
            labels=list(d.get("labels", [])),
            event_id=d["event_id"],
            timestamp=d["timestamp"]
        )