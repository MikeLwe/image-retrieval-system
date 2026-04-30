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

    @classmethod
    async def create(cls, init_label, init_x1, init_y1, init_x2, init_y2):
        """
        Create an Detected Data Object async
        """

        return cls(
            label = init_label,
            x1 = init_x1,
            y1 = init_y1,
            x2 = init_x2,
            y2 = init_y2
        )

@dataclass
class ImageData:
    """
    Information about the image
    """
    encoded_data: bytes
    encoding: str
    objects: list[DetectedObject] #no objects detected -> size = 0

    @classmethod
    async def create(cls, init_encoded_data, init_objects = None, init_encoding = "base64"):
        """
        Create an Image Data Object async
        """

        if init_objects is None:
            init_objects = []

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

    @staticmethod
    def from_json(json_str: str):
        d = json.loads(json_str)

        return RequestPayload(
            query=d["query"],
            labels=list(d.get("labels", [])),
            event_id=d["event_id"],
            timestamp=d["timestamp"]
        )
    
@dataclass
class ConfirmImageStored:
    """
    Payload of image stored confirmation
    """
    type: str #image file type
    event_id: str #id for this event
    image_id: str #id associated with this image
    timestamp: str #time event created (MAY REMOVE)
    path: str #file path where image was uploaded from
    vector_stored: bool #confirm vector was stored
    database_stored: bool #confirm database was stored
    data: ImageData | None = None #objects from the image (TEMPORARY?)

    @classmethod
    async def create(cls, 
                     init_type, 
                     init_event_id,
                     init_image_id,
                     init_timestamp,
                     init_path,
                     init_data,
                     init_vector = False,
                     init_database = False,
                     ):
        """
        Create an Request Payload Object async
        """

        return cls(
            type = init_type,
            event_id = init_event_id,
            image_id = init_image_id,
            timestamp = init_timestamp,
            path = init_path,
            data = init_data,
            vector_stored = init_vector,
            database_stored = init_database
        )

    def to_json(self):
        return json.dumps(asdict(self), default=str)

    @staticmethod
    def from_json(json_str: str):
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

        return ConfirmImageStored(
            type=d["type"],
            event_id=d["event_id"],
            image_id=d["image_id"],
            timestamp=d["timestamp"],
            path=d["path"],
            data=data,
            vector_stored=d["vector_stored"],
            database_stored=d["database_stored"]
        )

@dataclass
class RequestedInfoPayload:
    """
    Payload of request information
    """

    event_id: str
    timestamp: str
    similar_labels: list[str] #similar labels around request
    images: list[ImageData] #send back images with similar labels

    @classmethod
    async def create(cls,
                     init_event_id,
                     init_timestamp,
                     init_similar_labels = None,
                     init_images=None):
        """
        Create an Requested Information Payload Object async
        """

        if init_similar_labels is None:
            init_similar_labels = []
        if init_images is None:
            init_images = []

        return cls(
            event_id=init_event_id,
            timestamp=init_timestamp,
            similar_labels = init_similar_labels,
            images = init_images
        )

    def to_json(self):
        return json.dumps(asdict(self), default=str)

    @staticmethod
    def from_json(json_str: str):
        d = json.loads(json_str)

        return RequestedInfoPayload(
            event_id=d["event_id"],
            timestamp=d["timestamp"],
            similar_labels=list(d.get("similar_labels", [])),
            images=list(d.get("images", []))
        )