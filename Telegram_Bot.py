import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import pynput.keyboard
import pynput.mouse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import random
from functools import wraps

keyboard = pynput.keyboard.Controller()
mouse = pynput.mouse.Controller()

options = Options()
options.add_argument('--headless')
options.set_preference('dom.webnotifications.enabled', False)
options.set_preference('dom.push.enabled', False)
options.set_preference('dom.webdriver.enabled', False)
options.set_preference('useAutomationExtension', False)
options.set_preference('privacy.trackingprotection.enabled', True)

options.set_preference('browser.cache.disk.enable', False)
options.set_preference('browser.cache.memory.enable', False)
options.set_preference('browser.cache.offline.enable', False)
options.set_preference('network.http.use-cache', False)

mouse.position = (9999, 9999)
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(10)
keyboard.press(pynput.keyboard.Key.f11)
keyboard.release(pynput.keyboard.Key.f11)
driver.get('http://192.168.1.33')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

LIST_OF_ADMINS = ['UNQUOTED USER IDs']

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped

@restricted
def start(update, context):
    '''DHT11/DHT22'''
    keyboard = [
        [
            InlineKeyboardButton("Temperature", callback_data=driver.find_element(By.ID, 'temperature').text + '°C'),
            InlineKeyboardButton("Humidity", callback_data=driver.find_element(By.ID, 'humidity').text + '%'),
        ],
        [InlineKeyboardButton("Flip coin", callback_data=random.choice(['heads', 'tails']))],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Get by', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=query.data)


def main():
    updater = Updater("TOKEN", use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
