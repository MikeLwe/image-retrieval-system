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
class ImageData:
    """
    Information about the image
    """
    encoded_data: bytes
    objects: dict #don't forget the case when the image has nothing of note
    encoding: str | None = None

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

    @classmethod
    async def create(cls, path: str, image_id: str):
        """
        Create an Image Payload Object async
        """

        mime, _ = mimetypes.guess_type(path)

        return cls(
            path=path,
            image_id=image_id,
            type=mime or "application/octet-stream",
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

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

    query: str
    event_id: str
    timestamp: str

    @classmethod
    async def create(cls, query: str):
        """
        Create an Request Payload Object async
        """

        return cls(
            query = query,
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def to_json(self):
        return json.dumps(asdict(self))
    
    @staticmethod
    def from_json(json_str: str):
        d = json.loads(json_str)
        d["data"] = ImageData(**d["data"])
        return ImagePayload(**d)