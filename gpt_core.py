import openai
import os


OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY
CHAT_HISTORY_DIR = "chat_history"

def load_instructions(file_path="instructions.txt"):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        raise FileNotFoundError(f"Файл с инструкциями '{file_path}' не найден.")
GPT_INSTRUCTIONS = load_instructions()
def get_chat_history(user_id, CHAT_HISTORY_DIR):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{user_id}.txt")
    with open(file_path, "r", encoding="utf-8") as f:
        old_lines = f.readlines()
    full_text=''.join(old_lines)
    return full_text

def gpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": GPT_INSTRUCTIONS},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.6,
            top_p=0.9,
            frequency_penalty=0.2,
            presence_penalty=0.3,
        )
        return response["choices"][0]["message"]["content"].strip()
    except openai.error.OpenAIError as e:
        return f"Ошибка OpenAI API: {e}"
    except Exception as e:
        return f"Произошла ошибка при обработке запроса: {e}"

def save_message(user_id, new_message, name_object, max_length=1024):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{user_id}.txt")

    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            old_lines = f.readlines()
            print(len(old_lines))
    else:
        old_lines = []

    
    old_lines.append(name_object + ':' + new_message +'\n')
    
    
    while len(old_lines) > 20 and old_lines:
        old_lines.pop(0)
        
    
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(old_lines)   
    f.close()
