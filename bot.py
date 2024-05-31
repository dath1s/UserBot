import telebot as tb
import configparser

from sender import sender
from db import create_request, add_message, add_delay, get_data

config = configparser.ConfigParser()
config.read(r'config.ini')

bot_token = config['tgbot']['bot_token']
bot = tb.TeleBot(bot_token)

action_keyboard = tb.types.ReplyKeyboardMarkup()
action_keyboard.row(tb.types.KeyboardButton("Начать рассылку"))

back_keyboard = tb.types.ReplyKeyboardMarkup()
back_keyboard.row(tb.types.KeyboardButton("Отмена"))


@bot.message_handler(commands=['start', 'restart'])
def welcome(message):
    bot.send_message(
        message.from_user.id,
        'Для начала работы нажмите на кнопку "Начать рассылку" ниже',
        parse_mode='html',
        reply_markup=action_keyboard
    )


@bot.message_handler(content_types=['text'])
def text(message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        if message.text in ["Начать рассылку", "Отмена"]:
            bot.send_message(
                user_id,
                'Для начала рассылки пришлите файл с указанием id пользователей или их юзернеймов(@user_example)\n'
                '<b>Пример приложен файлом ниже</b>',
                parse_mode='html',
                reply_markup=back_keyboard
            )
            bot.send_document(user_id, open(r'src/example.txt', mode='rb'))
            bot.register_next_step_handler(message, send_mes_text)


def send_mes_text(mes):
    user_id = mes.chat.id
    if mes.content_type == 'text' and mes.text == 'Отмена':
        bot.send_message(
            user_id,
            'Для начала работы нажмите на кнопку "Начать рассылку" ниже',
            parse_mode='html',
            reply_markup=action_keyboard
        )
    else:
        try:
            assert mes.content_type == 'document'

            file_info = bot.get_file(mes.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = fr'requestsFiles/{user_id}_{mes.document.file_name}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            create_request(user_id, file_path)

            bot.send_message(
                user_id,
                'Введите текст сообщения для рассылки',
                reply_markup=back_keyboard
            )
            bot.register_next_step_handler(mes, send_delay)

        except Exception:
            bot.send_message(
                user_id,
                "Возможно вы ошиблись при вводе. "
                "Требуется файл как в примере, а не текстовое сообщение. Повторите попытку пожалуйста.",
                reply_markup=back_keyboard
            )
            bot.register_next_step_handler(mes, send_mes_text)


def send_delay(mes):
    user_id = mes.chat.id
    if mes.content_type == 'text' and mes.text == 'Отмена':
        bot.send_message(
            user_id,
            'Для начала работы нажмите на кнопку "Начать рассылку" ниже',
            parse_mode='html',
            reply_markup=action_keyboard
        )
    else:
        try:
            assert mes.content_type == 'text'
            add_message(user_id, mes.text)

            bot.send_message(
                user_id,
                'Введите задержку между отправками сообщений в секундах'
                '(при указании дробных чисел используйте ТОЧКУ. Например: 0.5)',
                reply_markup=back_keyboard
            )
            bot.register_next_step_handler(mes, save_delay)

        except Exception:
            bot.send_message(
                user_id,
                "Возможно вы ошиблись при вводе. Требуется ввести текстовое сообщение. Повторите попытку пожалуйста.",
                reply_markup=back_keyboard
            )
            bot.register_next_step_handler(mes, send_delay)


def save_delay(mes):
    user_id = mes.chat.id
    if mes.content_type == 'text' and mes.text == 'Отмена':
        bot.send_message(
            user_id,
            'Для начала работы нажмите на кнопку "Начать рассылку" ниже',
            parse_mode='html',
            reply_markup=action_keyboard
        )
    else:
        # try:
        assert mes.content_type == 'text'
        add_delay(user_id, float(mes.text))
        bot.send_message(
            user_id,
            'Рассылка начата.\nПосле окончания рассылки, в чат будет выслан отчет по рассылке.',
            reply_markup=action_keyboard
        )
        filepath, messageText, delay = get_data(user_id)
        sender(
            filepath,
            messageText,
            delay,
            user_id
        )
        bot.send_document(user_id, open(f'отчет_{user_id}.json', mode='rb'))
        # except Exception as e:
        #     bot.send_message(
        #         user_id,
        #         f"Возможно вы ошиблись при вводе. Текст ошибки: {e}",
        #         reply_markup=back_keyboard
        #     )
        #     bot.register_next_step_handler(mes, save_delay)


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=1)
    bot.load_next_step_handlers()
    bot.polling(skip_pending=True)
