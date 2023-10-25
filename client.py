import socket
import time
import json
import threading
import os
import datetime
import inspect
import traceback

# Данные для logger
LOGGER_PATH = os.path.join(os.getcwd(), "logs_tcp\\")


class BColors:
    """ Класс вариантов цвета для текста в консоли """
    col_header = '\033[95m'
    col_okblue = '\033[94m'
    col_okcyan = '\033[96m'
    col_okgreen = '\033[92m'
    col_warning = '\033[93m'
    col_fail = '\033[91m'
    col_endc = '\033[0m'
    col_bold = '\033[1m'
    col_underline = '\033[4m'


def test_dir(log_path) -> bool:
    """ Функция проверки папки куда сохраняются логи """
    ret_value = True

    try:
        if not os.path.exists(log_path):  # Если нет директории log_path пробуем её создать.
            os.makedirs(log_path)
            print(f"{BColors.col_warning}Была создана директория для лог-фалов:{BColors.col_endc} {log_path}")
    except Exception as ex:
        print(f"Ошибка при проверка/создании директории лог файлов: {ex}")
        ret_value = False

    return ret_value


class SingletonBaseClass(type):
    """ Шаблон сингелтон (объяви один раз и пользуйся во всей программе одним экземпляром)"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonBaseClass, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class Logger(metaclass=SingletonBaseClass):
    """ Класс вывода данных в консоль и запись в файл """
    def __init__(self, log_path: str = None):
        self.font_color = False
        self.log_guard = threading.Lock()
        if log_path:
            global LOGGER_PATH
            LOGGER_PATH = log_path

    def add_log(self, text: str, print_it=True):
        """ Обшивает текст датой, табуляцией и переходом на новую строку """
        ret_value = False
        try:
            today = datetime.datetime.today()

            for_file_name = str(today.strftime("%Y-%m-%d"))

            date_time = str(today.strftime("%Y-%m-%d/%H.%M.%S"))
            # Создаем лог
            mess = date_time + "\t" + text + "\n"

            if test_dir(LOGGER_PATH):

                with self.log_guard:  # Защищаем поток

                    if print_it:
                        if 'ERROR' == text[:5]:
                            print(f"{BColors.col_fail}{date_time}\t{text}{BColors.col_endc}")
                        elif 'WARNING' == text[:7]:
                            print(f"{BColors.col_warning}{date_time}\t{text}{BColors.col_endc}")
                        else:
                            print(date_time + "\t" + text)

                    # Открываем и записываем логи в файл отчета.
                    with open(f'{LOGGER_PATH}{for_file_name}.log', 'a', encoding='utf-8') as file:
                        file.write(mess)
                        ret_value = True
        except Exception as ex:
            print(f"{BColors.col_warning}"
                  f"EXCEPTION\tLOGGER.add_log\tИсключение в работе регистрации события в файл: {ex}"
                  f"{BColors.col_endc}")

        return ret_value

    def __rebuild_msg(self, text: str, print_it=True, type_mess="INFO", current_frame=inspect.currentframe()):
        """ Метод изменяет текст в стандартный стиль """

        # получи фрейм объект, который его вызвал
        caller_frame = current_frame.f_back

        # возьми у вызвавшего фрейма исполняемый в нём объект типа "код" (code object)
        code_obj = caller_frame.f_code

        # и получи его имя
        code_obj_name = code_obj.co_name

        return self.add_log(f"{type_mess}\t{code_obj_name}\t{text}", print_it)

    def event(self, text: str, print_it=True):
        """ Метод изменяет текст в стандартный стиль """
        # возьми текущий фрейм объект (frame object)
        current_frame = inspect.currentframe()
        return self.__rebuild_msg(text, print_it, "EVENT", current_frame)

    def warning(self, text: str, print_it=True):
        """ Метод изменяет текст в стандартный стиль """
        # возьми текущий фрейм объект (frame object)
        current_frame = inspect.currentframe()
        return self.__rebuild_msg(text, print_it, "WARNING", current_frame)

    def error(self, text: str, print_it=True):
        """ Метод изменяет текст в стандартный стиль """
        # возьми текущий фрейм объект (frame object)
        current_frame = inspect.currentframe()
        return self.__rebuild_msg(text, print_it, "ERROR", current_frame)

    def exception(self, text: str, print_it=True):
        """ Метод изменяет текст и указывает где была вызвана ошибка(traceback) """
        # возьми текущий фрейм объект (frame object)
        current_frame = inspect.currentframe()

        # получи фрейм объект, который его вызвал
        caller_frame = current_frame.f_back

        # возьми у вызвавшего фрейма исполняемый в нём объект типа "код" (code object)
        code_obj = caller_frame.f_code

        # и получи его имя
        code_obj_name = code_obj.co_name

        return self.add_log(f"EXCEPTION\t{code_obj_name}\t{text} - {traceback.format_exc()}", print_it)


HOST = "192.168.15.10"
PORT = 8071

logger = Logger()


def client(cam_number: int):

    ret_value = False
    # Получаем дату и время
    today = datetime.datetime.today()
    date_time = str(today.strftime("%Y-%m-%d_%H-%M"))

    # Приобразуем словарь с данными в байт-строку
    dict_data = {"cam": cam_number, 'data': f"{date_time} {time.time()}"}
    json_str = json.dumps(dict_data).encode('utf-8')
    json_bytes = bytes(json_str)

    try:
        # Отправляем данные по TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cl:
            cl.settimeout(2)
            # Подключаемся
            cl.connect((HOST, PORT))
            # Отправляем данные
            cl.sendall(json_bytes)
            # Ждем ответ
            data = cl.recv(1024)

            if data == b'SUCCESS':
                ret_value = True
    except TimeoutError as tex:
        logger.exception(f"Исключение по времени ответа: {tex}")
    except Exception as ex:
        logger.exception(f"Неизвестная ошибка: {ex}")

    return ret_value


def main(cam_number=1):
    # Замеряем время исполнения скрипта
    start_time = time.time()

    if client(cam_number):
        logger.event(f"Успешно отправлен запрос на сохранениe кадра")
    else:
        logger.error(f"Не удалось отправить запрос на сохранениe кадра... камера: {cam_number}")

    logger.event(f"Время работы: {time.time() - start_time} s.", print_it=False)

    return True


def speed_test():
    # Замеряем время исполнения скрипта
    start_time = time.time()

    cam_number = 3
    index = 1
    list_tr = []
    # Тесты скорости работы
    while index <= 1:
        index += 1
        tr = threading.Thread(target=client, args=[cam_number, ])
        tr.start()
        time.sleep(0.05)
        list_tr.append(tr)

    for tr in list_tr:
        tr.join()

    logger.event(f"Время работы: {time.time() - start_time} s.", print_it=False)
    return True


if __name__ == "__main__":
    main(input("Укажите порядковый номер камеры из settings.ini файл: "))
    input()
