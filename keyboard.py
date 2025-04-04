import os
import pandas as pd

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import WebAppInfo

# Стандартная клавиатура
def main_keyboard():
    markup = InlineKeyboardMarkup()
    web_info_cabs = WebAppInfo('https://docs.google.com/spreadsheets/u/0/d/1yGUeXqHzZ-DaP2dbCEx3EC_MtQkYK3dAtjYXgMraTrY/htmlview#gid=0')
    web_info_moodle = WebAppInfo('https://kapps.at/ords/r/rnd/wishmate/home') #('https://moodleprk.kuzstu.ru/login/index.php')
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Расписание на сегодня", callback_data="class_schedule_day"),
        InlineKeyboardButton("Расписание на неделю", callback_data="class_schedule_week"),
        InlineKeyboardButton("Расписание комп. каб.", web_app=web_info_cabs),
        InlineKeyboardButton("MOODLE", web_app=web_info_moodle),
        InlineKeyboardButton("Доп. информация", callback_data="info")
    )
    return markup

def profile_choice():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("ВО", callback_data="ВО"),
        InlineKeyboardButton("СПО / Лицей", callback_data="СПО"),
        InlineKeyboardButton("Заочное", callback_data="заочное")
    )
    return markup

def back_to_main():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Назад", callback_data="back_to_main")
    )
    return markup



def class_schedule_keyboard():
    path = "D:\Programing\python\schedule\pdfs"
    files = []

    for f in os.listdir(path):
        if f.endswith('.pdf'):
            files.append(f)

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for i in range(len(files)):
        markup.add(InlineKeyboardButton((files[i][:-4]).split()[0] + " " + ' '.join((files[i][:-4]).split()[-3:]), callback_data='schedule_' + str(i)))
    markup.add(InlineKeyboardButton("Назад", callback_data="back"))
    return markup

def groups_keyboard(file):
    path = 'D:\Programing\python\schedule\pdfs\\'
    df = pd.read_excel(path + file[:-4] + '.xlsx')
    df.reset_index()
    df.dropna(how='all', inplace=True)
    #display(df)

    groups = list(df.iloc[:, 4::2].columns)

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    for i in range(0, len(groups)-1, 2):
        print(i)
        markup.add(
            InlineKeyboardButton(groups[i], callback_data=("groups_"+str(i))),
            InlineKeyboardButton(groups[i+1], callback_data=("groups_"+str(i+1)))
        )
    markup.add(InlineKeyboardButton("Назад", callback_data="back_schedule"))
    return markup

