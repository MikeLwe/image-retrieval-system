import redis.asyncio as redis
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from msg_structure import ImagePayload, ImageData, DetectedObject, RequestPayload, ConfirmImageStored, RequestedInfoPayload

portnum = 6379

#error log file config, works globally as the program should start here
logging.basicConfig(
    filename="error_log.txt",          # file to write to
    level=logging.ERROR,           # only log errors and above
    #time at error - name of file error came from - severity of error - message
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def insert_one(collection, data):
    data = data.to_json()
    result = await collection.insert_many([data])
    print(result.inserted_ids)
    return True #CHECK HOW TO SEE IF THIS WORKED

async def store_image(image: ImagePayload, collection):
    """
    Embeds Image file objects
    """
    stored = asyncio.run(insert_one(collection, image))
    #if successful storage, create confirm object
    confirm_image = await ConfirmImageStored.create(
        image.type,
        image.event_id,
        image.image_id,
        image.timestamp,
        image.path,
        image.data, #MAY REMOVE
        image.vector_stored,
        False
    )
    if stored:
        confirm_image = await ConfirmImageStored.create(
            image.type,
            image.event_id,
            image.image_id,
            image.timestamp,
            image.path,
            image.data, #MAY REMOVE
            image.vector_stored,
            True
        )
    return confirm_image

async def gather_requested_images(request: RequestPayload):
    """
    Embeds Request labels
    """
    #if successful retrival of images with similar labels
    similar_images = []
    requested_payload = await RequestedInfoPayload.create(
        request.event_id,
        request.timestamp,
        request.similar_labels,
        similar_images
    )
    return requested_payload

async def main():
    #create a redis client running on an image I am running
    client = redis.Redis(host='localhost', port=portnum, decode_responses=True)

    #create instance of MongoDB
    db_client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = db_client["document_db"]
    collection = db["image_objects"]

    #declare channels
    in_upload_ch = 'image_stored'
    in_request_ch = 'info_gathered'
    out_upload_ch = 'stored_confirm'
    out_request_ch = 'request_completed'

    #create pubsub instance 
    pubsub = client.pubsub()
    await pubsub.subscribe(in_upload_ch, in_request_ch)

    try:
        # message is a dict like {'type': 'message', 'pattern': None, 'channel': 'my_channel', 'data': '...'}
        async for message in pubsub.listen():
            # 'message' is a dict. type 'message' contains actual data.
            if message['type'] == 'message':
                if message['channel'] == in_upload_ch:
                    try:
                        img_payload = ConfirmImageStored.from_json(message['data'])
                        print(f"Received: {img_payload.path}") #REMOVE LATER
                        img_payload = await store_image(img_payload, collection) #UPDATE THIS LATER
                        
                        if not img_payload.database_stored:
                            print("database not stored?")
                            raise Exception
                        
                        
                        await client.publish(out_upload_ch, img_payload.to_json())
                        print(f"Image Stored in Database")

                    except Exception as e:
                        logging.error(f"Something went wrong. {e}", exc_info=True)
                        print("Upload Document Database Service Error")
                elif message['channel'] == in_request_ch:
                    try:
                        rq_payload = RequestedInfoPayload.from_json(message['data'])
                        print(f"Received: {len(rq_payload.similar_labels)} labels") #REMOVE LATER
                        rq_payload = await gather_requested_images(rq_payload)
                        await client.publish(out_request_ch, rq_payload.to_json())
                        print(f"Requested Images Sent")

                    except Exception as e:
                        logging.error(f"Something went wrong. {e}", exc_info=True)
                        print("Request Document Database Service Error")
                    

    except Exception as e:
        logging.error(f"Something wrong happened. {e}", exc_info=True)
        print("ruh roh fatal error")

    finally:
        await pubsub.unsubscribe() #remove later?
        await pubsub.aclose()
        await client.aclose()

if __name__ == '__main__':
    print("Document Database Service Running...")
    asyncio.run(main())