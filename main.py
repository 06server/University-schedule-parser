import requests
import wget
import os
import asyncio
import datetime

from tabula import read_pdf
from bot import *
from bs4 import BeautifulSoup

# colors for cmd
FRED    	= "\033[31m"
FGREEN  	= "\033[32m"
FYELLOW 	= "\033[33m"
FBLUE   	= "\033[34m"
RESET_ALL   = "\033[0m"

pdfs_dir = "D:\Programing\python\schedule\\"
pdfs_dir_name = "pdfs"
site_url = "http://www.prk.kuzstu.ru"
url_raspisanie = "http://www.prk.kuzstu.ru/studentu/raspisanie/"

"""
def clear_dir():
    # Удаление директории с pdf
    path = os.path.join(pdfs_dir, pdfs_dir_name)
    os.rmdir(path)

def make_dir():
    # Создание новой дириктории для pdf
    path = os.path.join(pdfs_dir, pdfs_dir_name)
    os.mkdir(path)

def download_pdfs():
    # Парсинг pdf файлов расписания с сайта, сохранение в папку pdfs
    page = requests.get(url_raspisanie)
    soup = BeautifulSoup(page.text, "html.parser")
    data = soup.findAll('div', class_='tab-content-file__links')

    clear_dir()
    make_dir()

    pdfs = []

    for s in data:
        if str(s).find("Расписание") is not None and str(s).find("Расписание") != -1:
            a_tag = str(s).split("\n")[1]
            href_index = a_tag.find('href') + 5
            pdfs.append(site_url + a_tag[href_index:].split('"')[1])

        
    urls_for_download = list(set(pdfs))

    for url in urls_for_download:
        wget.download(url, pdfs_dir + pdfs_dir_name)

def convert():
    # Функция конвертации pdf в директории
    df = pd.DataFrame()

    path = "D:\Programing\python\schedule\pdfs"
    files = []

    for f in os.listdir(path):
        if f.endswith('.pdf'):
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
        with pdfplumber.open(file) as pdf:
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
        df.to_excel(f'{file[:-4]}.xlsx')
        print(f"{file} - DONE!")
        df = pd.DataFrame()     

    print('END!')
"""


def main():    
    print("-" * 80)
    print(f"{FGREEN} [START] {RESET_ALL}| {' '*9}Date: [{date}]")
    print("-" * 80)  
    asyncio.run(bot.polling(non_stop=True, request_timeout=90))

if __name__ == '__main__':
    date = str(datetime.datetime.now())[:-7]

    main()
    #download_pdfs()
    #download_pdfs()