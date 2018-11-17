# -*- coding: utf-8 -*-

import getopt
import socket
import subprocess
import sys
import threading

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def run_command(command):

    command = command.rstrip()

    try:
        output = subprocess.check_output(command,
                                         stderr=subprocess.STDOUT,
                                         shell=True)
    except:
        output = "Failed to execute command.\r\n"

    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):

        file_buffer = ""

        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            file_buffer += data

        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
        except:
            mensage = "Failed to save file to {}\r\n"
            client_socket.send(mensage.format(upload_destination))

    if len(execute):

        output = run_command(execute)

        client_socket.send(output)

    if command:
        while True:
            client_socket.send("<BHP:#>")
            command_buffer = ""

            while "\n" not in command_buffer:
                command_buffer += client_socket.recv(1024)

            response = run_command(command_buffer)
            client_socket.send(response)


def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:

        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:
            recv_len = 1

            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response
            buffer = raw_input("")

            buffer += "\n"

            client.send(buffer)
    except:
        print "[*] Exception exiting"

        client.close()


def server_loop():

    global target

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler,
                                         args=(client_socket,))
        client_thread.start()


def main():
    global target
    global listen
    global command
    global upload_destination
    global execute
    global port
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",
                                   ["help", "listen", "execute", "target",
                                    "port", "command", "upload"])
    except getopt.GetoptError as err:
        print err

    for option, argument in opts:
        if option in ("-h", "--help"):
            return
        elif option in ("-l", "--listen"):
            listen = True
        elif option in ("-e", "--execute"):
            execute = True
        elif option in ("-c", "--commandshell"):
            command = True
        elif option in ("-u", "--upload"):
            upload_destination = argument
        elif option in ("-t", "--target"):
            target = argument
        elif option in ("-p", "--port"):
            port = int(argument)
        else:
            assert False, "Unhandled Option"

    if not listen and len(target) and port > 0:
        buffer = "ls -la"

        client_sender(buffer)

    if listen:
        server_loop()


main()
