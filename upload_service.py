"""
Upload Service to tell other services that an Upload has been requested
"""
import redis
portnum = 6379

def main():
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

    except Exception:
        print("ruh roh")

    finally:
        pubsub.unsubscribe()
        pubsub.close()
        client.close()

    
    print("Upload Service: Call Received!")


if __name__ == '__main__':
    print("Upload Service Running...")
    main()