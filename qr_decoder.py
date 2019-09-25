#!/bin/python3

from io import BytesIO
from pprint import pprint

import requests
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
import os
import requests


class Check:
    def __init__(self, path_to_qr_image, path_to_json):
        self.path_to_qr_image = path_to_qr_image
        self.path_to_json = path_to_json
        self.products = None
        self.total = None
        self.date_time = None
        self.userInn = None
        self.decoded_qr = None
        
        #general
        self.url = "https://proverkacheka.nalog.ru:9999/v1/"
        self.mobile_user = "mobile/users/"
        self.sign = "signup"
        self.login = "login"
        self.restore = "restore"
        self.phone = "phone"
        self.headers = {'Device-OS':'', 'Device-Id':''}
        self.test='t=20190916T2024&s=2074.55&fn=9289000100461638&i=27517&fp=2675576248&n=1'
        
        #user
        self.name = "Hleb"
        self.phone_number = "+79056202225"
        self.password = "784579"
        
    def decode_qr_image(self):
        from pyzbar.pyzbar import decode
        from PIL import Image
        
        decoded = decode(Image.open(self.path_to_qr_image))
        self.decoded_qr = decoded[0].data.decode("utf-8")
        
    def create_user(self):
        data = {"email" : self.email, "name" : self.name, self.phone : self.phone_number}
        answer = requests.post(f"{self.url}{self.mobile_user}{self.sign}", json=data)
        print(answer) #for debug
    
    def parserQRCodeInforamtion(self):
        receiptData = {}
        for pair_input_variables in self.decoded_qr.split("&"):
            var_name, var_value = pair_input_variables.split("=")
            receiptData[var_name] = var_value
        return receiptData
    
    def getReceipt(self):
        import requests
        
        receiptData = self.parserQRCodeInforamtion()

        s = receiptData['s'].replace(".", "")
        fn = receiptData['fn']
        fp = receiptData['fp']
        n = receiptData['n']
        i = receiptData['i']
        year = receiptData['t'][0:4] 
        month = receiptData['t'][4:6]
        day = receiptData['t'][6:8] 
        hour = receiptData['t'][9:11]
        minute = receiptData['t'][11:13]

        t = f"{year}-{month}-{day} {hour}:{minute}:00"
        ofds_inns_fss = "ofds/*/inns/*/fss/"
        inns_kkts_fss = "inns/*/kkts/*/fss/"
        fiscal = "?fiscalSign="
        op = "/operations/"
        tickets = "/tickets/"
        send_email = "&sendToEmail=no"
        sum_url = "&sum="
        date = "&date="

        # проверка необходима
        ans_er = requests.get(
            f"{self.url}{ofds_inns_fss}{fn}{op}{n}{tickets}{i}{fiscal}{fp}{date}{t}{sum_url}{s}", 
            auth=(self.phone_number, self.password), 
            headers=self.headers)
        
        ans_gr = requests.get(
            f"{self.url}{inns_kkts_fss}{fn}{tickets}{i}{fiscal}{fp}{send_email}",
            headers=self.headers,
            auth=(self.phone_number, self.password))
        
        f = open(self.path_to_json, 'wb')
        f.write(ans_gr.content)
        f.close()
        #pprint(ans_er.content)

    def parse(self):
        import json
        
        with open(self.path_to_json, "r", encoding='utf-8') as read_file:
            data = json.load(read_file)
            products = {}
            for product in data.get('document').get('receipt').get('items'):
                products[product.get('name')] = product.get('price') / 100
            self.products = products
            self.total = data.get('document').get('receipt').get('totalSum') / 100
            self.date_time = data.get('document').get('receipt').get('dateTime')
            self.userInn = data.get('document').get('receipt').get('userInn')
    
    def psrint(self):
        global spisok
        spisok = self.products.items()
        return spisok
        #for product, price in spisok:
        #    print(f"{product} {price}")
    