import pandas as pd
import re
import telebot
from telebot import types
from yandex_gpt_main import yandex_gpt, save_message
import ast
import psycopg2
from bs4 import BeautifulSoup
from base_functions import search1
from rag_functions import rel_inf, example, study_plan, specialties_list, specialties_with_kod
from model_util import model, device, tokenizer
from dotenv import load_dotenv
import os
import time

load_dotenv()

api_key = os.getenv("API_KEY")
debug_mode = os.getenv("DEBUG")

bot = telebot.TeleBot(api_key, parse_mode='HTML')  
bot.remove_webhook()
CHAT_HISTORY_DIR = "chat_history"

db_params = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}
table_sp = ['FAQ','specialties','disciplines','enterprises_new','individual_achievements','departments']

for i in range(len(table_sp)):
  table_name = table_sp[i]
  try:
      conn = psycopg2.connect(**db_params)
      if i == 0:
          query = f'SELECT * FROM "{table_name}"';
          df = pd.read_sql_query(query, conn)
          print(df.head())
      if i == 1:
          query = f'SELECT * FROM "{table_name}"';
          df1 = pd.read_sql_query(query, conn)
          print(df1.head())
      if i == 2:
          query = f'SELECT * FROM "{table_name}"';
          df2 = pd.read_sql_query(query, conn)
          print(df2.head())
      if i == 3:
          query = f'SELECT * FROM "{table_name}"';
          df3 = pd.read_sql_query(query, conn)
          print(df3.head())
      if i == 4:
          query = f'SELECT * FROM "{table_name}"';
          df4 = pd.read_sql_query(query, conn)
          print(df4.head())
      if i == 5:
          query = f'SELECT * FROM "{table_name}"';
          df5 = pd.read_sql_query(query, conn)
          print(df5.head())
  except Exception as e:
      print(f'ошибка :{e}')
  finally:
      conn.close()

  

def convert_markdown_to_html(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)   # жирный
    text = re.sub(r"__(.*?)__", r"<u>\1</u>", text)       # подчёркнутый
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)       # курсив
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)   # код
    return text

def convert_to_telegram_html(text: str) -> str:
    text = convert_markdown_to_html(text)
    text = text.replace("\\n", "\n").replace("\n\n", "\n")
    soup = BeautifulSoup(text, "html.parser")
    for tag in soup.find_all():
        if tag.name not in ['b', 'strong', 'i', 'em', 'u', 's', 'code', 'pre', 'a']:
            tag.unwrap()
    return str(soup)





def main(request_user,df,df1,df2,df3,df4,df5):
    
    functions = {
        0:rel_inf,
        1:rel_inf,
        2:rel_inf,
        3:rel_inf,
        4:rel_inf,
        5:rel_inf,
        6:rel_inf,
        7:rel_inf,
        8:rel_inf,
        9:rel_inf,
        10:rel_inf,
        11:rel_inf,
        12:rel_inf,
        13:rel_inf,
        14:rel_inf,
        15:rel_inf,
        16:rel_inf,
        17:rel_inf,
        18:rel_inf,
        19:rel_inf,
        20:rel_inf,
        21:rel_inf,
        22:rel_inf,
        23:rel_inf,
        24:rel_inf,
        25:rel_inf,
        26:rel_inf,
        27:rel_inf,
        28:rel_inf,
        29:rel_inf,
        30:rel_inf,
        31:rel_inf,
        32:rel_inf,
        34:rel_inf,
        35:rel_inf,
        36:rel_inf,
        37:rel_inf,
        38:rel_inf,
        39:rel_inf,
        40:rel_inf,
        43:rel_inf,
        44:rel_inf,
        45:rel_inf,
        46:rel_inf,
        47:rel_inf,
        48:rel_inf,
        49:rel_inf,
        169:rel_inf,
        170:rel_inf,
        41:study_plan,
        89:study_plan,
        118:study_plan,
        122:study_plan,
        124:study_plan,
        127:study_plan,
        130:study_plan,
        132:study_plan,
        135:study_plan,
        136:study_plan,
        138:study_plan,
        140:study_plan,
        141:study_plan,
        144:study_plan,
        200:specialties_with_kod,
        201:specialties_with_kod,
        202:specialties_with_kod,
        203:specialties_list,
        204:example
    }
    
    
    embedding = df['emb_FAQ'].apply(ast.literal_eval)
    
    num = int(search1(request_user,embedding))
    
    if num != -1:
      print(num, df.loc[num, 'Таблица\n'])
      try:
          
          args = [request_user,model,device,tokenizer,num,df,df1,df2,df3,df4,df5]
          result = functions[num](*args)
          return(result)
      except:
          result = example(request_user,model,device,tokenizer,num,df,df1,df2,df3,df4,df5)
          return(result)
    else:

      return('Придумай ответ самостоятельно')

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("👋 Спросить")
    btn2 = types.KeyboardButton("ℹ️ О боте")
    btn3 = types.KeyboardButton("📅 Даты")
    btn4 = types.KeyboardButton("📞 Контакты")
    btn5 = types.KeyboardButton("❓ Задать вопрос")
    btn6 = types.KeyboardButton("Ответ не подходит 😈")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)

    bot.send_message(
        message.chat.id, 
        "👋 Привет! Я твой бот-помощник МГТУ. Чем могу помочь?",
        reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    
    list_massage = pd.read_csv('Massage_list.csv')
    save_message(message.from_user.id,message.text,'user')
    error_list = pd.read_csv('Mistake_question.csv')
    try:
        if message.text == '👋 Спросить':
            save_message(message.from_user.id,"Привет! Задате мне вопрос о МГТУ, и я постараюсь ответить.",'assistant')
            bot.send_message(message.from_user.id, "Привет! Задате мне вопрос о МГТУ, и я постараюсь ответить.")
        elif message.text == 'ℹ️ О боте':
            save_message(message.from_user.id,"Привет! Я умный помощник МГТУ, который поможет тебе при поступлении на специалитет. Я умею отвечать на самые часто задаваемые вопросы и очень скоро научусь думать абстрактно. Задай мне вопрос и я отвечу!",'assistant')
            bot.send_message(message.from_user.id, "Привет! Я умный помощник МГТУ, который поможет тебе при поступлении на специалитет. Я умею отвечать на самые часто задаваемые вопросы и очень скоро научусь думать абстрактно. Задай мне вопрос и я отвечу!")
        elif message.text == '📅 Даты':
            save_message(message.from_user.id,"Привет! Задате мне вопрос о МГТУ, и я постараюсь ответить.",'assistant')
            bot.send_message(message.from_user.id, "Подробнее вы сможете ознакомиться по ссылке https://bmstu.ru/documents")
        elif message.text == '📞 Контакты':
            save_message(message.from_user.id,"Телефон приемной комиссии: ```+7\(499\)263\-65\-41```\nНаша почта: ```abiturient@bmstu\.ru```\nБолее подробную информацию вы можете прочитать на https://bmstu\.ru/admission\-board",'assistant')
            bot.send_message(
                message.from_user.id, 
                "Телефон приемной комиссии: ```+7\(499\)263\-65\-41```\nНаша почта: ```abiturient@bmstu\.ru```\nБолее подробную информацию вы можете прочитать на https://bmstu\.ru/admission\-board", 
                parse_mode="MarkdownV2"
            )

        elif message.text == '❓ Задать вопрос':
            save_message(message.from_user.id,"Напиши свой вопрос, и я постараюсь помочь, а если у меня не получится, то вы можете позвонить нам на телефон ```+7\(499\)263\-65\-41``` или написать на почту ```abiturient@bmstu\.ru```",'assistant')
            bot.send_message(
                message.from_user.id, 
                "Напиши свой вопрос, и я постараюсь помочь, а если у меня не получится, то вы можете позвонить нам на телефон ```+7\(499\)263\-65\-41``` или написать на почту ```abiturient@bmstu\.ru```", 
                parse_mode="MarkdownV2"
            )
        elif message.text == 'Ответ не подходит 😈':
            id = message.from_user.id
            
            try:
                
                for i in range(len(list_massage)-1,-1,-1):
                    
                    if  id == int(list_massage.loc[i, 'user_id']):
                        
                        error_list.loc[len(error_list)]=[list_massage.loc[i, 'Question'],list_massage.loc[i, 'Answer']]
                        break
                
                error_list.to_csv('Mistake_question.csv',index=False)
                save_message(message.from_user.id,"Ваш вопрос отправлен в тех.поддержку, в скором времени мы разберемся и исправим ошибки, спасибо за помощь!",'assistant')
                bot.send_message(message.from_user.id, "Ваш вопрос отправлен в тех.поддержку, в скором времени мы разберемся и исправим ошибки, спасибо за помощь!")
            except:
                save_message(message.from_user.id,'Спасибо за ваше сообщение!','assistant')
    
                bot.send_message(message.from_user.id, 'Спасибо за ваше сообщение!')
        else:
            
            prompt = main(message.text,df,df1,df2,df3,df4,df5)
            print(prompt)
            response = yandex_gpt(message.from_user.id,prompt) 
            print('модель дала ответ')   
            save_message(message.from_user.id,response,'assistant')
            
            result = convert_to_telegram_html(response)
            
            list_massage.loc[len(list_massage)]=[message.text,result,message.from_user.id]
            
            list_massage.to_csv('Massage_list.csv',index=False)
            if result == None:
                bot.send_message(message.from_user.id, "В моей базе данных нет информации об этом вопросе. Попробуйте переформулировать, а я попробую подумать")
                bot.send_message(message.from_user.id, "⏳ Думаю...")
                bot.send_message(message.from_user.id, "Попробуйте переформулировать и я отвечу еще раз")
            else:
              
              bot.send_message(message.from_user.id, result)
    except Exception as e:
        print(f"Ошибка: {e}")
        save_message(message.from_user.id,"К сожалению, у меня, пока что не получается овтветить на данный вопрос просьба нажать поле: 'Ответ не подходит 😈'",'assistant')
        bot.send_message(message.from_user.id, "К сожалению, у меня, пока что не получается овтветить на данный вопрос просьба нажать поле: 'Ответ не подходит 😈'")


def start_polling():
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Exception in polling: {e}")
            time.sleep(5) # чтобы не забанили за слишком частые запросы
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] завершился без ошибок")
            break

if __name__ == "__main__":
    start_polling()