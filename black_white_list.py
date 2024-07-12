import os
import sys
import ctypes
from datetime import datetime

PREFETCH_DIR = os.path.join(os.getenv('WINDIR'), 'Prefetch')
OUTPUT_FILE = 'result.txt'


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        return e


def read_list(file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            return [line.strip().upper() for line in file if line.strip()]
    except IOError as e:
        return e


def get_prefetch_files():
    try:
        return [f for f in os.listdir(PREFETCH_DIR) if f.endswith('.pf')]
    except WindowsError as e:
        return e


def parse_date(file_name):
    PATTERN = "%Y-%m-%d %H:%M:%S"
    full_path = os.path.join(PREFETCH_DIR, file_name)
    try:
        last_executed = os.path.getmtime(full_path)
        last_executed = datetime.strftime(datetime.fromtimestamp(last_executed), PATTERN)
        return last_executed
    except WindowsError as e:
        return e


def check_software(software_list, prefetch_files, check_type):
    results = []
    for pf in prefetch_files:
        if ".EXE" in pf:
            file_name = pf.split("-")[0]
            if check_type == 'белый список':
                if file_name in software_list:
                    results.append((file_name, parse_date(pf)))
                results.append((file_name, "<b>{0}<\b>".format(parse_date(pf))))
            elif check_type == 'черный список':
                if file_name in software_list:
                    results.append((file_name, "<b>{0}<\b>".format(parse_date(pf))))
                results.append((file_name, parse_date(pf)))

    return set(sorted(results, key=lambda x: x[0].lower()))


def write_results(results, status):
    with open(OUTPUT_FILE, 'w', encoding="utf-8") as file:
        for name, date in results:
            file.write('{0} | {1}'.format(name, date)+"\n")
        file.write('\nСтатус: {0}'.format(status))


def main():
    white_list = read_list("white_list.txt")
    black_list = read_list("black_list.txt")

    check_type = "Черный Список".lower()

    prefetch_files = get_prefetch_files()
    status = "не соответствует"
    results = check_software(white_list,
                             prefetch_files,
                             check_type)

    if check_type == "белый список":
        if all(map(lambda x: x[0] in white_list, results)):
            status = "соответствует"
        else:
            status = "не соответствует"
    elif check_type == "черный список":
        if any(map(lambda x: x[0] in black_list, results)):
            status = "не соответствует"
        else:
            status = "соответствует"
    write_results(results, status)
    print("Результаты сохранены в {0}".format(OUTPUT_FILE))

if __name__ == '__main__':
    # if is_admin():
    #     main()
    # else:
    #     ctypes.windll.shell32.ShellExecuteW(
    #         None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
    main()