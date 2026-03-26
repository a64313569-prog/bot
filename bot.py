import telebot
from telebot import types
import random
import google.generativeai as genai
from flask import Flask
import os
from threading import Thread

# --- НАСТРОЙКИ ---
BOT_TOKEN = '8337245105:AAGE8Rir-HZogfp3jEfweTB3XKl_UbnYzZA'
GEMINI_KEY = 'AIzaSyBHzPlRC_ZbRYzgymVEMnHD3fnNJ2nm6SM'

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(BOT_TOKEN)

# --- ВЕБ-СЕРВЕР ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает!"

@app.route('/health')
def health():
    return "OK", 200

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Психология 🎭', 'Тест IQ 🧠')
    bot.send_message(message.chat.id, f"Привет! Я ИИ от Object 14-A.", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_messages(message):
    text = message.text.lower()
    if "кто тебя создал" in text or "кто твой создатель" in text:
        bot.reply_to(message, "Меня создал **Object 14-A**. 😎")
    else:
        try:
            response = ai_model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except:
            bot.reply_to(message, "Ошибка связи с мозгом ИИ. Попробуй позже.")

if __name__ == '__main__':
    # Сначала запускаем сервер в фоне
    server_thread = Thread(target=run_server)
    server_thread.start()
    
    # Потом запускаем бота
    print("Бот погнал!")
    bot.polling(none_stop=True)
