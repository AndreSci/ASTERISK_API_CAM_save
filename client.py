import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 8071


def client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cl:
        cl.connect((HOST, PORT))
        cl.sendall(b"CAM 1")
        data = cl.recv(1024)
        print(data)


if __name__ == "__main__":
    index = 1
    start_time = time.time()
    list_tr = []

    while index <= 1:
        index += 1
        tr = threading.Thread(target=client)
        tr.start()
        list_tr.append(tr)

    for tr in list_tr:
        tr.join()

    print(f"Время работы: {time.time() - start_time} s.")