import pytest
import redis.asyncio as redis
from unittest.mock import AsyncMock
import asyncio
import time
from contextlib import redirect_stdout
import io
from cli_interface import create_parser, start_pubsub, run_services, structure_image, structure_request, stop_services
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
async def test_all_services_async_1():
    """Test the whether all services can run with payloads in them"""
    #create a redis client
    client = redis.Redis(host='localhost', port=portnum, decode_responses=True)

    services = [
        "upload_service.py",
        "image_service.py",
        "document_db_service.py",
        "embedding_service.py",
        "vector_index_service.py"
    ]
    
    #run all the services
    processes = []
    for s in services:
        p = await asyncio.create_subprocess_exec(
            "python", s,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        processes.append(p)
    await start_pubsub(client)
    await asyncio.sleep(1)  # give services time to subscribe


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
        client.publish('info_gathered', vector_r_payload.to_json()),

        #calling from document_db_service
        client.publish('stored_confirm', doc_u_payload.to_json()),
        client.publish('request_completed', doc_r_payload.to_json()),
    ]

    await asyncio.gather(*publish_tasks)

    multiple_outputs = await asyncio.gather(*(p.communicate() for p in processes))
    output = "".join(out[0].decode() for out in multiple_outputs)

    await asyncio.sleep(2)

    await stop_services(processes)

    assert output.count("Image Successfully Uploaded!") == 5
    assert output.count("Request Successfully Achieved!") == 4

# @pytest.mark.asyncio
# #AI support with this
# async def test_async_1():
#     """Test the asynchronous parser of CLI"""
#     mock_redis = AsyncMock()

#     # Add artificial delay to simulate real async work
#     async def fake_publish(channel, msg):
#         await asyncio.sleep(0.5)

#     mock_redis.publish.side_effect = fake_publish
#     parser = create_parser(mock_redis)
#     commands = [
#         "upload images/logo.png",
#         "upload images/mascot.png",
#         "upload images/seal.png",
#     ]

#     tasks = set()

#     start = time.perf_counter()

#     for cmd in commands:
#         args = parser.parse_args(cmd.split())
#         task = asyncio.create_task(args.func(args))
#         tasks.add(task)

#     await asyncio.gather(*tasks)

#     duration = time.perf_counter() - start

#     # If sequential: ~1.5s (running 3 times)
#     # If concurrent: < 1s (running 3 in aasync)
#     assert duration < 1.0