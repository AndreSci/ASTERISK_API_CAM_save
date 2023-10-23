import socket
import threading
import time
import json
from datetime import datetime


HOST = "127.0.0.1"
PORT = 8071


def client(cam_number: int):
    today = datetime.today()

    date_time = str(today.strftime("%Y-%m-%d_%H-%M"))
    dict_data = {"cam": cam_number, 'data': f"{date_time} {time.time()}"}

    json_str = json.dumps(dict_data).encode('utf-8')
    json_bytes = bytes(json_str)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cl:
        cl.connect((HOST, PORT))
        cl.sendall(json_bytes)
        data = cl.recv(1024)
        print(data)


if __name__ == "__main__":
    index = 1
    start_time = time.time()
    list_tr = []

    while index <= 20:
        index += 1
        tr = threading.Thread(target=client, args=[3, ])
        tr.start()
        time.sleep(0.05)
        list_tr.append(tr)

    for tr in list_tr:
        tr.join()

    print(f"Время работы: {time.time() - start_time} s.")