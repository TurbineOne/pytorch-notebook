# Example Python program that uses domain sockets and the socket module function
# send_fds() to send file descriptors to another process.
import argparse
import os
import socket
import tempfile
import time

parser = argparse.ArgumentParser()
parser.add_argument("--file", help="First to send", type=str)
parser.add_argument("--url", help="URL to send", type=str)
parser.add_argument("--mp4", help="URL to send", type=str)

def send_file(file_name: str = None, url: str = None, mp4: str = None):
    # Create a UNIX Domain socket
    sender = socket.socket(socket.AF_UNIX)

    # Connect the socket to the server
    path = "notebooks/test.sock"
    sender.connect(path)

    # Append the descriptors to a list 
    desList = []
    msgb = b""
    if file_name:
        msgb = b"file"
        fds = os.open(file_name, os.O_RDONLY)
        desList.append(fds)
        socket.send_fds(sender, [msgb], desList, 2, None)
    elif url:
        msgb = b"url"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((url, 80))
        desList.append(s.fileno())
        socket.send_fds(sender, [msgb], desList, 2, None)
    elif mp4:
        msgb = b"mp4"
        with tempfile.NamedTemporaryFile() as tf:
            fds = os.open(tf.name, os.O_RDONLY)
            desList.append(fds)
            socket.send_fds(sender, [msgb], desList, 2, None)

            reader = os.open(mp4, os.O_RDONLY)
            for i in range(100):
                data = os.read(reader, 1024 * 100)
                if data:
                    os.write(fds, data)
                else:
                    break

    # Receive data from the Unix Domain Socket
    while(True):
        data = sender.recv(1024)
        if(data!=b''):
            print("Server Response:")
            print(data)
        else:    
            print("Connection closed by server")
            break

    sender.close()


if __name__ == '__main__':
    args = parser.parse_args()
    send_file(args.file, args.url, args.mp4)