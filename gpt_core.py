import openai
import os
import re


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

def save_message(user_id, new_message, name_object):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{user_id}.txt")

    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            old_lines = f.readlines()
            
    else:
        old_lines = []
    
    new_text = ''.join(name_object + ':' + new_message)
    new_text = new_text.replace('\t', ' ')
    new_text = new_text.replace('\n',' ')
    new_text = re.sub(' +', ' ', new_text)
    new_text = new_text.strip()

    old_lines.append(new_text + '\n')
    
    
    while len(old_lines) > 20 and old_lines:
        old_lines.pop(0)
        
    
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(old_lines)   
    f.close()


    print('raw_text:', raw_text)
        parsed = json.loads(raw_text)
        print('parsed:', raw_text)
        answer = parsed["text"]
        print(str(answer)[1:])
