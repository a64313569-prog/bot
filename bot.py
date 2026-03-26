import telebot
from telebot import types
import random
import google.generativeai as genai
from flask import Flask
from threading import Thread
import os

# --- НАСТРОЙКИ ---
BOT_TOKEN = '8337245105:AAGE8Rir-HZogfp3jEfweTB3XKl_UbnYzZA'
GEMINI_KEY = 'AIzaSyBHzPlRC_ZbRYzgymVEMnHD3fnNJ2nm6SM'

# Настройка ИИ
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)

# --- МИНИ-СЕРВЕР ДЛЯ RENDER (ЧТОБЫ БЫЛО БЕСПЛАТНО) ---
app = Flask('')

@app.route('/')
def home():
    return "Бот запущен и работает!"

def run():
    # Render сам назначит порт, если его нет — используем 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- КОНТЕНТ ---
SYSTEM_PROMPT = "Ты — харизматичный ИИ-помощник, созданный Object 14-A. Твой стиль: уверенный, лаконичный, используй эмодзи."

TEXT_PSYCHOLOGY = "<b>🎭 ПСИХОЛОГИЯ</b>\n1. Эффект ореола: внешность обманчива.\n2. EQ: управляй эмоциями.\n3. Осознанность: живи моментом."
TEXT_MANIPULATION = "<b>⭐️ МАНИПУЛЯЦИИ</b>\n• Газлайтинг: «тебе показалось».\n• Нога в дверях: начни с малого.\n• Защита: личные границы."
TEXT_RELATIONSHIPS = "<b>❤️ ОТНОШЕНИЯ</b>\n1. Типы привязанности.\n2. Границы — это база.\n3. Правило 5/1."

BASE_QUESTIONS = [
    {"q": "У отца Мэри есть 5 дочерей: Нана, Нене, Нини, Ноно. Как зовут пятую?", "a": "Мэри"},
    {"q": "Что становится больше, если его поставить вверх ногами?", "a": "6"},
    {"q": "Сколько месяцев в году имеют 28 дней?", "a": "Все"},
    {"q": "Если у вас 3 яблока и вы забрали 2, сколько у вас яблок?", "a": "2"},
    {"q": "В семье 7 сыновей, и у каждого есть сестра. Сколько всего детей?", "a": "8"}
]

user_test_data = {}

# --- ЛОГИКА ТЕСТА ---
def run_iq_test(message, q_index=0, score=0):
    chat_id = message.chat.id
    if q_index == 0:
        q_list = BASE_QUESTIONS.copy()
        random.shuffle(q_list)
        user_test_data[chat_id] = q_list
    
    current_qs = user_test_data.get(chat_id)
    if q_index < len(current_qs):
        msg = bot.send_message(chat_id, f"<b>Вопрос №{q_index + 1}:</b>\n\n{current_qs[q_index]['q']}", parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, check_iq_answer, q_index, score)
    else:
        bot.send_message(chat_id, f"<b>Тест завершен!</b>\nРезультат: {score} из {len(current_qs)}.")
        start(message)

def check_iq_answer(message, q_index, score):
    if message.text == '/start': return start(message)
    ans = message.text.strip().lower()
    if ans == user_test_data[message.chat.id][q_index]['a'].lower():
        score += 1
    run_iq_test(message, q_index + 1, score)

# --- ОБРАБОТКА ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('Психология 🎭', 'Манипуляции ⭐️', 'Отношения ❤️', 'Тест IQ 🧠', 'Главное меню 🏠')
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! О чем поболтаем?", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_messages(message):
    text = message.text.lower()
    
    # ОТВЕТ ПРО СОЗДАТЕЛЯ
    if "кто тебя создал" in text or "кто твой создатель" in text:
        bot.reply_to(message, "Меня создала легенда по имени **Object 14-A** (Профессор). 😎")
        return

    if text == 'психология 🎭':
        bot.send_message(message.chat.id, TEXT_PSYCHOLOGY, parse_mode='HTML')
    elif text == 'манипуляции ⭐️':
        bot.send_message(message.chat.id, TEXT_MANIPULATION, parse_mode='HTML')
    elif text == 'отношения ❤️':
        bot.send_message(message.chat.id, TEXT_RELATIONSHIPS, parse_mode='HTML')
    elif text == 'тест iq 🧠':
        run_iq_test(message)
    elif text == 'главное меню 🏠':
        start(message)
    else:
        # РАБОТА ИИ
        try:
            prompt = f"{SYSTEM_PROMPT}\nПользователь: {message.text}"
            response = ai_model.generate_content(prompt)
            bot.reply_to(message, response.text)
        except:
            bot.send_message(message.chat.id, "Я задумался... Попробуй меню!")

if __name__ == '__main__':
    keep_alive() # Запуск веб-сервера
    print("Бот запущен!")
    bot.polling(none_stop=True)
