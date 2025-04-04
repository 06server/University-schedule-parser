import telebot
import datetime
import pdfplumber
import requests
import wget
import os
import shutil
import pandas as pd

from bs4 import BeautifulSoup
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from data import TG_TOKEN
from keyboard import *
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import asyncio_filters

bot = AsyncTeleBot(TG_TOKEN, state_storage=StateMemoryStorage())

class MyStates(StatesGroup):
    group = State()
    profile = State()

pdfs_dir = "D:\Programing\python\schedule\\"
pdfs_dir_name = "pdfs"
site_url = "http://www.prk.kuzstu.ru"
url_raspisanie = "http://www.prk.kuzstu.ru/studentu/raspisanie/"

# Удаление директории с pdf
def clear_dir():
    path = os.path.join(pdfs_dir, pdfs_dir_name)
    for file in os.listdir(path):
        path_file = os.path.join(path, file)
        os.remove(path_file)

    print('Директория очищена')

# Парсинг pdf файлов расписания с сайта, сохранение в папку pdfs
def download_pdfs():
    page = requests.get(url_raspisanie)
    soup = BeautifulSoup(page.text, "html.parser")
    data = soup.findAll('div', class_='tab-content-file__links')

    clear_dir()

    pdfs = []

    for s in data:
        if str(s).find("Расписание") is not None and str(s).find("Расписание") != -1:
            a_tag = str(s).split("\n")[1]
            href_index = a_tag.find('href') + 5
            pdfs.append(site_url + a_tag[href_index:].split('"')[1])

        
    urls_for_download = list(set(pdfs))

    for url in urls_for_download:
        if 'заочное' not in url:
            wget.download(url, pdfs_dir + pdfs_dir_name)
    
    print("\nЗагрузка pdf закончена")

# Функция конвертации pdf в директории
def convert():
    df = pd.DataFrame()

    path = "D:\Programing\python\schedule\pdfs\\"
    files = []

    for f in os.listdir(path):
        if f.endswith('.pdf') and 'заочное' not in f:
            files.append(f)

    def str_to_time(string):
        if string == "время":
            return string
        elif len(string) == 0:
            return string
        elif len(string) < 9:
            new_string = '0' + string
            output = new_string[0:2] + ":" + new_string[2:7] + ":" + new_string[7:9]
            return output
        else:
            output = string[0:2] + ":" + string[2:7] + ":" + string[7:9]
            return output


    for file in files:
        with pdfplumber.open(path + file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    
                    df_table = pd.DataFrame(table, columns=['c1', 'c2','c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11', 'c12', 'c13', 'c14', 'c15', 'c16']).drop(['c3', 'c15', 'c16'], axis=1)
                    df_table['c1'] = df_table['c1'].apply(lambda x: (''.join(str(x).splitlines())[::-1].title()) if str(x) != "None" else x)
                    df_table.loc[0, 'c1'] = 'День недели'
                    df_table['c1'] = df_table['c1'].ffill()
                    df_table['c2'] = df_table['c2'].ffill()
                    df_table['c4'] = df_table['c4'].apply(str_to_time)
                    df_table['c2'] = df_table['c2'].apply(lambda x: (''.join(str(x).splitlines())[::-1].title()) if str(x) != "None" and str(x) != "дата" else x)
                    
                    #display(df_table)
                    #print(df_table.shape)
                    df_table.columns = [df_table.iloc[0]]
                    #df_table.drop([0], inplace=True, axis=0)
                        
                    if len(df) == 0:
                        df = pd.concat([df, df_table], ignore_index=False, sort=False)
                    else:
                        df = pd.concat([df, df_table.iloc[:, 3:]], ignore_index=False, sort=False, axis=1)

        df.drop([0], inplace=True)
        #df.reset_index()
        #print(df.shape)
        df.to_excel(f'{path}{file[:-4]}.xlsx')
        print(f"{file} - DONE!")
        df = pd.DataFrame()     

    print('Файлы успешно конвертированы')

# Функция поиска расписания группы на сегодня
def day_classes(group, profile):
    path = "D:\Programing\python\schedule\pdfs\\"
    files = []

    # Сбор всех pdf в директории
    for f in os.listdir(path):
        if f.endswith('.xlsx') and profile in f and f[0] != '~':
            files.append(f)

    output_string = ''
    
    for f in files:
        try:
            df = pd.read_excel(path + f)
            df.reset_index()
            df.dropna(how='all', inplace=True)

            now_date = str(datetime.datetime.now().date().strftime("%d.%m.%y"))

            group_df = df.iloc[:, [1,2,3, df.columns.get_loc(group), df.columns.get_loc(group)+1]]
            mask = group_df['дата'] == f'{now_date}'
            output_df = group_df[mask]
            output_df.fillna('', inplace=True)

            if len(output_df) > 0:
                output_string += f'{output_df.iloc[0, 0]}  ({output_df.iloc[0, 1]})\n'
                for i in range(len(output_df)):
                    #print(f'{output_df.iloc[i, 2]:11} | {output_df.iloc[i, 3]:28} | {str(output_df.iloc[i, 4])[:-2]}')
                    if output_df.iloc[i, 4] == '':
                        add_info = output_df.iloc[i, 4]
                    else:
                        add_info = '(' + output_df.iloc[i, 4] + ')'

                    if ((i%7)+1) % 6 == 0:
                        output_string += '\n'

                    output_string += f'\n{i+1} | {output_df.iloc[i, 3]}   {add_info}'
                
                return output_string
                
        except KeyError:
            print('key err')
            continue

        except IndexError:
            print('index err')
            continue

# Функция поиска расписания группы на неделю
def week_classes(group, profile):
    path = "D:\Programing\python\schedule\pdfs\\"
    files = []

    # Сбор всех pdf в директории
    for f in os.listdir(path):
        if f.endswith('.xlsx') and profile in f and f[0] != '~':
            files.append(f)

    output_string = ''
    
    for f in files:
        try:
            df = pd.read_excel(path + f)
            df.reset_index()
            df.dropna(how='all', inplace=True)

            now_date = datetime.datetime.now().date()
            now_date_str = now_date.strftime("%d.%m.%y")
            first_day_of_week = (now_date - datetime.timedelta(days=now_date.weekday())).strftime("%d.%m.%Y")

            group_df = df.iloc[:, [1,2,3, df.columns.get_loc(group), df.columns.get_loc(group)+1]]
            mask = group_df['дата'] >= first_day_of_week
            output_df = group_df[mask]
            output_df.fillna('', inplace=True)

            if len(output_df) > 0:
                for i in range(len(output_df)):
                    #print(f'{output_df.iloc[i, 2]:11} | {output_df.iloc[i, 3]:28} | {str(output_df.iloc[i, 4])[:-2]}')
                    if output_df.iloc[i, 4] == '':
                        add_info = output_df.iloc[i, 4]
                    else:
                        add_info = '(' + output_df.iloc[i, 4] + ')'

                    if i % 7 == 0:
                        if i == 0:
                            output_string += f'\n\n{output_df.iloc[i, 0]}  ({output_df.iloc[i, 1]})'                            
                        else:
                            output_string += f'\n----------\n\n{output_df.iloc[i, 0]}  ({output_df.iloc[i, 1]})'
                        
                    if ((i%7)+1) % 6 == 0:
                        output_string += '\n'
                        
                    output_string += f'\n{(i%7)+1:2} | {output_df.iloc[i, 3]}  {add_info}'

                
                return output_string
                
        except KeyError:
            print('key err')
            continue

        except IndexError:
            print('index err')
            continue

@bot.message_handler(commands=['start'])
async def starting(message):
    """

    await bot.send_message(message.chat.id, "Hello", reply_markup=main_keyboard())    
    """
    await bot.delete_my_commands(scope=None, language_code=None)
    await bot.set_my_commands(
        commands=[
            telebot.types.BotCommand("start", "Посмотреть расписание"),
            telebot.types.BotCommand("reset", "Изменить данные")
            #telebot.types.BotCommand("update", "Обновить данные")
        ], )
    
    await bot.set_state(message.from_user.id, MyStates.group, message.chat.id)
    await bot.send_message(message.chat.id, "Введите навзвание группы:")

# Сброс данных пользователя
@bot.message_handler(commands=['reset'])
async def starting(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['group'] = ''      
        data['profile'] = ''       

    await bot.set_state(message.from_user.id, MyStates.group, message.chat.id)
    await bot.send_message(message.chat.id, "Введите навзвание группы:")

# Апдейт файлов расписания
@bot.message_handler(commands=['update'])
async def update(message):
    print(message.chat.id)
    if message.chat.id == 1163738962:
        download_pdfs()
        convert()
        await bot.send_message(message.chat.id, "Данные обновлены")

@bot.message_handler(state=MyStates.group)
async def get_group(message):

    await bot.send_message(message.chat.id, "Выберите вид обучения:", reply_markup=profile_choice())
    await bot.set_state(message.from_user.id, MyStates.profile, message.chat.id)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['group'] = message.text   

@bot.message_handler(state=MyStates.profile)
async def get_profile(message):

    await bot.send_message(message.chat.id, "f:", reply_markup=main_keyboard())
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['profile'] = ""
    
@bot.callback_query_handler(func=lambda call:True)
async def editing_keyboard(call):
    cid = call.message.chat.id

    path = "D:\Programing\python\schedule\pdfs"
    files = []

    for f in os.listdir(path):
        if f.endswith('.pdf'):
            files.append(f)

    if call.data == "ВО":
        async with bot.retrieve_data(cid, cid) as data:
            data['profile'] = call.data
        await bot.edit_message_text(chat_id=cid, message_id=call.message.id, text="Добро пожаловать!")
        await bot.edit_message_reply_markup(chat_id=cid, message_id=call.message.id, reply_markup=main_keyboard())
    
    elif call.data == "СПО":
        async with bot.retrieve_data(cid, cid) as data:
            data['profile'] = call.data
        await bot.edit_message_text(chat_id=cid, message_id=call.message.id, text="Добро пожаловать!")
        await bot.edit_message_reply_markup(chat_id=cid, message_id=call.message.id, reply_markup=main_keyboard())
  
    elif call.data == "заочное":
        async with bot.retrieve_data(cid, cid) as data:
            data['profile'] = call.data
        await bot.edit_message_text(chat_id=cid, message_id=call.message.id, text="Добро пожаловать!")
        await bot.edit_message_reply_markup(chat_id=cid, message_id=call.message.id, reply_markup=main_keyboard())
  
    elif call.data == "class_schedule_day":
        async with bot.retrieve_data(cid, cid) as data:
            await bot.edit_message_text(chat_id=cid, message_id=call.message.id, text=day_classes(data['group'], data['profile']))
            await bot.edit_message_reply_markup(chat_id=cid, message_id=call.message.id, reply_markup=back_to_main())

    elif call.data == "class_schedule_week":
        async with bot.retrieve_data(cid, cid) as data:
            await bot.edit_message_text(chat_id=cid, message_id=call.message.id, text=week_classes(data['group'], data['profile']))
            await bot.edit_message_reply_markup(chat_id=cid, message_id=call.message.id, reply_markup=back_to_main())

    elif call.data[:9] == "schedule_":
        await bot.edit_message_reply_markup(chat_id=cid, message_id=call.message.id, reply_markup=groups_keyboard(files[int(call.data[9:])]))    

    elif call.data == "back_to_main":
        await bot.edit_message_text(chat_id=cid, message_id=call.message.id, text="Добро пожаловать!")
        await bot.edit_message_reply_markup(chat_id=cid, message_id=call.message.id, reply_markup=main_keyboard())

    elif call.data == "back_schedule":
        await bot.edit_message_reply_markup(chat_id=cid, message_id=call.message.id, reply_markup=class_schedule_keyboard())


bot.add_custom_filter(asyncio_filters.StateFilter(bot))