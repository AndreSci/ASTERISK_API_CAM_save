# echo-server
import datetime
import socket
import threading
import time
import json
from io import StringIO

from misc.logger import Logger
from src.frames import create_cams_threads
from misc.settings import SettingsIni

logger = Logger()

HOST = "0.0.0.0"
PORT = 8071

CAM_LIST = dict()


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
                    if CAM_LIST[cam_name].set_url_frame(f"{json_data['data']}"):
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

            # if str_data[:3] == 'CAM':
            #     res = str_data.split()
            #
            #     cam_name = 'cam' + cam_name[str_data.find(':') + 1:]
            #
            #     try:
            #         # Команда на запись кадра в файл
            #         if CAM_LIST[cam_name].set_url_frame(f"{}")
            #             valid_frame = CAM_LIST[cam_name].create_frame(logger)
            #
            #         if valid_frame:
            #             logger.event(f"Успешно сохранен кадр: время - {datetime.datetime.now()} камера - {cam_name}")
            #         else:
            #             logger.add_log(f"WARNING\tread_port\t"
            #                            f"Не удалось сохранить кард: - {datetime.datetime.now()} камера - {cam_name}")
            #
            #     except Exception as ex:
            #         logger.exception(f"Не удалось получить кадр из камеры: {ex}")
            #     print(res)

            logger.event(f"{data} - port:{addr}")
            conn.sendall(b"SUCCESS")


class ServerTCP:
    """ Сервер рассчитан на короткие соединения с малым объемом данных"""
    def __init__(self, host: str, port: int, logger_class: Logger, set_ini_class: SettingsIni):
        self.host = host
        self.port = port
        self.logger = logger_class
        # self.cameras = create_cams_threads(set_ini_class.cams(), logger_class)

    def start(self):
        while True:
            self.logger.event(f"Открытие сокета: {self.host}:{self.port}")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ser:
                    ser.bind((self.host, self.port))
                    ser.settimeout(1)

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

    if set_ini.create_settings():
        CAM_LIST = create_cams_threads(set_ini.cams(), logger)

        server = ServerTCP(set_ini.host(), set_ini.port(), logger, set_ini)
        server.start()
    else:
        input()
