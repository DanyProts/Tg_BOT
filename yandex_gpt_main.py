from __future__ import annotations
import json
from yandex_cloud_ml_sdk import YCloudML
import os
import re

CHAT_HISTORY_DIR = "chat_history"
sdk = YCloudML(
        folder_id="b1g2oescfm94htet8scd",
        auth="AQVN3XVL4eptS3BwbBiR_18NhzRhWnnDihNLBqoH",
    )

model = sdk.models.completions("yandexgpt")
def yandex_gpt(user_id,rag_info):

    messages_1 = get_dialog(user_id)
    
    system_insruct = {
        "role": "system",
        "text":  f"ТЫ ВИРТУАЛЬНЫЙ АССИСТЕНТ ПРИЕМНОЙ КОМИССИИ МГТУ ИМ. Н.Э.БАУМАНА. НИКОГДА НЕ ФОРМИРУЙ ОТВЕТ В JSON ФОРМАТЕ,ТОЛЬКО ЧИСТЫЙ ТЕКСТ, КАК БУДТО ПИШЕШЬ СООБЩЕНИЯ В ТЕЛЕГРАММ. ТЫ ОБЩАЕШЬСЯ ОТ ЛИЦА СОТРУДНИКА УНИВЕРСИТЕТА И ПОМОГАЕШЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ ПРО УНИВЕРСИТЕТ, КОНКРЕТНО ПО ВОПРОСАМ, СВЯЗАННЫМИ С ПОСТУПЛЕНИЕМ, НАПРАВЛЕНИЯМИ, ПРЕДСТАВЛЕННЫМИ В УНИВЕРСИТЕТЕ, И ПРЕДПРИЯТИМИ СОТРУДНИЧАЮЩИМИ С НИМ. СТИЛЬ ОБЩЕНИЯ: НЕ НАДО ЗДОРОВАТЬСЯ С ПОЛЬЗОВАТЕЛЕМ, ОБЩАТЬСЯ НАДО ДРУЖЕЛЮБНО, ЕСЛИ НЕ УВЕРЕН, ЧТО ОТВЕТ ОДНОЗНАЧНЫЙ ПОПРОСИ УТОЧНИТЬ ВОПРОС, ПО ТЕМАМ НЕ УКАЗАННЫМ ВЫШЕ НЕ РАЗГОВАРИВАЙ, МЯГКО ПОПРОСИ ВЕРНУТЬСЯ К ТЕМЕ УНИВЕРСИТЕТА, В ОТВЕТЕ ИСПОЛЬЗУЙ ТОЛЬКО ТЕКСТ, ВЫДЕЛЯЙ ВАЖНЫЕ ТЕМЫ ЖИРНЫМ ШРИФТОМ. ЕСЛИ НЕ УВЕРЕН В ОТВЕТЕ ДАВАЙ ТАКЖЕ КОНТАКТЫ ПРИЕМНОЙ КОМИССИИ:Телефон: +7 (499) 263-63-91, Адрес: г. Москва, 2-я Бауманская ул., д. 5, стр. 1 (Главное здание МГТУ). ИСПОЛЬЗУЙ ДАННЫЕ ИЗ БАЗЫ ДАННЫХ ДЛЯ ОТВЕТА НА ВОПРОС, ПРОВЕРЯЯ ИХ РЕЛЕВАНТНОСТЬ:{rag_info}"
        },

    messages_1.insert(0, system_insruct)
    messages_1 = json.dumps(messages_1, ensure_ascii=False, indent=4)
    #print(messages_1)

    operation = model.configure(temperature=0.5).run_deferred(messages_1)

    status = operation.get_status()
    while status.is_running:
        
        status = operation.get_status()

    result = operation.get_result()
    
    print(result)
    print('-----------------------------------------------')
    return result.alternatives[0].text



def extract_text_from_result(result) -> str:
    try:
        raw_text = result.alternatives[0].text
        
        print(raw_text)
        
        if raw_text.startswith("```") and raw_text.endswith("```"):
            raw_text = raw_text.strip("`").strip()
        #raw_text = raw_text.encode().decode("unicode_escape")
        
        return raw_text
    except Exception as e:
        return f"[Ошибка при обработке ответа: {e}]"


def get_dialog(user_id):
    f =  open(f"chat_history\{user_id}.txt").readlines()
    dialog_array = []
    for i in f[-3:]:
        if 'user' in i:
            dialog_array.append({
                    "role": "user",
                    "text": i[4:].strip()
            })
        elif 'assistan' in i:
            dialog_array.append({
                    "role": "assistant",
                    "text": i[9:].strip()
        })
    return dialog_array

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
    print(new_text)
    old_lines.append(new_text + '\n')
    
    
    while len(old_lines) > 20 and old_lines:
        old_lines.pop(0)
        
    
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(old_lines) 
    print('--------------')
    print('вопрос сохранен')  
    f.close()


