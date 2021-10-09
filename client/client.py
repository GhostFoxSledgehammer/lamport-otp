

import socket
import sys
from ast import literal_eval  # Used to safely parse list from file

''' GLOBALS '''

IS_DEBUG = False

OUT_CLIENT_FILE = "client_passwords.txt"

PROGRAM_ARG_NUM = 0    # i.e. sys.argv[0]
IP_ARG_NUM = 1
PORT_ARG_NUM = 2

SERVER_IP = "localhost"
SERVER_PORT = 40000
BUFF_SIZE = 1024


''' CLASSES '''


class FileService:
    def __init__(self):
        print_debug("Creating FileService...")
        print_debug("Successful init of FileService")

    def get_list_from_file(self):
        """Parses list literal from client passwords file."""
        try:
            cfile = open(OUT_CLIENT_FILE, "r")
            list_pwords = literal_eval(cfile.read())  # ast lib provides safe literal parsing
        except:
            error_quit("Failed to read from file %s" % cfile.name, 403)
        return list_pwords

    def remove_used_password(self, list_passwords):
        """Removes first password (which was recently used) from list file."""
        try:
            cfile = open(OUT_CLIENT_FILE, "w")
            cfile.write("%s\n" % str(list_passwords[1:]))
        finally:
            cfile.close()


''' FUNCTIONS '''


def usage():
    """Prints the usage/help message for this program."""
    program_name = sys.argv[PROGRAM_ARG_NUM]
    print("\nUsage:")
    print("\t%s" % program_name)
    print("\tFile \"%s\" must exist and be populated with a list of passwords." % OUT_CLIENT_FILE)
    print("\tNew passwords can be generated by running \"generate_list.py\"")


def error_quit(msg, code):
    """Prints out an error message, the program usage, and terminates with an
       error code of `code`."""
    print("\n[!] %s" % msg)
    usage()
    sys.exit(code)


def get_next_password(file_service):
    try:
        if not file_service.get_list_from_file():
            print_debug("List of passwords is empty")
            error_quit("All passwords have been exhausted, please generate a new list of passwords!", 200)
        pword = file_service.get_list_from_file()[0]
    except Exception:
        error_quit("Failed to read first password", 500)
    return pword


def send_to_server(ip, port, pword):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
        sock.send(pword.encode())
        msg_recv = sock.recv(BUFF_SIZE).decode('utf-8')
        sock.close()
    except socket.error:
        error_quit("Connection refused, did you specify the correct host and port?", 400)
    except Exception as e:
        print(str(e))
        error_quit("Terminating session due to issue in transmission.", 400)
    return msg_recv


''' DEBUG '''


def print_debug(msg):
    """Prints if we are in debug mode."""
    if IS_DEBUG:
        print(msg)


''' MAIN '''


def main():
    """Main driver that parses args & creates objects."""
    print_debug("Starting...")
    file_service = FileService()

    pword = get_next_password(file_service)
    print_debug("Password %s will be used to authenticate." % pword)

    # If IP & Port are passed as args, use them.
    # Otherwise, default to localhost:40000.
    # Note: IP & Port should be passed together, not one or the other.
    ip = sys.argv[IP_ARG_NUM] if len(sys.argv) == PORT_ARG_NUM + 1 else SERVER_IP
    port = sys.argv[PORT_ARG_NUM] if len(sys.argv) == PORT_ARG_NUM + 1 else SERVER_PORT

    # Send otp to server, print response.
    resp = send_to_server(ip, port, pword)
    print(resp)

    # Otp was used, so remove it from the list.
    file_service.remove_used_password(file_service.get_list_from_file())
    print_debug("Done!")


''' PROCESS '''


if __name__ == '__main__':
    main()