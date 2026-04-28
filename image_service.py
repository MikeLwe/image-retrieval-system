import redis.asyncio as redis
import base64
import asyncio
import logging
import aiofiles
from msg_structure import ImagePayload, ImageData, DetectedObject, RequestPayload
import os

portnum = 6379

#error log file config, works globally as the program should start here
logging.basicConfig(
    filename="error_log.txt",          # file to write to
    level=logging.ERROR,           # only log errors and above
    #time at error - name of file error came from - severity of error - message
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def infer_image(image: ImagePayload):
    """
    Identifies the contents of the image and initializes the objects field
    """
    #gets the DetectedObjects and stores them in the list
    if image.path == "images/logo.png":
        image.data.object = []
    # image.data.object = []
    return image

async def analyze_request(request: RequestPayload):
    """
    Converts query into a dictionary to be read by the embedding service
    """
    #gets the key words as str and stores them in the list
    request.labels = []
    return request

async def main():
    #create a redis client running on an image I am running
    client = redis.Redis(host='localhost', port=portnum, decode_responses=True)

    #declare channels
    in_upload_ch = 'image_uploaded'
    in_request_ch = 'request'
    out_upload_ch = 'image_processed'
    out_request_ch = 'text_processed'

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
                        img_payload = ImagePayload.from_json(message['data'])
                        print(f"Received: {img_payload.path}") #REMOVE LATER
                        img_payload = await infer_image(img_payload)
                        await client.publish(out_upload_ch, img_payload.to_json())
                        print(f"Image Processed")

                    except Exception as e:
                        logging.error(f"Something went wrong. {e}", exc_info=True)
                        print("Upload Image Service Error")
                elif message['channel'] == in_request_ch:
                    try:
                        rq_payload = RequestPayload.from_json(message['data'])
                        print(f"Received: {rq_payload.query}") #REMOVE LATER
                        rq_payload = await analyze_request(rq_payload)
                        await client.publish(out_request_ch, rq_payload.to_json())
                        print(f"Request Processed")

                    except Exception as e:
                        logging.error(f"Something went wrong. {e}", exc_info=True)
                        print("Request Image Service Error")
                    

    except Exception as e:
        logging.error(f"Something wrong happened. {e}", exc_info=True)
        print("ruh roh fatal error")

    finally:
        await pubsub.unsubscribe() #remove later?
        await pubsub.aclose()
        await client.aclose()

if __name__ == '__main__':
    print("Image Service Running...")
    asyncio.run(main())