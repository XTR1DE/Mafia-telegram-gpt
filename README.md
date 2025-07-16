# AI Mafia Telegram Bot

# Описание.

Этот Telegram-бот реализует игру "Мафия", в которой роли игроков исполняют нейросети. Бот управляет ходом игры, назначает роли и использует AI для генерации действий и ответов игроков.

## Возможности игры.

1. •   Автоматическое распределение ролей (мафия, шериф, мирные жители).
2. •   AI-управляемые игроки, принимающие решения на основе заданных ролей и текущей ситуации в игре.
3. •   Поддержка различных сценариев игры.
4. •   Логирование действий и результатов игры.

## Библиотеки .py .

1. •   **Telebot (pyTelegramBotAPI):** Библиотека для создания Telegram-ботов.
2. •   **g4f:** Библиотека для доступа к различным языковым моделям.
3. •   **python-dotenv:** Библиотека для управления конфигурационными параметрами из файла `.env`.

## Установка зависимостей.

1. • pip install -U g4f[all]
2. • pip install pyTelegramBotAPI
3. • pip install python-dotenv


## Настройка и запуск.

1. • Создайте файл .env в корне проекта.
2. • Добавьте ваш токен Telegram бота, полученный у BotFather:
		TG_TOKEN=ваш_токен
```.env
TG-TOKEN = "Ваш токен, полученный от BotFather"
```

4. • Запустите бота:
5. • В Telegram напишите /start, чтобы начать взаимодействие.


## Настройка сцен и нейросетей.

2. • Для добавления или изменения сцен редактируйте файл Mafia/game.py в функции scene_update().
```python
    def scene_update(self):
        self.scene = {
            'Участники': f"В игре участвуют {len(self.names)} игроков: {', '.join(self.names)}. Из них затаились {len(self.mafia)} мафии. Вам предстоит найти их. Представьтесь пожалуйста.",
            'Ночь мафии': 'Начинается ночь, город засыпает, просыпается мафия, мафия выбирает кого убить',
            "Выбор мафии": f"Мафия сделала выбор",
            'Ночь шерифа': 'Мафия засыпает. Просыпается шериф выбирает кого он хочет проверить',
            'Выбор шерифа': f'Шериф сделал выбор, шериф засыпает. Наступает новый день, город просыпается, кроме {self.kills}',
            'Обсуждение': 'Обсуждение',
            'Обсуждение2': 'Продолжаем обсуждение. Последний раунд перед голосованием.',

	    'Обсуждение3': "Подводите итоги, кого хотите кикнуть", # <---- Можно добавлять или удалять сцены

            'Голосование': 'Обсуждение закончилось, начинает голосование, все игроки обязаны назвать имя игрока. Игрок, набравший большинство голосов выбывает.',
            'Конец голосование': f'Голосование закончилось, игрок {self.kicked} Выбывает из игры. Он был - {self.kicked_role}',
        }
```
4. • Если хотите более живую игру, то следует выбрать более сильную нейросеть. Для изменения используемой нейросети редактируйте файл Mafia-telegram-gpt-only/GPT_Requests/request_gpt.py.
```python
def gpt(message: str, context: str, prompt: str, provider = g4f.Provider.Chatai, model="gpt-4o"):
    try:
        full_prompt = f"{context}\n{prompt}\n{message} Не пиши слишком большие сообщения."
        response = g4f.ChatCompletion.create(
            provider=provider, # <--- Здесь можете подобрать более подходящий провайдер. Используйте документацию от библиотеки g4f
            model=g4f.models.default, # <--- Здесь можете выбрать модель нейросети.  Используйте документацию от библиотеки g4f
            stream=False,
            messages=[
                {"role": "assistant", "content": full_prompt},
                {"role": "user", "content": f"{message}"},
            ],
        )
        return response
    except Exception as e:
        print(e)
        return "None"
```
5. • Если хотите использовать оригинальный GPT API, адаптируйте функцию gpt() под нужный API, сохранив входные и выходные переменные. Пример для OpenAi и gemini
   
## Пример для OpenAi

```python
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

def gpt(message: str, context: str, prompt: str, provider=None, model=None): # <--- Входные данные должны быть, как и в начальном виде
    try:
        client = OpenAI(api_key=os.getenv("GPT-TOKEN")) # <--- Загрузить api key добавить в .env GPT-TOKEN = "Ваш токен от openai"
        full_prompt = f"{context}\n{prompt}\n{message} Не пиши слишком большие сообщения."

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "assistant", "content": full_prompt},
                {"role": "user", "content": message},
            ],
        )
        return completion.choices[0].message.content # <--- Выходящий ответ должен быть ответ gpt : str
    except Exception as e:
        print(e)
        return "None"
```

## Пример для Gemini
 
```python
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

def gpt(message: str, context: str, prompt: str, provider=None, model=None): # <--- Входные данные должны быть, как и в начальном виде
    try:
        full_prompt = f"{context}\n{prompt}\n{message}. Не пиши очень длинные сообщение."

        genai.configure(api_key=os.getenv("GPT-TOKEN")) # <--- Загрузить api key добавить в .env GPT-TOKEN = "Ваш токен от gemini"

        model = genai.GenerativeModel('models/gemini-1.5-flash')

        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        print(e)
        return "None"
```

## Для более живой игры использовать варианты с Gemini(Есть бесплатный план) и OpenAi(Платная)

##
## by XTR1DE
## Telegram -> @XTR1DE
## Email -> xtreamd034@gmail.com
