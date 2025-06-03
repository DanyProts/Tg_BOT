import pandas as pd
import ast

from base_functions import search, match

def rel_inf(request_user,model,device,tokenizer,num,df,df1,df2,df3,df4,df5):
  return  df.loc[num, 'rel_info']
def example(request_user,model,device,tokenizer,num,df,df1,df2,df3,df4,df5):
    data = pd.DataFrame()
    s1 = df.loc[num, 'Таблица\n'][:-1]
    
    name_col = ['вектор_названия','вектор_краткое_описание',]
    if s1 == 'specialties':
        data = pd.concat([data, df1], ignore_index=True)
    elif s1 == 'disciplines':
        data = pd.concat([data, df2], ignore_index=True)
    elif s1 in 'enterprises_new':
        data = pd.concat([data, df3], ignore_index=True)
    elif s1 == "individual_achievements":
        
        data = pd.concat([data, df4], ignore_index=True)
        
    elif s1 == 'departments':
        data = pd.concat([data, df5], ignore_index=True)
    embedding = []

    
    for i in name_col:
        try:
            embedding = data[i].apply(ast.literal_eval)
            break
        except:
            continue

    req = match(request_user)
    
    num1 = search(req,embedding)
    res = ''
    colum = data.columns

    for i in colum:
        if 'вектор' not in i:
            res+= f'{i}:{data.loc[num1, i]}'+' '

    return res
def specialties_with_kod(request_user,model,device,tokenizer,num,df,df1,df2,df3,df4,df5):
    
    match_str=''
    for i in range(len(request_user)):
        if request_user[i] in '0123456789._':
            match_str+=request_user[i]
    req = match(match_str)
    
    result = ''
    if req:
        num = -1
        for i in range(len(df1)):
            if req == df1.loc[i, 'код_с_профилем'] or req == df1.loc[i, 'код']:
                num = i
                break
    else:
        num = []
        for i in range(len(df1)):
            if req == df1.loc[i, 'код_с_профилем'] or req == df1.loc[i, 'код']:
                num.append(i)
                
    if type(num) == int:
        if num != -1:
            for i in df1.columns[1:-2]:
                result+=f'{i}:{df1.loc[num, i]}'
        else:
            return 'Уточните пожалуйста ваш вопрос или попробуйте сформиулировать по другому'
    elif type(num)==list:
        if len(num)!=0:
            for j in num:
                for i in df1.columns[1:-2]:
                        result+=f'{i}:{df1.loc[j, i]}'
                result+='\t'
        else:
            return 'Уточните пожалуйста ваш вопрос или попробуйте сформиулировать по другому'
    return result

def study_plan(request_user,model,device,tokenizer,num,df,df1,df2,df3,df4,df5):
    req = match(request_user)
    embedding = df1['вектор_названия'].apply(ast.literal_eval)
    num = search(req,embedding)
    
    kod = df1.loc[num, 'код_с_профилем']
    res = ''
    for i in range(len(df1)):
        if df2.loc[i, 'speciality_id'] == kod:
            s1 = df2.loc[i, 'discipline']
            s2 = df2.loc[i, 'department']
            res += f'{s1}:{s2},  '
    return res
def specialties_list(request_user,model,device,tokenizer,num,df,df1,df2,df3,df4,df5):
    request = request_user.split()
    codes = ['ИУ', 'СМ', 'ФН', 'БМТ', 'РК', 'Э', 'Л', 'ИБМ', 'ЮР', 'МТ', 'РЛ', 'СГН', 'РКТ']
    list_spec = []
    for prefix in codes:
        for req in request:
            if prefix in req.upper() and len(req)-len(prefix)<3:
                list_spec.append(prefix)
    
    result = ''
    for req in list_spec:
        for i in range(len(df5)):
            if req in df5.loc[i, 'name']:
                result+= df5.loc[i, 'name'] +':'+ df5.loc[i, 'description']+' '
    if result != '':
        return result
    else:
        return 'Уточните пожалуйста ваш вопрос или попробуйте сформиулировать по другому'

