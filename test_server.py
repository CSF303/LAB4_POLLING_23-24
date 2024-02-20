import socket
import subprocess
import time
import sys
import inspect
import os
from threading import Thread
from threading import Lock

list_cmd = ["NOOP", "LIST", "MESG: CREATE FILE", "CALL", "EXIT", "LIST", "NOOP", "EXIT", "CALL", "MESG: DELETE FILE", "LIST", "EXIT"]
loc = 0
names = ["Aang", "Sokka", "Katara"]
names_index = 0
order = []
mutex_lock = Lock()

def print_passed(msg):
    print("\033[92m" + msg + "\033[0m")


def print_failed(msg):
    print("\033[91m" + msg + "\033[0m")


def client(ip, port, thread_no):
    global loc 
    global list_cmd
    global order
    global names_index
    global mutex_lock
    score = 0
    server_ip = ip
    server_port = port

    try:
        server_addr = (server_ip, server_port)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with mutex_lock:
            client_socket.connect(server_addr)
            name = names[names_index]
            names_index += 1

        client_buffer = client_socket.recv(1024).decode().strip("\x00")

        if client_buffer != "NAME\n":
            # print("CONNECTION FAILED: EXITING......")
            client_socket.close()
            sys.exit(1)

        client_socket.sendall(name.encode())
        while True:
            client_buffer = client_socket.recv(1024).decode().strip("\x00")
            # print(repr(client_buffer))
            if client_buffer != "POLL\n":
                # print("INVALID MESSAGE: EXITING......")
                client_socket.close()
                # time.sleep(1)
                sys.exit(1)

            # print("ENTER CMD")
            client_buffer = list_cmd[loc]
            order += [name]
            loc += 1

            if client_buffer == "EXIT":
                client_socket.sendall(client_buffer.encode() + b'\n')
                # print("CLIENT TERMINATED: EXITING......")
                client_socket.close()
                sys.exit(0)
            else:
                client_socket.sendall(client_buffer.encode() + b'\n')

                if client_buffer == "LIST":
                    client_buffer = client_socket.recv(1024).decode().strip("\x00")
                    # print(client_buffer)
                elif client_buffer.startswith("MESG:") or client_buffer == "NOOP":
                    pass
    except Exception as e:
        print_failed("CLIENT PROCESS FAILED")
        sys.exit(1)

def server_setup(host, port):
    global server_p
    global names
    global cmds
    server_p = subprocess.Popen(
        f"gcc server.c -o server.out && ./server.out {host} {port}",
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        )
    time.sleep(2)
    threads = []
    for n in range(3):
        t = Thread(target=client, args=(host, port, n))
        t.start()
        threads.append(t)

    for t in threads:
        t.join(15.)
    score = 0
    right_order = ['Aang', 'Sokka', 'Katara', 'Aang', 'Sokka', 'Katara', 'Aang', 'Katara', 'Aang', 'Aang', 'Aang', 'Aang']
    if order == right_order:
        print_passed("polling_test - 2.0/2.0")
        score += 2
    else:
        print_failed("polling_test - 0.0/2.0")

    return score

def server_msg():
    score = 0
    global server_p
    try:
        output, _ = server_p.communicate(timeout=2)
        # print(repr(output))
        out = 'Katara: CREATE FILE\nINVALID CMD\nINVALID CMD\nAang: DELETE FILE\nSERVER TERMINATED: EXITING......'
    except subprocess.TimeoutExpired:
        server_p.kill()
    # print(repr(output.strip()))
    if output.strip() == out:
        print_passed("server_msg - 1.0/1.0")
        score += 1
    else:
        print_failed("server_msg - 0.0/1.0")
    del(server_p)
    return score


if __name__ == "__main__":
    try:
        score = 0
        total_marks = 3.
        ip = sys.argv[1]
        port = int(sys.argv[2])
        score += server_setup(ip, port)
        score += server_msg()
        exit(score) 
    except Exception as e:
        exit(score)