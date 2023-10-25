# echo-server
import socket
import threading
import time
import json
import os
from io import StringIO
import ctypes

from misc.logger import Logger
from src.frames import create_cams_threads
from misc.settings import SettingsIni

logger = Logger()

HOST = "0.0.0.0"
PORT = 8071

CAM_LIST = dict()
FRAMES_PATH = os.path.join(os.getcwd(), "frames\\")


def test_dir(frames_path) -> bool:
    """ Функция проверки папки куда сохраняются кадры """
    ret_value = True

    try:
        if not os.path.exists(frames_path):  # Если нет директории log_path пробуем её создать.
            os.makedirs(frames_path)
            print(f"Была создана директория куда сохранять кадры: {frames_path}")
    except Exception as ex:
        print(f"Ошибка при проверке/создании директории куда сохранять кадры: {ex}")
        ret_value = False

    return ret_value


# Таймер для тестов
def timer(func):
    start_time = time.time()

    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    print(f"Скорость обработки запроса: {time.time() - start_time} s.")
    return wrapper()


# Метод для обработки запроса по TCP
def read_port(conn, addr):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            str_data = data.decode("utf-8")

            try:
                json_data = json.load(StringIO(str_data))

                cam_name = f"cam{json_data['cam']}"

                try:
                    valid_frame = False
                    # Команда на запись кадра в файл
                    if CAM_LIST[cam_name].set_url_frame(f"{cam_name}_{json_data['data']}"):
                        valid_frame = CAM_LIST[cam_name].create_frame(logger)

                    if valid_frame:
                        logger.event(f"Успешно сохранен кадр: имя файла - {json_data['data']} камера - {cam_name}")
                    else:
                        logger.add_log(f"WARNING\tread_port\t"
                                       f"Не удалось сохранить кард: "
                                       f"имя файла - {json_data['data']} камера - {cam_name}")

                except Exception as ex:
                    logger.exception(f"Не удалось получить кадр из камеры: {ex}")

            except Exception as ex:
                logger.exception(f"Ошибка работы с данными в запросе: {ex}: {str_data}")

            logger.event(f"{data} - port:{addr}")
            conn.sendall(b"SUCCESS")


class ServerTCP:
    """ Сервер рассчитан на короткие соединения с малым объемом данных"""
    def __init__(self, host: str, port: int, logger_class: Logger):
        self.host = host
        self.port = port
        self.logger = logger_class

    def start(self):
        while True:
            self.logger.event(f"Открытие сокета: {self.host}:{self.port}")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ser:
                    ser.bind((self.host, self.port))
                    ser.settimeout(3)

                    ser.listen()
                    self.logger.event("Начало прослушивания порта...")
                    while True:
                        try:
                            # Создаем поток и продолжаем слушать порт
                            conn, addr = ser.accept()
                            tr = threading.Thread(target=read_port, args=[conn, addr])
                            tr.start()
                        except TimeoutError as ter:
                            pass
                        except OSError as oer:
                            self.logger.exception(f"Исключение: {oer}")
                        except Exception as wer:
                            self.logger.exception(f"Исключение: {wer}")
            except Exception as ex:
                self.logger.exception(f"Исключение: {ex}")


if __name__ == "__main__":
    set_ini = SettingsIni()

    if set_ini.create_settings() and test_dir(FRAMES_PATH):
        # Меняем имя терминала
        ctypes.windll.kernel32.SetConsoleTitleW(f"TCP ASTERISK CAM_API port: {set_ini.port()}")

        CAM_LIST = create_cams_threads(set_ini.cams(), logger)

        server = ServerTCP(set_ini.host(), set_ini.port(), logger)
        server.start()
    else:
        input()
