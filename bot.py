import telebot
import os
from dotenv import load_dotenv
from Mafia.game import Mafia
from config import _names, _russian_roles
from GPT_Requests.prompts import _prompts

load_dotenv()
TG = os.getenv("TG-TOKEN")
bot = telebot.TeleBot(TG)

_mafia: Mafia = None
_chat_id: int = None


@bot.message_handler(content_types=['text'])
def handle_message(message):
    global _mafia, _chat_id
    if message.text == "/start":
        _chat_id = message.chat.id
        _mafia = Mafia(_prompts, _names, send_message_callback=lambda name, role, message: send_message(name, role, message))
        _mafia.run()


def send_message(name, role, message):
    role_name = _russian_roles[role]
    bot.send_message(
        _chat_id,
        f"*{name}* | *{role_name}*\n\n{message}",
        parse_mode="Markdown",
    )


def main():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()