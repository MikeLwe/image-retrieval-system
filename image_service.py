import redis.asyncio as redis
import base64
import asyncio
import logging
import aiofiles
from msg_structure import ImagePayload, ImageData
import os

portnum = 6379

#error log file config, works globally as the program should start here
logging.basicConfig(
    filename="error_log.txt",          # file to write to
    level=logging.ERROR,           # only log errors and above
    #time at error - name of file error came from - severity of error - message
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def encode_image(image_path):
    """
    Encode an Image into Base64
    """
    async with aiofiles.open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(await image_file.read())
        return encoded_string.decode('utf-8')

# async def structure_image(filepath, encoding):
#     """
#     Compact all image information into one object
#     """
#     return filepath

# async def structure_request(query):
#     """
#     Convert query into an event
#     """
#     return query

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
                if message['channel'] == 'upload':
                    try:
                        print(f"Received: {message['data']}") #REMOVE LATER

                        encoded_img = await encode_image(message['data'])
                        image = await structure_image(message['data'], encoded_img)
                        #include more information in this payload------------------------
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