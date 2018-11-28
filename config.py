import json
import os
import argparse

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILES = os.path.join(THIS_FOLDER, 'config.json')


def set_config():
    dictionary = {}
    description = ('Токен ютуба ', 'Токен вк ', 'Токен дисокрда ')
    values_1 = []
    for i in range(len(description)):
        try:
            values_1.append(input(description[i],))
        except ValueError as err:
            print('nothing')
            values_1.append(None)    # чтобы полюбому добавили токен = while not y: y = input(), но надо доработать
            continue
    keys_1 = ('TOKEN_YOUTUBE', 'TOKEN_VK', 'DISCORD_TOKEN')
    for i in range(len(keys_1)):
        if values_1[i]:         # если значения нет, то ключ не создается, поменять
            dictionary[keys_1[i]] = values_1[i]

    return dictionary


def check_config():
    if not os.path.exists(CONFIG_FILES):
        with open(CONFIG_FILES, 'wt') as file:
            file.write(json.dumps(set_config()))
    else:
        with open(CONFIG_FILES, 'rt') as file:
            return json.load(file)


def edit_config():
    print('1')
    conf = check_config()
    print(conf)
    for i in conf.keys():
        new = input('Введите новое значение токена ',)
        if new:
            conf[i] = new
        print('Новое значение ', i, ' : ', conf[i])
    with open(CONFIG_FILES, 'wt') as file:
        file.write(json.dumps(conf))


def config_options():

    parser = argparse.ArgumentParser(description='Управление config.json, содержащего токены для бота')
    parser.add_argument('-e', '--edit', action = 'store_true', help='Функция для редактирования config.json')
    args = parser.parse_args()
    return args

def main():
    opt = config_options()
    if opt.edit:
        edit_config()
    else:
        check_config()

main()