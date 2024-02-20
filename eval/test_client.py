import socket
import subprocess
import time
import sys
import inspect
import os
import math

# host = '127.0.0.1'
# port = 8080

def print_passed(msg):
    print("\033[92m" + msg + "\033[0m")


def print_failed(msg):
    print("\033[91m" + msg + "\033[0m")


def client_setup(host, port):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(server_socket)
    server_socket.settimeout(2)
    server_socket.bind((host, port))
    server_socket.listen(3)
    print(f"Server listening on port {host}:{port}")

    global processes
    global client_sockets
    global client_addresses 
    global names
    processes = []
    client_sockets = [0]*3
    client_addresses = [0]*3
    names = ["Aang", "Sokka", "Katara"]
    for i in range(0, 3):
        processes.append(subprocess.Popen(
        f"gcc ../impl/client.c -o client.out && ./client.out {host} {port} {names[i]}",
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        ))
        try:
            client_sockets[i], client_addresses[i] = server_socket.accept()
            data="NAME\n"
            client_sockets[i].sendall(data.encode())
            name = client_sockets[i].recv(1024).decode().strip("\x00")

            if name != names[i] + "\n":
                print_failed(f"client{i+1}_status: FAILED")
                raise ValueError(repr(names[i])+ " " + repr(name))
            print_passed(f"client{i+1}_status: SUCCESS")

        except (TimeoutError, ValueError) as e:
            print_failed(f"client_setup - 0.0/1.0")
            return 0

    print_passed(f"client_setup - 1.0/1.0")
    return 1

def test_cmds():
    total_marks = 2.
    token = 0
    connected_clients = 3
    loc = 0


    list_cmd = ["NOOP", "LIST", "MESG: CREATE FILE", "CALL", "EXIT", "LIST", "NOOP", "EXIT", "CALL", "MESG: DELETE FILE", "LIST", "EXIT"]
    noop_l = [0, 6]
    list_l = [1, 5, 10]
    exit_l = [4, 7, 11]
    mesg_l = [2, 9]
    invalid_l = [3, 8]
    exit_ans = ['INITIALIZING......\nENTER CMD: ENTER CMD: ENTER CMD: ENTER CMD: ENTER CMD: ENTER CMD: 1. Aang\nENTER CMD: CLIENT TERMINATED: EXITING......', 
                'INITIALIZING......\nENTER CMD: 1. Aang\n2. Sokka\n3. Katara\nENTER CMD: CLIENT TERMINATED: EXITING......', 
                'INITIALIZING......\nENTER CMD: ENTER CMD: 1. Aang\n2. Katara\nENTER CMD: CLIENT TERMINATED: EXITING......']
    score = 0.000
    try:
        while loc < len(list_cmd):
            data = "POLL\n"
            client_sockets[token].sendall(data.encode())
            processes[token].stdin.write(list_cmd[loc] + "\n")
            processes[token].stdin.flush()
            out = client_sockets[token].recv(1024).decode().strip("\x00")
            if out == "NOOP\n":
                if loc in noop_l:
                    score += .11111
            elif out == "EXIT\n":
                try:
                    output, _ = processes[token].communicate(timeout=2)
                    data = output.strip()
                    # print(repr(data))
                except subprocess.TimeoutExpired:
                    processes[token].kill()
                    print_failed(f"test_cmds - {round(score, 2)}/{total_marks}")
                    return score
                # print(repr(data))
                if data != exit_ans[token]:
                    raise ValueError()
            
                client_sockets[token].close()
                del(client_sockets[token])
                del(names[token])
                del(client_addresses[token])
                del(processes[token])
                del(exit_ans[token])

                # print(names)
                # print(client_addresses)
                # print(client_sockets)
            
                connected_clients -= 1
                token -= 1
                # print(connected_clients)
                if loc in exit_l:
                    score += 0.333333
        
            elif out == "LIST\n":
                ans = ""
                for j in range(0, connected_clients - 1):
                    ans += names[j] + ":"
                ans += names[connected_clients - 1] + "\n"
                client_sockets[token].sendall(ans.encode())

                if loc in list_l:
                    score += .1111111
            elif out[:5] == "MESG:":
                if loc in mesg_l and out == list_cmd[loc] + "\n":
                    score += .1111111
            else:
                if loc in invalid_l:
                    score += .1111111
            loc += 1
            if connected_clients:
                token = (token + 1)%connected_clients
            # print("token:", token)
            # print(score)
        server_socket.close()
        if round(score, 2) == total_marks:
            print_passed(f"test_cmds - {round(score, 2)}/{total_marks}")
        else:
            print_failed(f"test_cmds - {round(score, 2)}/{total_marks}")
        
        return score
    except Exception as e:
        print_failed(f"test_cmds - {round(score, 2)}/{total_marks}")
        return score
    

if __name__ == "__main__":
    ip = sys.argv[1]
    port = int(sys.argv[2])
    score1 = client_setup(ip, port)
    score2 = test_cmds()
    






