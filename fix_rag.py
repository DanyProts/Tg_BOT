import pandas as pd
import ast
import psycopg2
from base_functions import search, search_bm25



db_params = {
        'host': '212.109.194.252',
        'port': '5432',
        'dbname': 'admission',
        'user': 'postgres',
        'password': 'F2_RdsFh2'
    }
conn = psycopg2.connect(**db_params)
query = f'SELECT * FROM "FAQ"';
FAQ = pd.read_sql_query(query, conn)

FAQ['emb_FAQ'] = FAQ['emb_FAQ'].apply(ast.literal_eval)


def predict_table(req,FAQ):
  a={'specialties':0,'enterprises':0,'disciplines':0,'departments':0,'individual_achievements':0,'rel_info':0}
  result = [search(req, FAQ['emb_FAQ']), search_bm25(req, FAQ['FAQ'])]
  for i in result:
    for j in i:
      a[FAQ['Таблица'][j]] += 1
  
  max_key = max(a, key=a.get)
  return max_key

req='Какие проходные баллы на направление Информатика и вычислительная техника в 2023 году на бюджет'
print(predict_table(req,FAQ))