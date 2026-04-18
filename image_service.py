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
    return image

async def analyze_request(request: RequestPayload):
    """
    Converts request into a dictionary to be read
    """
    return request

async def main():
    #create a redis client running on an image I am running
    client = redis.Redis(host='localhost', port=portnum, decode_responses=True)

    #create pubsub instance 
    pubsub = client.pubsub()
    await pubsub.subscribe('image_uploaded', 'request')

    try:
        # message is a dict like {'type': 'message', 'pattern': None, 'channel': 'my_channel', 'data': '...'}
        async for message in pubsub.listen():
            # 'message' is a dict. type 'message' contains actual data.
            if message['type'] == 'message':
                if message['channel'] == 'image_uploaded':
                    try:
                        print(f"Received: {message['data']}") #REMOVE LATER

                        encoded_img = await encode_image(message['data'])
                        image = await structure_image(message['data'], encoded_img)
                        await client.publish('image_processed', image)
                        print(f"Image Processed")

                        #In case the user has the wrong file input
                    except FileNotFoundError as e:
                        logging.error(f"File not found. {e}", exc_info=True)
                        print("File does not exist. Please check your input.")
                elif message['channel'] == 'request':
                    try:
                        print(f"Received: {message['data']}") #REMOVE LATER

                        image = await structure_request(message['data'])
                        #include more information in this payload------------------------
                        await client.publish('text_processed', image)
                        print(f"Image Processed")

                        #In case the user has the wrong file input
                    except FileNotFoundError as e:
                        logging.error(f"File not found. {e}", exc_info=True)
                        print("File does not exist. Please check your input.")
                    

    except Exception as e:
        logging.error(f"Something wrong happened. {e}", exc_info=True)
        print("ruh roh fatal error")

    finally:
        await pubsub.unsubscribe() #remove later
        await pubsub.aclose()
        await client.aclose()

    
    print("Upload Service: Call Received!")
if __name__ == '__main__':
    print("Image Service Running...")