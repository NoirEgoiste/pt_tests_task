import os
import re
import sys
import ctypes
from datetime import datetime

SOFTWARE_LIST = [
    'DOCKER.EXE',
    'DWM.EXE',
    'WSL.EXE'
]
COMPARE_TYPE = 'Белый список'
# COMPARE_TYPE = 'Черный список'
PREFETCH_DIR = os.path.join(os.getenv('WINDIR'), 'Prefetch')
OUTPUT_FILE = 'result.txt'
FILE_PATTERN = re.compile(r'(?P<file_name>[\w\d]+\.EXE)-.*\.pf')
DATE_PATTERN = "%Y-%m-%d %H:%M:%S"
FILE_OK_TEMPLATE = '{software:<30} | {date}'
FILE_NOT_OK_TEMPLATE = '{software:<30} | <b>{date}<\\b>'


def is_admin():
    """
    Проверяет, запущена ли программа с правами администратора.

    :return: True, если программа запущена с правами администратора, иначе False.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        raise False


def get_date(file_):
    """
    Получает дату последнего изменения файла.

    :param file_: Имя файла.
    :return: Дата последнего изменения в формате 'YYYY-MM-DD HH:MM:SS'.
    """
    try:
        full_path = os.path.join(PREFETCH_DIR, file_)
        last_executed = os.path.getmtime(full_path)
        last_executed = datetime.strftime(datetime.fromtimestamp(last_executed), DATE_PATTERN)
        return last_executed
    except WindowsError as e:
        print('Функция {func_name} Ошибка'.format(func_name=get_date.__name__), e)


def get_info_prefetch_files():
    """
    Получает информацию о файлах в папке Prefetch.

    :return: Словарь с информацией о файлах Prefetch.
    """
    file_mapping = {}

    try:
        for file_ in os.listdir(PREFETCH_DIR):
            name_match = FILE_PATTERN.match(file_)
            if name_match:
                file_mapping[name_match.group()] = {
                    'name': name_match.group('file_name'),
                    'date': get_date(file_)
                }
        return file_mapping
    except WindowsError as e:
        print('Функция {func_name} Ошибка'.format(func_name=get_info_prefetch_files.__name__), e)


def list_check(file_mapping):
    """
    Проверяет файлы Prefetch на соответствие белому или черному списку.

    :param file_mapping: Словарь с информацией о файлах Prefetch.
    :return: Кортеж из булевого значения (соответствие списку) и отсортированного списка результатов.
    """
    result_list = []
    check = False
    try:
        all_file_names = set(map(lambda x: x['name'], file_mapping.values()))

        for file_info in file_mapping.values():
            if COMPARE_TYPE == 'Белый список':
                check = True if all_file_names.issubset(set(SOFTWARE_LIST)) else False
                template = FILE_OK_TEMPLATE if file_info['name'] in SOFTWARE_LIST else FILE_NOT_OK_TEMPLATE
            else:
                check = False if all_file_names.intersection(set(SOFTWARE_LIST)) else True
                template = FILE_NOT_OK_TEMPLATE if file_info['name'] in SOFTWARE_LIST else FILE_OK_TEMPLATE

            result_list.append(
                template.format(
                    software=file_info['name'],
                    date=file_info['date']
                )
            )
        return check, sorted(result_list)
    except (AttributeError, TypeError) as e:
        print('Функция {func_name} Ошибка'.format(func_name=list_check.__name__), e)

def main():
    try:
        file_mapping = get_info_prefetch_files()
        check, result_file_list = list_check(file_mapping)

        with open(OUTPUT_FILE, 'w', encoding="utf-8") as file:
            for file_info in result_file_list:
                file.write(file_info + '\n')

        if check:
            print('Соответствует')
            return
        print('Не соответствует')
    except Exception as e:

        print('Функция {func_name} Ошибка'.format(func_name=main.__name__), e)


if __name__ == '__main__':
    if is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,
                                            " ".join(sys.argv), None, 1)