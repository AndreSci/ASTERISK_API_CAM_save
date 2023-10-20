import os
import configparser
import datetime
import traceback


class SettingsIni:
    """ Класс управления данными настройки """
    def __init__(self):
        # general settings
        self.settings_ini = dict()
        self.settings_file = configparser.ConfigParser()

    def create_settings(self) -> bool:
        """ Функция получения настройки из файла settings.ini. """

        error_mess = 'Успешная загрузка данных из settings.ini'

        ret_value = False

        # проверяем файл settings.ini
        if os.path.isfile("settings.ini"):
            try:
                self.settings_file.read("settings.ini", encoding="utf-8")
                # general settings ----------------------------------------
                self.settings_ini["log_path"] = os.path.join(os.getcwd(), 'logs')

                # подгружаем все доступные камеры
                self.settings_ini['CAMS'] = self.settings_file["CAMS"]

                # Получаем данные сервера
                self.settings_ini['HOST'] = str(self.settings_file['GEN'].get('HOST'))
                self.settings_ini['PORT'] = int(self.settings_file['GEN'].get('PORT'))

                ret_value = True

            except KeyError as ex:
                error_mess = f"Не удалось найти поле в файле settings.ini: {ex} {traceback.format_exc()}"

            except Exception as ex:
                error_mess = f"Не удалось прочитать файл: {ex} {traceback.format_exc()}"
        else:
            error_mess = "Файл settings.ini не найден в корне проекта"

        today = datetime.datetime.today()
        date_time = str(today.strftime("%Y-%m-%d/%H.%M.%S"))

        print(f"{date_time}\t{ret_value}\t{error_mess}")

        return ret_value

    def take_settings(self):
        return self.settings_ini

    def log_path(self):
        return self.settings_ini["log_path"]

    def host(self):
        return self.settings_ini.get("HOST")

    def port(self):
        return self.settings_ini.get("PORT")

    def cams(self):
        return self.settings_ini.get("CAMS")
