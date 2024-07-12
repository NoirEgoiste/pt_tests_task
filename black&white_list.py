import os
from datetime import datetime


PREFETCH_DIR = os.path.join(os.getenv('WINDIR'), 'Prefetch')
OUTPUT_FILE = 'result.txt'

def read_list(file_path):
    with open(file_path, 'r') as file:
        return [line.strip().upper() for line in file if line.strip()]


def get_prefetch_files():
    try:
        return [f for f in os.listdir(PREFETCH_DIR) if f.endswith('.pf')]
    except PermissionError as e:
        return print(e)


def parse_date(file_name):
    PATTERN = "%Y-%m-%d %H:%M:%S"
    full_path = os.path.join(PREFETCH_DIR, file_name)
    last_executed = os.path.getmtime(full_path)
    last_executed = datetime.strftime(datetime.fromtimestamp(last_executed), PATTERN)
    return last_executed

def check_software(software_list, prefetch_files, check_type):
    results = []
    for pf in prefetch_files:
        if ".EXE" in pf:
            file_name = pf.split("-")[0]
            if check_type == 'white_list.txt':
                if file_name in software_list:
                    results.append((file_name, parse_date(pf)))
                else:
                    results.append(('<b>{0}</b>'.format({file_name}), parse_date(pf)))
            elif check_type == 'blacklist.txt':
                if file_name not in software_list:
                    results.append((file_name, parse_date(pf)))
                else:
                    results.append(('<b>{0}</b>'.format(file_name), parse_date(pf)))
    return sorted(results, key=lambda x: x[0].lower())

def write_results(results, status):
    with open(OUTPUT_FILE, 'w') as file:
        for name, date in results:
            file.write('{0} | {1}\n'.format(name, date))
        file.write('\nСтатус: {0}'.format(status))

def main():
    software_list_file = "files.txt"# input("Введите путь к файлу со списком ПО например files.txt: ")
    check_type = "white_list.txt"# input("Введите тип проверки (Белый список/Черный список): ")
    if check_type.lower() == 'белый список':
        check_type = "white_list.txt"
    elif check_type.lower() == "черный список":
        check_type = "black_list.txt"
    # else:
    #     print("Введите Белый список или Черный список")

    software_list = read_list(software_list_file)
    #print(software_list)
    prefetch_files = get_prefetch_files()
    #print(prefetch_files)
    status = 'не соответствует'

    if not prefetch_files:
        status = 'не соответствует'
        results = []
    else:
        results = check_software(software_list, prefetch_files, check_type)
        if check_type == 'Белый список':
            status = 'соответствует' if all('<b>{0}</b>'.format(name) not in result[0] for result in results) else 'не соответствует'
        elif check_type == 'Черный список':
            status = 'соответствует' if all('<b>{0}</b>'.format(name) not in result[0] for result in results) else 'не соответствует'
    #print(status)
    print(results)
    write_results(results, status)
    print('Результаты сохранены в {0}'.format(OUTPUT_FILE))

if __name__ == '__main__':
    main()
