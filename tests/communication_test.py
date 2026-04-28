import pytest
import redis.asyncio as redis
from unittest.mock import AsyncMock
import asyncio
import time
from contextlib import redirect_stdout
import io
from cli_interface import create_parser, run_services, structure_image, structure_request, stop_services
from upload_service import encode_image
from image_service import infer_image, analyze_request
from embedding_service import embed_image, embed_request
from vector_index_service import store_image_embed, compare_request
from document_db_service import store_image, gather_requested_images
from msg_structure import ImagePayload, ImageData, DetectedObject, RequestPayload, ConfirmImageStored, RequestedInfoPayload

portnum = 6379

# @pytest.mark.asyncio
# async def test_redis_publish():
#     """
#     Default Test to see if Redis works
#     """
#     r = redis.Redis(host="localhost", port=6379, decode_responses=True)

#     result = await r.publish("test_channel", "hello")
#     assert isinstance(result, int)

#     await r.aclose()


@pytest.mark.asyncio
async def test_test():
    """
    Sanity Check
    """
    assert True

@pytest.mark.asyncio
async def test_all_services_async_1():
    """Test the whether all services can run with payloads in them"""
    #create a redis client
    client = redis.Redis(host='localhost', port=portnum, decode_responses=True)

    services = [
        # "cli_interface.py",
        "upload_service.py",
        "image_service.py",
        "document_db_service.py",
        "embedding_service.py",
        "vector_index_service.py"
    ]
    
    #run all the services
    processes = await run_services(services)

    await asyncio.sleep(3)  # give services time to subscribe

    #initializing all variables
    #cli
    file = "images/logo.png"
    cli_u_payload = await structure_image(file, 0)
    query = "show me images of a test"
    cli_r_payload = await structure_request(query)

    #upload
    img_obj = await encode_image(cli_u_payload.path)
    upload_u_payload = cli_u_payload
    upload_u_payload.data = await ImageData.create(img_obj)

    #image
    image_u_payload = await infer_image(upload_u_payload)
    image_r_payload = await analyze_request(cli_r_payload)

    #embedding
    embed_u_payload = await embed_image(image_u_payload)
    embed_r_payload = await embed_request(image_r_payload)

    #vector index
    vector_u_payload = await store_image_embed(embed_u_payload)
    vector_r_payload = await compare_request(embed_r_payload)

    #document db
    doc_u_payload = await store_image(vector_u_payload)
    doc_r_payload = await gather_requested_images(vector_r_payload)

    publish_tasks = [
        #calling from cli_interface
        client.publish('upload', cli_u_payload.to_json()),
        client.publish('request', cli_r_payload.to_json()),

        #calling from upload_service

        client.publish('image_uploaded', upload_u_payload.to_json()),

        #calling from image_service

        client.publish('image_processed', image_u_payload.to_json()),
        client.publish('text_processed', image_r_payload.to_json()),

        #calling from embedding_service
        client.publish('image_embedded', embed_u_payload.to_json()),
        client.publish('text_embedded', embed_r_payload.to_json()),

        #calling from vector_index_service
        client.publish('image_stored', vector_u_payload.to_json()),
        client.publish('info_gathered', vector_r_payload.to_json())

        # #calling from document_db_service
        # client.publish('stored_confirm', doc_u_payload.to_json()),
        # client.publish('request_completed', doc_r_payload.to_json())
    ]

    await asyncio.gather(*publish_tasks)
    # await asyncio.sleep(1)  # give services time to subscribe

    pubsub = client.pubsub()
    await pubsub.subscribe('stored_confirm', 'request_completed')

    count_message = 0
    # start = asyncio.get_event_loop().time()
    max_messages = 9
    timeout = 5
    # timeout_occurred = 0

    while True:
        try:
            message = await asyncio.wait_for(pubsub.get_message(ignore_subscribe_messages=True), timeout=timeout)
        except asyncio.TimeoutError:
            print("Timeout reached")
            break

        if message is None:
            continue
        if message["type"] != "message":
            continue
        
        if message["type"] == "message":
            if message["channel"] == 'stored_confirm':
                img_payload = ConfirmImageStored.from_json(message['data'])
                print(f"Received: {img_payload.path}") #REMOVE LATER
                
                if img_payload.database_stored and img_payload.vector_stored:
                    print(f"Image Successfully Uploaded!")
                    count_message += 1
                else:
                    print(f"Something did not save properly...")

            elif message["channel"] == 'request_completed':
                rq_payload = RequestedInfoPayload.from_json(message['data'])
                print(f"Received: {len(rq_payload.similar_labels)} labels") #REMOVE LATER
                
                print(f"Request Successfully Achieved!")
                count_message += 1

        print(f"Received {count_message} messages\n")

    await pubsub.unsubscribe()
    await pubsub.aclose()
    await stop_services(processes)

    assert count_message == max_messages