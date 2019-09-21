#!/bin/python3
from io import BytesIO
from pprint import pprint

import requests
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
import os
import requests

from qr_decoder import Check

TOKEN = #your token
STICKER_ID_GJ = 'CAADAgADJQAD--ADAAFr8LUIKr_oHxYE'

help1 = 'Welcome! I will help you to figure out what are you spending money on and how to save them :)'
help2 = 'Only you need is to send me photo of QR-code in your receipt as an image file or as a photo'

# Сама работа бота
def answer(bot, update):
    user_first_name = update.message.from_user.first_name

    update.message.reply_text(f"Hello, {user_first_name}")
    pprint(update.message.from_user.__dict__)
    print()

def help(bot, update):
    update.message.reply_text(f'{help1}')
    update.message.reply_text(f'{help2}')
    #pprint(update.message.from_user.__dict__)
    print()

def send_sticker(bot,update):
    #pprint(update.message.sticker.__dict__)
    sticker_id = update.message.sticker['file_id']
    update.message.reply_sticker(sticker_id)
    update.message.reply_text(f"Пока умею только дублировать твой стикер.")
    
    
def answer_photo(bot, update):
    # Тут говно
    date_of_photo = update.message.date
    date_of_photo = str(date_of_photo).split(' ')
    global exactly_day
    global exactly_time
    global client_id
    exactly_day = date_of_photo[0]
    exactly_time = date_of_photo[1].split(':')   
    exactly_time = '-'.join(exactly_time[i] for i in range(0,len(exactly_time)))
    client_id = update.message.from_user.id

    file_link = bot.getFile(update.message.photo[-1].file_id)['file_path']
    
    print("Скачиваю файл...")
    print()
    
    r = requests.get(file_link)

    # define the name of the directory to be created and checking their status at DB
    directory0 = f'/Users/dexp-pc/Desktop/Project/photos/{str(client_id)}/'
    directory = f'{directory0}{str(exactly_day)}/'
    
    if os.path.exists(directory0):
        print(f'This client({client_id}) isn\'t the new one')
    else:
        os.mkdir(directory0)
    
    if os.path.exists(directory):
        print(f'Id:{client_id} and Day:{exactly_day} packages are there (PHOTO)')
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
        print(f'This client({client_id}) isn\'t the new one')
    else:
        os.mkdir(directory_qr0)
    
    if os.path.exists(directory_qr):
        print(f'Id:{client_id} and Day:{exactly_day} packages are there (QR)')
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
        update.message.reply_text('Something went wrong :( Try another photo please!')
            
    spisok = check.psrint()
        
    #=======================text
        
    # define the name of the directory to be created and checking their status at DB
    directory_txt0 = f'/Users/dexp-pc/Desktop/Project/text/{str(client_id)}/'
    directory_txt = f'{directory_txt0}{str(exactly_day)}.txt'
    
    if os.path.exists(directory_txt0):
        print(f'This client({client_id}) isn\'t the new one')
    else:
        os.mkdir(directory_txt0)

    f = open(directory_txt, 'a')
    for product, price in spisok:
        update.message.reply_text(f"{product} {price}")
            
        f.write(f'{exactly_day}, {product}, {price}\n')
            
    f.close()
    #update.message.reply_text('Done!!!')
    update.message.reply_sticker(STICKER_ID_GJ)
    
    
    
def reply_to_photo(bot, update):
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
        
        print("Скачиваю файл...")
        print()
    
        r = requests.get(file_link)

        # define the name of the directory to be created and checking their status at DB
        directory0 = f'/Users/dexp-pc/Desktop/Project/photos/{str(client_id)}/'
        directory = f'{directory0}{str(exactly_day)}/'
    
        if os.path.exists(directory0):
            print(f'This client({client_id}) isn\'t the new one')
        else:
            os.mkdir(directory0)
    
        if os.path.exists(directory):
            print(f'Id:{client_id} and Day:{exactly_day} packages are there (PHOTO)')
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
            print(f'This client({client_id}) isn\'t the new one')
        else:
            os.mkdir(directory_qr0)
    
        if os.path.exists(directory_qr):
            print(f'Id:{client_id} and Day:{exactly_day} packages are there (QR)')
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
            update.message.reply_text('Something went wrong :( Try another photo please!')
            
        spisok = check.psrint()
        
        #=======================text
        
        # define the name of the directory to be created and checking their status at DB
        directory_txt0 = f'/Users/dexp-pc/Desktop/Project/text/{str(client_id)}/'
        directory_txt = f'{directory_txt0}{str(exactly_day)}.txt'
    
        if os.path.exists(directory_txt0):
            print(f'This client({client_id}) isn\'t the new one')
        else:
            os.mkdir(directory_txt0)

        f = open(directory_txt, 'a')
        for product, price in spisok:
            update.message.reply_text(f"{product} {price}")
            
            f.write(f'{exactly_day}, {product}, {price}\n')
            
        f.close()
        #update.message.reply_text('Done!!!')
        update.message.reply_sticker(STICKER_ID_GJ)
        

def main():
    my_bot = Updater(TOKEN)

    dp = my_bot.dispatcher
    dp.add_handler(CommandHandler('start', answer))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.document, reply_to_photo))
    dp.add_handler(MessageHandler(Filters.photo, answer_photo))
    dp.add_handler(MessageHandler(Filters.sticker, send_sticker))
    
    my_bot.start_polling()
    my_bot.idle()

if __name__ == '__main__':
    main()