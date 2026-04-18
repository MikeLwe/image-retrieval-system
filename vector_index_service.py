import redis.asyncio as redis
import asyncio
import logging
from msg_structure import ImagePayload, ImageData, DetectedObject, RequestPayload, ConfirmImageStored, RequestedInfoPayload

portnum = 6379

#error log file config, works globally as the program should start here
logging.basicConfig(
    filename="error_log.txt",          # file to write to
    level=logging.ERROR,           # only log errors and above
    #time at error - name of file error came from - severity of error - message
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def store_image_embed(image: ImagePayload):
    """
    Stores Image Embedding into Database
    """
    #if successful storage, create confirm object
    confirm_image = await ConfirmImageStored.create(
        image.type,
        image.event_id,
        image.image_id,
        image.timestamp,
        image.path,
        image.data, #MAY REMOVE
        True
    )
    return confirm_image

async def compare_request(request: RequestPayload):
    """
    Embeds Request labels
    """
    #if successful comparison of vectors within some arbitrary epsilon
    nearby_labels = []
    requested_payload = await RequestedInfoPayload.create(
        request.event_id,
        request.timestamp,
        nearby_labels
    )
    return requested_payload

async def main():
    #create a redis client running on an image I am running
    client = redis.Redis(host='localhost', port=portnum, decode_responses=True)

    #declare channels
    in_upload_ch = 'image_embedded'
    in_request_ch = 'text_embedded'
    out_upload_ch = 'image_stored'
    out_request_ch = 'info_gathered'

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
                        img_payload = await store_image_embed(img_payload) #UPDATE THIS LATER
                        
                        if not img_payload.vector_stored:
                            print("vector db not stored?")
                            raise Exception
                        
                        await client.publish(out_upload_ch, img_payload.to_json())
                        print(f"Image Embedding Stored")

                    except Exception as e:
                        logging.error(f"Something went wrong. {e}", exc_info=True)
                        print("Upload Vector Index Service Error")

                elif message['channel'] == in_request_ch:
                    try:
                        rq_payload = RequestPayload.from_json(message['data'])
                        print(f"Received: {rq_payload.query}") #REMOVE LATER
                        rq_payload = await compare_request(rq_payload)
                        await client.publish(out_request_ch, rq_payload.to_json())
                        print(f"Requested Info Gathered")

                    except Exception as e:
                        logging.error(f"Something went wrong. {e}", exc_info=True)
                        print("Request Vector Index Service Error")
                    

    except Exception as e:
        logging.error(f"Something wrong happened. {e}", exc_info=True)
        print("ruh roh fatal error")

    finally:
        await pubsub.unsubscribe() #remove later?
        await pubsub.aclose()
        await client.aclose()

if __name__ == '__main__':
    print("Vector Index Service Running...")
    asyncio.run(main())