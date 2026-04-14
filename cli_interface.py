#take an input and know where to send the input
"""
CLI Interface to broadcast user uploading a file or requesting images
"""

import argparse
import shlex
import logging
import redis
import subprocess

#Run this command: docker run -d -p 6379:6379 --name images redis

#ChatGPT helped
#error log file config, works globally as the program should start here
logging.basicConfig(
    filename="error_log.txt",          # file to write to
    level=logging.ERROR,           # only log errors and above
    #time at error - name of file error came from - severity of error - message
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def request_handler(args):
    """
    Handles the query input from the user to run the query_service main function
    """
    query = " ".join(args.query)
    print("Reading your query...")
    # query_service.main(query)
    pass

def upload_handler(args):
    """
    Handles the upload input from the user to run the csv_loader main function
    """
    print("Uploading CSV to database...\n")
    # csv_loader.main(args.filepath)
    return

def run_services():
    """
    Starts all of the services required for the program
    """
    subprocess.Popen(["python, upload_service.py"])
    subprocess.Popen(["python, image_service.py"])
    subprocess.Popen(["python, document_db_service.py"])
    subprocess.Popen(["python, embedding_service.py"])

def main():
    """
    Runs the CLI Interface
    """

    services = ["upload_service.py",
                "image_service.py",
                "document_db_service.py",
                "embedding_service.py"]

    #create redis client for cli-interface
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    #run all the services
    run_services()

    #create a parser
    parser = argparse.ArgumentParser()

    #create the subparsers/commands and making the subparser required
    subparsers = parser.add_subparsers(dest="command", required=True)

    #request subcommand
    parser_query = subparsers.add_parser("request")
    parser_query.add_argument("request", nargs="+") #joins string args together
    parser_query.set_defaults(func=request_handler)

    #upload subcommand
    parser_upload = subparsers.add_parser("upload")
    parser_upload.add_argument("filepath", type=str)
    parser_upload.set_defaults(func=csv_handler)

    print("Interactive CLI for DataSheet AI running. Type 'exit' to quit.")
    print("Available commands: request, upload")

    #Complete assistance with ChatGPT:
    while True:
        try:
            #adds the classic > in the terminal
            user_input = input("> ").strip()
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

            # Parse arguments for subcommands
            args = parser.parse_args(args_list)
            #check if command exists by using the argument (first word of input)
            if hasattr(args, "func"):
                args.func(args)
            else:
                print("Unknown command. Available: query, upload")

        except KeyboardInterrupt as e:
            print("\nShutting all services down...")
            

        except Exception as e:
            print(f"Error: {e}")
            logging.

if __name__ == '__main__':
    main()