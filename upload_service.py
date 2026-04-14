"""
Upload Service to tell other services that an Upload has been requested
"""
import redis
import base64
import asyncio
import logging
portnum = 6379

#error log file config, works globally as the program should start here
logging.basicConfig(
    filename="error_log.txt",          # file to write to
    level=logging.ERROR,           # only log errors and above
    #time at error - name of file error came from - severity of error - message
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def encode_image(image_path):
    """
    Encode an Image into Base64
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')

async def main():
    #create a redis client running on an image I am running
    client = redis.Redis(host='localhost', port=portnum, decode_responses=True)

    #create pubsub instance 
    pubsub = client.pubsub()
    pubsub.subscribe('upload')

    try:
        # message is a dict like {'type': 'message', 'pattern': None, 'channel': 'my_channel', 'data': '...'}
        for message in pubsub.listen():
            # 'message' is a dict. type 'message' contains actual data.
            if message['type'] == 'message':
                print(f"Received: {message['data']}")
                encoded_img = encode_image(message['data'])
                client.publish('image_uploaded', encoded_img)
                print(f"Image Uploaded")
                await asyncio.sleep(1)

    except Exception as e:
        logging.error(f"Something wrong happened. {e}", exc_info=True)
        print("ruh roh")

    finally:
        pubsub.unsubscribe()
        pubsub.close()
        client.close()

    
    print("Upload Service: Call Received!")


if __name__ == '__main__':
    print("Upload Service Running...")
    asyncio.run(main())