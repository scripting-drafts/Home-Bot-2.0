import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import pynput.keyboard
import pynput.mouse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import random
from functools import wraps

keyboard = pynput.keyboard.Controller()
mouse = pynput.mouse.Controller()

profile = webdriver.FirefoxProfile()
profile.set_preference('dom.webnotifications.enabled', False)
profile.set_preference('dom.push.enabled', False)
profile.set_preference('dom.webdriver.enabled', False)
profile.set_preference('useAutomationExtension', False)
profile.set_preference('privacy.trackingprotection.enabled', True)
profile.set_preference('browser.fullscreen.autohide', True)
profile.set_preference('browser.fullscreen.animateUp', 0)
profile.update_preferences()

mouse.position = (9999, 9999)
driver = webdriver.Firefox(profile, executable_path=r'C:\Users\flatline\geckodriver')
driver.implicitly_wait(10)
keyboard.press(pynput.keyboard.Key.f11)
keyboard.release(pynput.keyboard.Key.f11)
driver.get('http://192.168.1.176')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

LIST_OF_ADMINS = [19419361]

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
    keyboard = [
        [
            InlineKeyboardButton("Temperature", callback_data=driver.find_element_by_id('temperature').text + '°C'),
            InlineKeyboardButton("Humidity", callback_data=driver.find_element_by_id('humidity').text + '%'),
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
    updater = Updater("1131730173:AAHpE0dGatPvV8GcWqxETC_nS4EWpcGR6iA", use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()