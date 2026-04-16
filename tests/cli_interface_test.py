import pytest
import redis.asyncio as redis
from unittest.mock import AsyncMock
import asyncio
import time
from cli_interface import create_parser

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
async def test_cli_1():
    """Test CLI Interface functions"""
    # cli_interface.main()
    proc = await asyncio.create_subprocess_exec(
        "python", "cli_interface.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    commands = [
        "upload images/logo.png\n",
        "exit\n"
    ]
    for cmd in commands:
        proc.stdin.write(cmd.encode())
        await proc.stdin.drain()
    
    stdout, _ = await proc.communicate()
    output = stdout.decode()
    assert "Uploading Image to database" in output
    assert "All processes stopped." in output

@pytest.mark.asyncio
#AI support with this
async def test_async_1():
    """Test the asynchronous parser of CLI"""
    mock_redis = AsyncMock()

    # Add artificial delay to simulate real async work
    async def fake_publish(channel, msg):
        await asyncio.sleep(0.5)

    mock_redis.publish.side_effect = fake_publish
    parser = create_parser(mock_redis)
    commands = [
        "upload images/logo.png",
        "upload images/mascot.png",
        "upload images/seal.png",
    ]

    tasks = set()

    start = time.perf_counter()

    for cmd in commands:
        args = parser.parse_args(cmd.split())
        task = asyncio.create_task(args.func(args))
        tasks.add(task)

    await asyncio.gather(*tasks)

    duration = time.perf_counter() - start

    # If sequential: ~1.5s (running 3 times)
    # If concurrent: < 1s (running 3 in aasync)
    assert duration < 1.0