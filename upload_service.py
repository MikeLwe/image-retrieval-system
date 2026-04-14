"""
Upload Service to tell other services that an Upload has been requested
"""
import redis
portnum = 6379

def start_upload_service(port):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def main(datapath):
    start_upload_service(portnum)

if __name__ == '__main__':
    main()