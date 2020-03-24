#!/bin/python3
from io import BytesIO
from pprint import pprint
from datetime import datetime, timedelta

import requests
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
import os
import requests

import telebot
from telebot import types

from qr_decoder import Check

TOKEN = #
STICKER_ID_GJ = 'CAADAgADJQAD--ADAAFr8LUIKr_oHxYE'

greeting1 = 'I will help you to figure out what are you spending money on and how to save them :)'
greeting2 = 'Only you need is to send me photo of QR-code in your receipt as an image file or as a photo'

# Сама работа бота

def welcome(bot, update):
    user_first_name = update.message.from_user.first_name
    update.message.reply_text(
        f'Hello, {user_first_name}! \n\n' 
        f'{greeting1} \n'
        f'{greeting2}')
    pprint(update.message.from_user.__dict__)
    print()

def help(bot, update):
    user_first_name = update.message.from_user.first_name
    update.message.reply_text(
        f"Usage: \n\n"
        "/gap week - total of this week \n"
        "/gap 10 - total of the last 10 days \n"
        "/day or \"/day today\" - total of the day \n"
        "/day yyyy-mm-dd - total of this exactly day \n"
        "/categories - total for today\n"
        "/categories yyyy-mm-dd - total for this exactly day \n")

    
def send_sticker(bot,update):
    #pprint(update.message.sticker.__dict__)
    sticker_id = update.message.sticker['file_id']
    update.message.reply_sticker(sticker_id)

    print(sticker_id)
    update.message.reply_text(f"Пока умею только дублировать твой стикер.")
    
    
def answer_photo(bot, update):
    # Тут говно
    date_of_photo = update.message.date
    date_of_photo = str(date_of_photo).split(' ')
    pprint(update.message.photo)
    global exactly_day
    global exactly_time
    global client_id
    exactly_day = date_of_photo[0]
    exactly_time = date_of_photo[1].split(':')   
    exactly_time = '-'.join(exactly_time[i] for i in range(0,len(exactly_time)))
    client_id = update.message.from_user.id

    file_link = bot.getFile(update.message.photo[0].file_id)['file_path']
    print(file_link)
    print("Скачиваю файл...")
    print()
    
    r = requests.get(file_link)

    # define the name of the directory to be created and checking their status at DB
    directory0 = f'/Users/dexp-pc/Desktop/Project/photos/{str(client_id)}/'
    directory = f'{directory0}{str(exactly_day)}/'
    
    if os.path.exists(directory0):
        pass
        #print(f'This client({client_id}) isn\'t the new one')
    else:
        os.mkdir(directory0)
    
    if os.path.exists(directory):
        pass
        #print(f'Id:{client_id} and Day:{exactly_day} packages are there (PHOTO)')
    else:
        os.mkdir(directory)

    #уже создаём само фото с названием в виде дня
    global path_to_file 
    path_to_file = f"{directory}{exactly_time}.{file_link.split('/')[-1].split('.')[-1]}"
    #print(path_to_file)
    
    with open(path_to_file, 'wb') as f:
        f.write(r.content)
        update.message.reply_text('Got it. Thanks!')
            
        
    path_to_image = path_to_file
        
    # define the name of the directory to be created and checking their status at DB
    directory_qr0 = f'/Users/dexp-pc/Desktop/Project/qrs/{str(client_id)}/'
    directory_qr = f'{directory_qr0}{str(exactly_day)}/'
    
    if os.path.exists(directory_qr0):
        pass
        #print(f'This client({client_id}) isn\'t the new one')
    else:
        os.mkdir(directory_qr0)
    
    if os.path.exists(directory_qr):
        pass
        #print(f'Id:{client_id} and Day:{exactly_day} packages are there (PHOTO)')
    else:
        os.mkdir(directory_qr)

    path_to_json = f'/Users/dexp-pc/Desktop/Project/qrs/{client_id}/{exactly_day}/{exactly_time}.json'
    
    check = Check(path_to_image, path_to_json)
    # если вдруг не смог вытащить инфу
    try:
        check.decode_qr_image()
        check.getReceipt()
        check.parse()
    except:
        update.message.reply_text('Smth went wrong. Try to send it as a file. Otherwise we do not know what to do:(')
    spisok = check.psrint()
    #=======================text
        
    # define the name of the directory to be created and checking their status at DB
    directory_txt0 = f'/Users/dexp-pc/Desktop/Project/text/{str(client_id)}/'
    directory_txt = f'{directory_txt0}{str(exactly_day)}.txt'
    
    if os.path.exists(directory_txt0):
        pass
        #print(f'This client({client_id}) isn\'t the new one')
    else:
        os.mkdir(directory_txt0)
    
    
    f = open(directory_txt, 'a')
    msg = ""
    msg_file = ""
    for product, price in spisok:
        msg_file += f'{exactly_day}, '
        #msg += f'{exactly_day}, {product}, {price}\n'
        for i in range(len(product.split())):
            if not product.split()[i][0].isdigit():
                msg += f'{product.split()[i]} '
                msg_file += f'{product.split()[i]} '
        msg += f'{price} RUB\n'
            
        f.write(f'{msg_file}, {price}\n')
        msg_file = ""
    f.close()
    update.message.reply_text(f"{msg}")
            
    #update.message.reply_text('Done!!!')
    update.message.reply_sticker(STICKER_ID_GJ)
    
    
    
def answer_file(bot, update):
    '''
    Тут мы качаем фото. сохраняем у себя и отправляем на чек
    Обязатель передаём только фото в виде файла.
    '''
    document = update.message['document']
    
    #pprint(update.__dict__)
    
    date_of_photo = update.message.date
    date_of_photo = str(date_of_photo).split(' ')
    global exactly_day
    global exactly_time
    global client_id
    exactly_day = date_of_photo[0]
    exactly_time = date_of_photo[1].split(':')   
    exactly_time = '-'.join(exactly_time[i] for i in range(0,len(exactly_time)))
    client_id = update.message.from_user.id
    
    pprint(document.__dict__)
    print()
    
    file_id = document['file_id']
    mime_type = document['mime_type']
    #that not to download big files
    now_type = mime_type.split('/')[-1]
    image_types = ['png', 'jpg', 'jpeg', 'bmp', 'psd']
    
    if (not mime_type.startswith('image') or (now_type not in image_types)):
        update.message.reply_text('I deal with image files only. Try again.')
        
    else:
        file_info_link = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}'
        file_path = requests.get(file_info_link).json()['result']['file_path']
        file_link = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        #file = requests.get(file_link).content
        print(file_link)
        print("Скачиваю файл...")
        print()
    
        r = requests.get(file_link)

        # define the name of the directory to be created and checking their status at DB
        directory0 = f'/Users/dexp-pc/Desktop/Project/photos/{str(client_id)}/'
        directory = f'{directory0}{str(exactly_day)}/'
    
        if os.path.exists(directory0):
            pass
            #print(f'This client({client_id}) isn\'t the new one')
        else:
            os.mkdir(directory0)
    
        if os.path.exists(directory):
            pass
            #print(f'Id:{client_id} and Day:{exactly_day} packages are there (PHOTO)')
        else:
            os.mkdir(directory)
        
        
        #уже создаём само фото с названием в виде дня
        global path_to_file 
        path_to_file = f"{directory}{exactly_time}.{file_link.split('/')[-1].split('.')[-1]}"
        #print(path_to_file)
    
        with open(path_to_file, 'wb') as f:
            f.write(r.content)
            update.message.reply_text('Got it. Thanks!')
            
        
        path_to_image = path_to_file
        
        # define the name of the directory to be created and checking their status at DB
        directory_qr0 = f'/Users/dexp-pc/Desktop/Project/qrs/{str(client_id)}/'
        directory_qr = f'{directory_qr0}{str(exactly_day)}/'
    
        if os.path.exists(directory_qr0):
            pass
            #print(f'This client({client_id}) isn\'t the new one')
        else:
            os.mkdir(directory_qr0)
    
        if os.path.exists(directory_qr):
            pass
            #print(f'Id:{client_id} and Day:{exactly_day} packages are there (QR)')
        else:
            os.mkdir(directory_qr)
    
        path_to_json = f'/Users/dexp-pc/Desktop/Project/qrs/{client_id}/{exactly_day}/{exactly_time}.json'
        print(path_to_json)
        check = Check(path_to_image, path_to_json)
        # если вдруг не смог вытащить инфу
        try:
            check.decode_qr_image()
            check.getReceipt()
            check.parse()
        except:
            update.message.reply_text('Smth went wrong. Try to send it as a file. Otherwise we do not know what to do:(')
    
            
        spisok = check.psrint()
        
        #=======================text
        
        # define the name of the directory to be created and checking their status at DB
        directory_txt0 = f'/Users/dexp-pc/Desktop/Project/text/{str(client_id)}/'
        directory_txt = f'{directory_txt0}{str(exactly_day)}.txt'
    
        if os.path.exists(directory_txt0):
            pass
            #print(f'This client({client_id}) isn\'t the new one')
        else:
            os.mkdir(directory_txt0)

        f = open(directory_txt, 'a')
        msg = ""
        msg_file = ""
        for product, price in spisok:
            msg_file += f'{exactly_day}, '
            #msg += f'{exactly_day}, {product}, {price}\n'
            for i in range(len(product.split())):
                if not product.split()[i][0].isdigit():
                    msg += f'{product.split()[i]} '
                    msg_file += f'{product.split()[i]} '
            msg += f'{price} RUB\n'
            
            f.write(f'{msg_file}, {price}\n')
            msg_file = ""
        f.close()
        update.message.reply_text(f"{msg}")
            
        #update.message.reply_text('Done!!!')
        update.message.reply_sticker(STICKER_ID_GJ)
	
def day_view(bot, update):
    client_id = update.message.from_user.id
    #pprint(update.message.date)
    text = str(update.message.text).split()[-1] # если пусто, то /day
    day = str(update.message.date).split()[0]

    if text != '/day' and text != 'today':
        directory_txt = f'/Users/dexp-pc/Desktop/Project/text/{str(client_id)}/{str(text)}.txt'
        sum = 0
        try:
            with open(directory_txt, 'r') as f: 
                for line in f:
                    if len((line.split(', ')[2])) > 1:
                        sum += float(line.split(', ')[-1])
                update.message.reply_text(f'Total amount for {text}:   {round(sum,2)} RUB')
        except:
            update.message.reply_text(f'Total amount for {text}:   0 RUB')
    else:
        directory_txt = f'/Users/dexp-pc/Desktop/Project/text/{str(client_id)}/{str(day)}.txt'
        sum = 0
        try:
            with open(directory_txt, 'r') as f: 
                for line in f:
                    if len((line.split(', ')[2])) > 1:
                        sum += float(line.split(', ')[2])
                update.message.reply_text(f'Total amount for TODAY:   {round(sum,2)} RUB')
        except:
            update.message.reply_text(f'Total amount for TODAY:   0 RUB')

def gap_view(bot, update):
    client_id = update.message.from_user.id
    day_today = datetime.today()
    text = str(update.message.text).split()[-1] #если пусто, то /gap
    sum = 0

    def amount(days):
        for i in range(int(text)):
            day_delta = timedelta(days = i)
            day = day_today - day_delta
            path = f'/Users/dexp-pc/Desktop/Project/text/{client_id}/{str(day).split()[0]}.txt'

            if os.path.exists(path):
                with open(path, 'r') as f:
                    for line in f:
                        if len((line.split(', ')[2])) > 1:
                            sum += float(line.split(', ')[2])
            else:
                sum += 0
        update.message.reply_text(f'Total amount for the last {text} days:   {round(sum,2)} RUB')


    if text != '/gap':
        for i in range(int(text)):
            day_delta = timedelta(days = i)
            day = day_today - day_delta
            path = f'/Users/dexp-pc/Desktop/Project/text/{client_id}/{str(day).split()[0]}.txt'

            if os.path.exists(path):
                with open(path, 'r') as f:
                    for line in f:
                        if len((line.split(', ')[2])) > 1:
                            sum += float(line.split(', ')[2])
            else:
                sum += 0
        update.message.reply_text(f'Total amount for the last {text} days:   {round(sum,2)} RUB')
    else:
        for i in range(7):
            day_delta = timedelta(days = i)
            day = day_today - day_delta
            path = f'/Users/dexp-pc/Desktop/Project/text/{client_id}/{str(day).split()[0]}.txt'

            if os.path.exists(path):
                with open(path, 'r') as f:
                    for line in f:
                        if len((line.split(', ')[2])) > 1:
                            sum += float(line.split(', ')[2])
            else:
                sum += 0
        update.message.reply_text(f'Total amount for the last week:   {round(sum,2)} RUB')

def month_view(bot, update):
    pass

def categories(bot, update):
    client_id = update.message.from_user.id
    day_today = datetime.today()
    text = str(update.message.text).split()[-1] # если пусто, то /categories
    
    if text in ('/categories','today'):
        text = str(update.message.date).split()[0]

    path_expens = f'/Users/dexp-pc/Desktop/Project/text/{client_id}/{text}.txt'
    path_cat = f'/Users/dexp-pc/Desktop/Project/XKeeper/categories.txt'
    f_expens = open(path_expens, 'r')
    f_cat = open(path_cat, 'r', encoding = 'utf-8')

    expens = []
    cat = []

    categories = {'alcohol': 0, 'bread' : 0, 'fastfood' : 0, 'fish' : 0, 'fruits' : 0, 'groceries' : 0,
     'meat' : 0, 'milk' : 0, 'others' : 0, 'sweets' : 0,
     'sweet' : 0, 'transport': 0, 'vegetables' : 0}

    for line_e in f_expens:
        expens.append(line_e.split(', '))
    for line_c in f_cat:
        cat.append(line_c.split(', '))

    for e in expens:
        price_e = e[2]
        word_e = e[1][:4].lower().split()[0]
    
        for c in cat:
            label = c[0]
            word_c = c[1][:4].lower().split()[0]
        
            if word_e == word_c:
                categories[label] += round(float(price_e),2)
            
    pprint(categories)

    cate_list = ""      
    for i in categories.items():
        cate_list += f"{i[0].title()}: {round(i[1],2)}\n"
    update.message.reply_text(f'{cate_list}')

    
def main():
    my_bot = Updater(TOKEN)

    dp = my_bot.dispatcher
    dp.add_handler(CommandHandler('start', welcome))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('day', day_view))
    dp.add_handler(CommandHandler('gap', gap_view))
    dp.add_handler(CommandHandler('categories', categories))
    
    dp.add_handler(MessageHandler(Filters.document, answer_file))
    dp.add_handler(MessageHandler(Filters.photo, answer_photo))
    dp.add_handler(MessageHandler(Filters.sticker, send_sticker))
    
    my_bot.start_polling()
    my_bot.idle()

if __name__ == '__main__':
    main()
