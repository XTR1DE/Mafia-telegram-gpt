import g4f
from g4f import Provider


def gpt(message: str, context: str, prompt: str, provider = g4f.Provider.Chatai, model="gpt-4o"):
    try:
        full_prompt = f"{context}\n{prompt}\n{message} Не пиши слишком большие сообщения."
        response = g4f.ChatCompletion.create(
            provider=provider,
            model=g4f.models.default,
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