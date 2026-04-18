#take an input and know where to send the input
"""
CLI Interface to broadcast user uploading a file or requesting images
"""

import argparse
import shlex
import logging
import redis.asyncio as redis
import asyncio
import time
from msg_structure import ImagePayload, ImageData, RequestPayload

#Run this command: docker run -d -p 6379:6379 --name images redis

#error log file config
logging.basicConfig(
    filename="error_log.txt",          # file to write to
    level=logging.ERROR,           # only log errors and above
    #time at error - name of file error came from - severity of error - message
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

i = 0 #TEMPORARY ID SOLUTION------------------

async def request_handler(args):
    """
    Handles the query input from the user to run the query_service main function
    """
    request = " ".join(args.request)
    
    r = args.redis
    request = args.request

    try:
        await r.publish('request', request)
    except Exception as e:
        print(f"Error: {e}")

async def upload_handler(args):
    """
    Handles the upload input from the user to run the csv_loader main function
    """
    print("Uploading Image to database...\n")
    global i #TEMPORARY ID SOLUTION------------------
    r = args.redis
    path = args.filepath
    img_id = f"img_{i}"

    i = i + 1 #TEMPORARY ID SOLUTION------------------

    upload_payload = await structure_image(path, img_id)

    try:
        await r.publish('upload', upload_payload)
    except Exception as e:
        print(f"Error: {e}")

async def structure_image(filepath, img_id):
    """
    Compact image information into an event
    """
    image_payload = await ImagePayload.create(
        path=filepath,
        image_id=img_id
    )
    return image_payload

async def structure_request(query):
    """
    Convert query into an event
    """
    request_payload = await RequestPayload.create(
        query=query,
    )
    return request_payload

def create_parser(client, is_test = False):
    """
    Support function for making a parser of the user input
    """
    #create a parser
    parser = argparse.ArgumentParser()

    #create the subparsers/commands and making the subparser required
    subparsers = parser.add_subparsers(dest="command", required=True)

    #request subcommand
    parser_query = subparsers.add_parser("request")
    parser_query.add_argument("request", nargs="+") #joins string args together
    parser_query.set_defaults(func=request_handler, redis=client, test=is_test)

    #upload subcommand
    parser_upload = subparsers.add_parser("upload")
    parser_upload.add_argument("filepath", type=str)
    parser_upload.set_defaults(func=upload_handler, redis=client, test=is_test)

    print("\nInteractive CLI for Image Reteival System running. Type 'exit' to quit.")
    print("Available commands:\n request <description>\n upload <filepath>\n")

    return parser

async def run_services(services):
    """
    Starts all of the services required for the program
    """
    procs = []

    for file in services:
        p = await asyncio.create_subprocess_exec("python", file)
        procs.append(p)

    return procs

async def stop_services(processes):
    """
    End all running services
    """
    for proc in processes:
        try:
            proc.terminate()
        #in case processes are all terminated already
        except ProcessLookupError:
            continue
        
    #AI code review help:   
    for proc in processes:
        try:
            await proc.wait()
        except Exception:
            pass

    print("All processes stopped.")

async def main(is_test = False):
    """
    Runs the CLI Interface
    """

    services = ["upload_service.py",
                "image_service.py",
                "document_db_service.py",
                "embedding_service.py",
                "vector_index_service.py"]

    #create redis client for cli-interface
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    #run all the services
    processes = await run_services(services)
    print("Starting all services...\n")
    time.sleep(1.5)

    #create parsers
    parser = create_parser(r, is_test)

    try:
        while True:
            #adds the classic > in the terminal
            # user_input = await asyncio.to_thread(input,"> ")
            user_input = await asyncio.to_thread(input)
            user_input = user_input.strip()
            #method of closing the CLI Interface
            if user_input.lower() in ("exit", "quit"):
                print("Closing the Interactive CLI...")
                break

            # Split input like shell arguments
            #ex: query datatables/test1.csv => ['query', 'datatables/test1.csv']
            #good for flexibility
            args_list = shlex.split(user_input)
            if not args_list:
                continue
            
            #AI suggestion for catching errors:
            valid_commands = {"request", "upload"}

            if args_list[0] not in valid_commands:
                print(f"Unknown command: {args_list[0]}")
                print("Available commands:\n request <description>\n upload <filepath>\n")
                continue

            if len(args_list) < 2:
                if args_list[0] == "request":
                    print("Command request is missing argument <description>.\n")
                elif args_list[0] == "uplaod":
                    print("Command upload is missing argument <filepath>.\n")
                continue

            # Parse arguments for subcommands
            try:
                args = parser.parse_args(args_list)
            except SystemExit:
                continue
            #check if command exists by using the argument (first word of input)
            if hasattr(args, "func"):
                asyncio.create_task(args.func(args))
            else:
                print("Unknown command. Available: request, upload")

    except KeyboardInterrupt as e:
        print("\nShutting all services down...")

    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Something wrong happened. {e}", exc_info=True)
    
    finally:
        await stop_services(processes)

if __name__ == '__main__':
    asyncio.run(main())