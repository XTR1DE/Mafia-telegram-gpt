import json


def DataCreate(name, role, prompt : dict, mafias = None):
    try:
        data = json.load(open('info.json', encoding='utf8'))
        for i in data['personal']:
            if name == i['name']:
                print(f"уже добавлен - {name}")
                return
        data['personal'].append(
            {
            'name': name,
            'role': role,
            'status': 'play',
            'prompt': f"тебя зовут {name}. Ты играешь в игру 'мафия'. Вот правила игры. Не нарушай их." + prompt["all"] + prompt[role] + f"{f"Твои напарники: {",".join(mafias)}" if mafias is not None else ""}",
            'history': [],
            }
        )
        with open('info.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except Exception(FileNotFoundError):
        createjson()
        DataCreate(name, role, prompt, mafias)


def check_info(name, _type):
    data = json.load(open('info.json', encoding='utf8'))
    for i in data['personal']:
        if name == i['name']:
            if _type in ['role', 'history', 'status', 'prompt']:
                return i[_type]
            else:
                print(f"Ошибка: {_type} нет в списке")

def change_status(name, status):
    data = json.load(open('info.json', encoding='utf8'))
    for i in data['personal']:
        if name == i['name']:
            i['status'] = status
    with open('info.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def addhistory(name, message, scene = None):
    data = json.load(open('info.json', encoding='utf8'))
    for i in data['personal']:
        if name == i['name']:
            i['history'].append(message)

    for i in data['personal']:
        if i['name'] != name and i['status'] == 'play' and i['role'] != 'system':
            if scene not in ["Ночь мафии", "Ночь шерифа", "Ночь доктора"]:
                i['history'].append(f"{name}: {message}")
            else:
                i['history'].append(f"{scene}: Кто-то выполнил действие.")
    with open('info.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def clear():
    data = {
        "personal": [

        ]
    }
    with open('info.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def createjson():
    data = {
        "personal": [

        ]
    }
    with open('info.json', 'w+', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)