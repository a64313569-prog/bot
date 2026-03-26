import telebot
from telebot import types
import random
import google.generativeai as genai
import os

# --- НАСТРОЙКИ ---
BOT_TOKEN = '8337245105:AAGE8Rir-HZogfp3jEfweTB3XKl_UbnYzZA'
GEMINI_KEY = 'AIzaSyBHzPlRC_ZbRYzgymVEMnHD3fnNJ2nm6SM'

# Настройка ИИ
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)

# Промпт для характера ИИ
SYSTEM_PROMPT = (
    "Ты — харизматичный ИИ-помощник. Твой стиль: уверенный, немного загадочный, "
    "но дружелюбный. Используй эмодзи. Отвечай кратко и по делу."
)

# --- ТЕКСТОВЫЕ БЛОКИ ---
TEXT_PSYCHOLOGY = "<b>🎭 ОСНОВЫ ПСИХОЛОГИИ</b>\n1. Эффект ореола.\n2. EQ.\n3. Осознанность."
TEXT_MANIPULATION = "<b>⭐️ ИСКУССТВО ВЛИЯНИЯ</b>\n• Газлайтинг.\n• Нога в дверях.\n• Защита."
TEXT_RELATIONSHIPS = "<b>❤️ ПСИХОЛОГИЯ ОТНОШЕНИЙ</b>\n1. Типы привязанности.\n2. Границы.\n3. Правило 5/1."

# --- ЛОГИКА ТЕСТА IQ ---
BASE_QUESTIONS = [
    {"q": "У отца Мэри есть 5 дочерей: Нана, Нене, Нини, Ноно. Как зовут пятую?", "a": "Мэри"},
    {"q": "Что становится больше, если его поставить вверх ногами?", "a": "6"},
    {"q": "Сколько месяцев в году имеют 28 дней?", "a": "Все"},
    {"q": "Если у вас 3 яблока и вы забрали 2, сколько у вас яблок?", "a": "2"},
    {"q": "В семье 7 сыновей, и у каждого есть сестра. Сколько всего детей?", "a": "8"}
]

user_test_data = {}

def run_iq_test(message, q_index=0, score=0):
    chat_id = message.chat.id
    if q_index == 0:
        q_list = BASE_QUESTIONS.copy()
        random.shuffle(q_list)
        user_test_data[chat_id] = q_list
    
    current_qs = user_test_data.get(chat_id, BASE_QUESTIONS)
    if q_index < len(current_qs):
        msg = bot.send_message(chat_id, f"<b>Вопрос №{q_index + 1}:</b>\n\n{current_qs[q_index]['q']}", parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, check_iq_answer, q_index, score)
    else:
        bot.send_message(chat_id, f"<b>Тест завершен!</b>\nПравильно: {score} из {len(current_qs)}.", parse_mode='HTML')
        start(message)

def check_iq_answer(message, q_index, score):
    if message.text == '/start': return start(message)
    ans = message.text.strip().lower()
    if ans == user_test_data[message.chat.id][q_index]['a'].lower():
        score += 1
    run_iq_test(message, q_index + 1, score)

# --- ОБРАБОТКА КОМАНД ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('Психология 🎭', 'Манипуляции ⭐️', 'Отношения ❤️', 'Тест IQ 🧠', 'Главное меню 🏠')
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Я твой ИИ-проводник.", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_messages(message):
    text = message.text.lower()
    
    # 1. Проверка на создателя (ТВОЙ ЗАПРОС)
    if "кто тебя создал" in text or "кто твой создатель" in text or "кто твой папа" in text:
        # Можешь вписать сюда свою ссылку на канал или юзернейм
        bot.reply_to(message, "Меня создала легенда по имени **@Beelzebub_8** (Профессор). 😎")
        return

    # 2. Кнопки
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
    
    # 3. Интеллектуальный ответ ИИ
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            full_prompt = f"{SYSTEM_PROMPT}\nПользователь: {message.text}\nТвой ответ:"
            response = ai_model.generate_content(full_prompt)
            bot.reply_to(message, response.text)
        except Exception:
            bot.send_message(message.chat.id, "Используй меню ниже! 👇")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)