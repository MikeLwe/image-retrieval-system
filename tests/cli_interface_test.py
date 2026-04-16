import pytest
import redis.asyncio as redis
from unittest.mock import patch
import cli_interface
import asyncio

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
async def test_async_1():
    """Test CLI Interface being Asynchronous"""
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