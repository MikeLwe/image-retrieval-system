import pytest
import redis.asyncio as redis

@pytest.mark.asyncio
async def test_redis_publish():
    """
    Default Test to see if Redis works
    """
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)

    result = await r.publish("test_channel", "hello")
    assert isinstance(result, int)

    await r.aclose()