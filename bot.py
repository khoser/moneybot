# import json
import os
from uuid import uuid4 as guid
import telebot
from telebot.types import Message
from telebot import types
import PocketClass


TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
ids = [int(os.environ.get('ID_KTU')), int(os.environ.get('ID_ERO'))]
pcs = PocketClass.Pockets('MyPythonMoney.db')
URL = os.environ.get('URL')
LOGIN = os.environ.get('LOGIN')
PASS = os.environ.get('PASS')
pcs.set_settings(URL, LOGIN, PASS)
action_stack = {}
for mid in ids:
    action_stack[mid] = {}


@bot.message_handler(commands=['start', 'help', 'test'])
def first_run(message: Message):
    bot.reply_to(message, 'Hi')


@bot.message_handler(commands=['report'])
def report(message: Message):
    if message.from_user.id not in ids:
        # bot.reply_to(message, message.from_user.id)
        bot.send_message(ids[0], f'{message.from_user.id}\n{message.chat.id}')
        bot.forward_message(ids[0], message.chat.id, message.message_id)
        return
    pcs.fill_from_db()
    pcs.get_data()
    # data = pcs.get_info()
    # data = '<pre>12345678901234567890123456789012345678901234567890</pre>'
    data = pcs.get_html_fin()
    bot.send_message(message.chat.id, data, parse_mode='HTML')


@bot.message_handler(commands=['reg'])
def reg(message: Message):
    if message.from_user.id not in ids:
        # bot.reply_to(message, message.from_user.id)
        bot.send_message(ids[0], f'{message.from_user.id}\n{message.chat.id}')
        bot.forward_message(ids[0], message.chat.id, message.message_id)
        return

    pcs.get_data()
    action_stack[message.from_user.id].clear()

    markup = types.InlineKeyboardMarkup()
    for simple in reversed(pcs.actions_names):
        uid = str(guid())
        action_stack[message.from_user.id][uid] = [pcs.actions_names[simple]]
        markup.add(types.InlineKeyboardButton(pcs.actions_names[simple], callback_data=uid))
    # markup.add(types.InlineKeyboardButton("Доход", callback_data='in'))
    # markup.add(types.InlineKeyboardButton("Перемещение", callback_data='between'))

    # markup = types.ReplyKeyboardMarkup()
    # markup.text = 'txt'
    # markup.row('a', 'v')
    # markup.row('c', 'd', 'e')
    # markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Действие:", reply_markup=markup)


@bot.callback_query_handler(func=lambda query: True)
def process_callback_1(query: types.CallbackQuery):
    # print(query.data)
    main_data = action_stack[query.from_user.id][query.data]
    # print(main_data)
    action_stack[query.from_user.id].clear()
    caption = "."
    markup = None
    if main_data[0] == 'Between':
        markup = types.InlineKeyboardMarkup()
        caption = "Перемещение:"
        if 1 <= len(main_data) <= 2:
            for simple in pcs.pockets:
                s = main_data.copy()
                s.append(simple)
                # print(s)
                uid = str(guid())
                action_stack[query.from_user.id][uid] = s
                markup.add(types.InlineKeyboardButton(simple.name, callback_data=uid))
                # bot.send_message(query.message.chat.id, caption, reply_markup=markup)
        if len(main_data) == 3:
            markup = None
            uid = 0
            action_stack[query.from_user.id][uid] = main_data
            caption = f"Введите сумму перемещения из {main_data[1]}\nв {main_data[2]}:"
    if main_data[0] == 'Out':
        markup = types.InlineKeyboardMarkup()
        caption = "Расход:"
        if len(main_data) == 1:
            for simple in pcs.pockets:
                s = main_data.copy()
                s.append(simple)
                # print(s)
                uid = str(guid())
                action_stack[query.from_user.id][uid] = s
                markup.add(types.InlineKeyboardButton(simple.name, callback_data=uid))
                # bot.send_message(query.message.chat.id, caption, reply_markup=markup)
        if len(main_data) == 2:
            for simple in pcs.out_items:
                s = main_data.copy()
                s.append(simple)
                uid = str(guid())
                action_stack[query.from_user.id][uid] = s
                markup.add(types.InlineKeyboardButton(simple.name, callback_data=uid))
        if len(main_data) == 3:
            markup = None
            uid = 0
            action_stack[query.from_user.id][uid] = main_data
            caption = f"Введите сумму расхода из {main_data[1]}\nв {main_data[2]}:"
    if main_data[0] == 'In':
        markup = types.InlineKeyboardMarkup()
        caption = "Доход:"
        if len(main_data) == 1:
            for simple in pcs.pockets:
                s = main_data.copy()
                s.append(simple)
                # print(s)
                uid = str(guid())
                action_stack[query.from_user.id][uid] = s
                markup.add(types.InlineKeyboardButton(simple.name, callback_data=uid))
                # bot.send_message(query.message.chat.id, caption, reply_markup=markup)
        if len(main_data) == 2:
            for simple in pcs.in_items:
                s = main_data.copy()
                s.append(simple)
                uid = str(guid())
                action_stack[query.from_user.id][uid] = s
                markup.add(types.InlineKeyboardButton(simple.name, callback_data=uid))
        if len(main_data) == 3:
            markup = None
            uid = 0
            action_stack[query.from_user.id][uid] = main_data
            caption = f"Введите сумму дохода в {main_data[1]}\nпо {main_data[2]}:"
    bot.send_message(query.message.chat.id, caption, reply_markup=markup)
    # print(type(query))
    # print(query.data)  # это callback_data

# @bot.callback_query_handler(lambda query: query.data in ["in", "between"])
# def process_callback_2(query):
#   pass

# @bot.inline_handler(lambda query: query.query == 'text')
# def query_text(inline_query):
#     # Query message is text
#     pass
#
#
# @bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
# def test_chosen(chosen_inline_result):
#     # Process all chosen_inline_result.
#     print(chosen_inline_result)


@bot.message_handler(func=lambda message: True)
def some_func(message: Message):
    if message.from_user.id not in ids:
        # bot.reply_to(message, message.from_user.id)
        bot.send_message(ids[0], f'{message.from_user.id}\n{message.chat.id}')
        bot.forward_message(ids[0], message.chat.id, message.message_id)
        return
    if len(action_stack[message.from_user.id]) > 0:
        # print(action_stack)
        main_data = action_stack[message.from_user.id][0]
        main_data.append(message.text)
        msg_text = len(main_data)
        if main_data[0] == 'Between':
            if len(main_data) == 4:
                msg_text = f'Выполняем операцию {main_data[0]}\n {main_data[3]}\n' \
                           f' из {main_data[1].name}\n в {main_data[2].name}' \
                           f'\nВведите комментарий к операции'
            elif len(main_data) == 5:
                pcs.action_between(main_data[1], main_data[2], float(main_data[3]), main_data[4])
                msg_text = 'Операция учтена'
                pcs.post_data()
        if main_data[0] == 'Out':
            if len(main_data) == 4:
                msg_text = f'Выполняем операцию {main_data[0]}\n {main_data[3]}\n' \
                           f' из {main_data[1].name}\n по статье {main_data[2].name}' \
                           f'\nВведите комментарий к операции'
            elif len(main_data) == 5:
                pcs.action_out(main_data[1], main_data[2], float(main_data[3]), 0, main_data[4])
                msg_text = 'Операция учтена'
                pcs.post_data()
        if main_data[0] == 'In':
            if len(main_data) == 4:
                msg_text = f'Выполняем операцию {main_data[0]}\n {main_data[3]}\n' \
                           f' из {main_data[1].name}\n по статье {main_data[2].name}' \
                           f'\nВведите комментарий к операции'
            elif len(main_data) == 5:
                pcs.action_in(main_data[1], main_data[2], float(main_data[3]), 0, main_data[4])
                msg_text = 'Операция учтена'
                pcs.post_data()

        bot.reply_to(message, msg_text)
        return

    bot.reply_to(message, 'Что-то непонятное :(')


if __name__ == '__main__':
    bot.polling()


# while True:
#     try:
#         bot.polling()
#     finally:
#         pass
