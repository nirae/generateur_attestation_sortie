#! /usr/bin/env python3

# pip3 install python-telegram-bot
import telegram
# pip3 install selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import yaml
import re
import os
import glob
from datetime import datetime
import time
from marshmallow import Schema, fields, validate, validates, post_load, ValidationError
import argparse as arg

class Generator(object):

    def __init__(self):
        self.url = "https://media.interieur.gouv.fr/deplacement-covid-19/"
        options = webdriver.ChromeOptions()
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        options.add_experimental_option("prefs", {"download.default_directory": self.dir_path, "intl.accept_languages": "fr"})
        options.add_argument('headless')
        options.add_argument('no-sandbox')
        options.add_argument('lang=fr')
        self.driver = webdriver.Chrome(options=options)

    def run(self, config):
        self.driver.get("https://media.interieur.gouv.fr/deplacement-covid-19/")
        # form
        self.driver.find_element_by_id("field-firstname").send_keys(config.first_name)
        self.driver.find_element_by_id("field-lastname").send_keys(config.last_name)
        self.driver.find_element_by_id("field-birthday").send_keys(config.birthday)
        self.driver.find_element_by_id("field-placeofbirth").send_keys(config.placeofbirth)
        self.driver.find_element_by_id("field-address").send_keys(config.address)
        self.driver.find_element_by_id("field-city").send_keys(config.city)
        self.driver.find_element_by_id("field-zipcode").send_keys(config.zipcode)
        self.driver.find_element_by_id("field-datesortie").send_keys(config.date)
        self.driver.find_element_by_id("field-heuresortie").send_keys(config.time)
        # checkboxs reasons
        if config.reason == 'achats':
            self.driver.find_element_by_id("checkbox-achats").click()
        elif config.reason == 'sante':
            self.driver.find_element_by_id("checkbox-sante").click()
        elif config.reason == 'famille':
            self.driver.find_element_by_id("checkbox-famille").click()
        elif config.reason == 'travail':
            self.driver.find_element_by_id("checkbox-travail").click()
        elif config.reason == 'handicap':
            self.driver.find_element_by_id("checkbox-handicap").click()
        elif config.reason == 'sports_animaux':
            self.driver.find_element_by_id("checkbox-sport_animaux").click()
        elif config.reason == 'convocation':
            self.driver.find_element_by_id("checkbox-convocation").click()
        elif config.reason == 'missions':
            self.driver.find_element_by_id("checkbox-missions").click()
        elif config.reason == 'enfants':
            self.driver.find_element_by_id("checkbox-enfants").click()
        # button
        self.driver.find_element_by_id("generate-btn").click()
        time.sleep(1)
        file = glob.glob("attestation-*.pdf")
        if not file:
            print("Bad informations for the form")
            return None
        filename = "%s_attestation.pdf" % config.user
        os.rename(file[0], filename)
        return self.dir_path + '/' + filename

    def close(self):
        self.driver.close()

class Config(object):

    def __init__(self, user, first_name, last_name, birthday, placeofbirth, address, zipcode, city, reason, send=None, date=None, time=None):
        self.user = user
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.placeofbirth = placeofbirth
        self.address = address
        self.zipcode = str(zipcode)
        self.city = city
        self.reason = reason
        self.sender = send
        if not date:
            self.date = self.get_current_date()
        else:
            self.date = date
        if not time:
            self.time = self.get_current_time()
        else:
            self.time = time

    def get_current_date(self):
        today = datetime.today()
        return today.strftime("%d/%m/%Y")
    
    def get_current_time(self):
        today = datetime.today()
        return today.strftime("%H:%M")

class ConfigSchema(Schema):
    available_reasons = [
        'achats',
        'sante',
        'famille',
        'travail',
        'handicap',
        'sports_animaux',
        'convocation',
        'missions',
        'enfants'
    ]
    senders = ['telegram']
    telegram_options = ['chat_id', 'token']

    user = fields.Str(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    birthday = fields.Str(required=True)
    placeofbirth = fields.Str(required=True)
    address = fields.Str(required=True)
    zipcode = fields.Int(required=True)
    city = fields.Str(required=True)
    reason = fields.Str(required=True, validate=validate.OneOf(available_reasons))
    send = fields.Dict(
        keys=fields.Str(
            required=True,
            validate=validate.OneOf(senders)
        ),
        values=fields.Dict(
            keys=fields.Str(
                required=True,
                validate=validate.OneOf(telegram_options)
            ),
            values=fields.Str(
                required=True
            ),
            required=True
        ),
        required=False
    )
    date = fields.Str(required=False)
    time = fields.Str(required=False)

    @validates('birthday')
    def validate_birthday(self, birthday):
        rx = re.compile(r'^([0-9]{2}/[0-9]{2}/[0-9]{4})$')
        match = rx.search(birthday)
        if not match:
            raise ValidationError("birthday not valid")
    
    @validates('date')
    def validate_date(self, date):
        rx = re.compile(r'^([0-9]{2}/[0-9]{2}/[0-9]{4})$')
        match = rx.search(date)
        if not match:
            raise ValidationError("date not valid")

    @validates('time')
    def validate_time(self, time):
        rx = re.compile(r'^([0-9]{2}:[0-9]{2})$')
        match = rx.search(time)
        if not match:
            raise ValidationError("time not valid")

    @post_load
    def create_processing(self, data, **kwargs):
        return Config(**data)

class Sender(object):

    def __init__(self, sender):
        self.sender = sender
        for key, value in sender.items():
            self.send_option = key
            self.sender_config = value

    def send_telegram(self, filename):
        bot = telegram.Bot(token=self.sender_config['token'])
        with open(filename, 'rb') as file:
            bot.send_document(chat_id=self.sender_config['chat_id'], document=file)
            file.close()

    def send(self, filename):
        if self.send_option == 'telegram':
            self.send_telegram(filename)

def main(config):
    gen = Generator()
    for conf in config:
        with open(conf) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            f.close()

        for user in data:
            data[user]['user'] = user
            schema = ConfigSchema()
            config = schema.load(data[user])
            print(vars(config))
            filename = gen.run(config)
            if not filename:
                return
            if config.sender:
                sender = Sender(config.sender)
                sender.send(filename)

    gen.close()

if __name__ == "__main__":
    os.environ['LC_ALL'] = "fr_FR.UTF-8"

    parser = arg.ArgumentParser(description="Générateur d'attestation de sortie - utilise le site officiel media.interieur.gouv.fr/deplacement-covid-19/")
    parser.add_argument(
        '-c',
        '--config',
        nargs='+',
        default=['config.yml'],
        help='le/les fichier(s) de configuration (defaut: config.yml)'
    )
    args = parser.parse_args()
    main(args.config)
