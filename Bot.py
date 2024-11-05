import logging
import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import random
import threading
# Включаем логирование
from datetime import datetime
import re
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальные переменные для хранения данных пользователей и рынка
user_data = {}
marketplace = []
# Define the bank file path
BANK_FILE = 'bank.json'


def load_bank_data():
    if os.path.exists(BANK_FILE):
        with open(BANK_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}


# Function to save bank data
def save_bank_data(bank_data):
    with open(BANK_FILE, 'w') as file:
        json.dump(bank_data, file)


# Функции для сохранения и загрузки данных
def save_data():
    try:
        with open('user_data.json', 'w') as file:
            json.dump(user_data, file, indent=4)
            logger.info("Данные пользователей успешно сохранены: %s", user_data)
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных пользователей: {e}")


def save_market():
    try:
        with open('marketplace.json', 'w') as file:
            json.dump(marketplace, file, indent=4)
        logger.info("Данные рынка успешно сохранены.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных рынка: {e}")


def load_data():
    global user_data
    try:
        with open('user_data.json', 'r') as file:
            loaded_data = json.load(file)
            # Преобразуем значения монет в int
            user_data = {int(user_id): data for user_id, data in loaded_data.items()}
            logger.info("Данные пользователей успешно загружены: %s", user_data)
    except FileNotFoundError:
        user_data = {}
        logger.warning("Файл с данными пользователей не найден. Создание нового файла.")
    except Exception as e:
        user_data = {}
        logger.error(f"Ошибка при загрузке данных пользователей: {e}")


def load_market():
    global marketplace
    try:
        with open('marketplace.json', 'r') as file:
            marketplace = json.load(file)
    except FileNotFoundError:
        marketplace = []


# Функции для команд модерации
def kick(update: Update, context: CallbackContext) -> None:
    user = update.message.reply_to_message.from_user
    context.bot.kick_chat_member(update.message.chat_id, user.id)
    update.message.reply_text(f'Пользователь {user.first_name} был исключен.')
    if user.id not in user_data:
        user_data[user.id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': []}
    user_data[user.id]['bans'] += 1
    save_data()
# сука я не понимаю откуда вы такие ебанаты что ему верите. он просто рофлит

def ban(update: Update, context: CallbackContext) -> None:
    user = update.message.reply_to_message.from_user
    context.bot.ban_chat_member(update.message.chat_id, user.id)
    update.message.reply_text(f'Пользователь {user.first_name} был забанен.')
    if user.id not in user_data:
        user_data[user.id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': []}
    user_data[user.id]['bans'] += 1
    save_data()


def unban(update: Update, context: CallbackContext) -> None:
    user_id = int(context.args[0])
    context.bot.unban_chat_member(update.message.chat_id, user_id)
    update.message.reply_text(f'Пользователь с ID {user_id} был разбанен.')


def mute(update: Update, context: CallbackContext) -> None:
    user = update.message.reply_to_message.from_user
    context.bot.restrict_chat_member(update.message.chat_id, user.id,
                                     permissions=ChatPermissions(can_send_messages=False))
    update.message.reply_text(f'Пользователь {user.first_name} был замьючен.')
    if user.id not in user_data:
        user_data[user.id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': []}
    user_data[user.id]['mutes'] += 1
    save_data()


def unmute(update: Update, context: CallbackContext) -> None:
    user = update.message.reply_to_message.from_user
    context.bot.restrict_chat_member(update.message.chat_id, user.id,
                                     permissions=ChatPermissions(can_send_messages=True))
    update.message.reply_text(f'Пользователь {user.first_name} был размьючен.')


# Функции для развлечений и мини-игр
def roll_dice(update: Update, context: CallbackContext) -> None:
    number = random.randint(1, 6)
    update.message.reply_text(f'Выпало число: {number}')


def flip_coin(update: Update, context: CallbackContext) -> None:
    result = 'орел' if random.random() < 0.5 else 'решка'
    update.message.reply_text(f'Монетка упала: {result}')


def guess_number(update: Update, context: CallbackContext) -> None:
    number = random.randint(1, 10)
    update.message.reply_text(f'Я загадал число от 1 до 10. Попробуй угадать!')
    context.user_data['number'] = number


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет, я чат-бот для развлечения. мой исходный код')


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        '👢 /kick - Исключить пользователя\n'
        '🚫 /ban - Забанить пользователя\n'
        '⛔️ /unban - Разбанить пользователя\n'
        '🔇 /mute - Замьютить пользователя\n'
        '🔊 /unmute - Размьютить пользователя\n'
        '🎲 /roll_dice - Бросить кубик\n'
        '🪙 /flip_coin - Подбросить монетку\n'
        '📢 /everyone - Упомянуть всех\n'
        '💰 /ferma - Получить деньги раз в 4 часа\n'
        '📊 /stats - Показать статистику\n'
        '🛒 /prodavat - Продать предмет (использование: /prodavat Машина 1000)\n'
        '🏪 /rynok - Показать рынок\n'
        '💸 /send - Перевести деньги пользователю (использование: /send 100 (айди человека)\n'
        '❓ /help - Помощь\n'
        '👀 /grabit - Ограбить человека (использование: /grabit (айди человека)\n'
        '📡 /check - Проверить бота на пинг\n'
        '🔍 /probit - Пробить человека по базе бота (использование: /probit (айди человека)\n'
        '🎰 /kazino - Обычное казино(использование: /kazino (ставка)\n'
        '🔴 /ruletka - Казино угадай число (использование: /ruletka (ставка) (ваше число)\n'
        '💸/vbank - Положить деньги в банк (использование: /vbank (сумма)\n'
        '💸/izbank - взять деньги из банка (использование: /izbank (сумма)\n'
        '📊/bank - Посмотреть деньги в банке\n'
    )


def kazino_X(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    if user_id not in user_data:
        user_data[user_id] = {'money': 100}

    try:
        # Получаем ставку и число предположения
        bet_amount, guess_number = map(int, context.args)
        if bet_amount <= 0:
            update.message.reply_text('❌ Ставка должна быть положительным числом.')
            return
        if user_data[user_id]['money'] < bet_amount:
            update.message.reply_text('🚫 У вас недостаточно денег для совершения этой ставки.')
            return
        if guess_number < 1 or guess_number > 10:
            update.message.reply_text('❗ Предположение должно быть числом от 1 до 10.')
            return

        # Загадываем число от 1 до 10
        secret_number = random.randint(1, 10)

        if guess_number == secret_number:
            # Если число предположения совпадает с загаданным числом, выигрыш увеличивается в три раза
            win_amount = bet_amount * 3
            user_data[user_id]['money'] += win_amount
            update.message.reply_text(
                f'🎉 Поздравляем! Вы угадали число и выиграли {win_amount} монет. Теперь у вас {user_data[user_id]["money"]} монет.')
        else:
            user_data[user_id]['money'] -= bet_amount
            update.message.reply_text(
                f'😔 К сожалению, загаданное число было {secret_number}. Вы проиграли {bet_amount} монет. Теперь у вас {user_data[user_id]["money"]} монет.')

        save_data()  # Сохраняем данные о пользователях после завершения игры
    except (IndexError, ValueError):
        update.message.reply_text('❓ Использование: /ruletka [ставка] [предположение от 1 до 10]')


def everyone(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    members = context.bot.get_chat_administrators(chat_id)
    mention_text = "📢 Упоминаю всех участников:\n"
    for member in members:
        user = member.user
        mention_text += f"@{user.username or user.first_name}, "
    update.message.reply_text(mention_text.strip(', '))

def farm(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id
    if user_id not in user_data:
        user_data[user_id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': []}

    current_time = time.time()
    last_farm_time = user_data[user_id]['last_farm']
    if current_time - last_farm_time >= 2 * 3600:
        ferma = random.randint(1, 150)
        user_data[user_id]['money'] += ferma
        user_data[user_id]['last_farm'] = current_time
        update.message.reply_text(f'🌾 Круто! Вы получили {ferma} монет.')
        save_data()
    else:
        time_left = 2 * 3600 - (current_time - last_farm_time)
        hours, remainder = divmod(time_left, 3600)
        minutes, seconds = divmod(remainder, 60)
        update.message.reply_text(
            f'⏳ Вы уже получали монеты недавно. Попробуйте через {int(hours)}ч {int(minutes)}м {int(seconds)}с.')


# Пример user_data, это должно быть определено и сохранено где-то в вашем коде

def grabit(update: Update, context: CallbackContext) -> None:
    sender = update.message.from_user
    sender_id = sender.id

    if sender_id not in user_data:
        user_data[sender_id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': [], 'last_grabit': 0}

    try:
        # Проверяем, что аргументы переданы корректно
        if len(context.args) < 1:
            update.message.reply_text('Использование: /grabit [ID_пользователя]')
            return

        recipient_id = int(context.args[0])

        # Проверяем, существует ли получатель
        try:
            recipient = context.bot.get_chat_member(update.message.chat_id, recipient_id).user
        except:
            update.message.reply_text('Пользователь не найден.')
            return

        if recipient_id not in user_data:
            user_data[recipient_id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': [], 'last_grabit': 0}

        current_time = time.time()
        if current_time - user_data[sender_id].get('last_grabit', 0) < 3700:  # 2 часа = 7200 секунд
            update.message.reply_text('Вы можете использовать эту команду только раз в 3700 сек.')
            return

        if user_data[recipient_id]['money'] > 0:
            stolen_amount = random.randint(1, user_data[recipient_id]['money'])
            user_data[sender_id]['money'] += stolen_amount
            user_data[recipient_id]['money'] -= stolen_amount
            user_data[sender_id]['last_grabit'] = current_time
            update.message.reply_text(f'💰 Вы ограбили пользователя с ID {recipient_id} на {stolen_amount} монет.')
            save_data()
        else:
            update.message.reply_text('У пользователя нет денег для ограбления.')
    except (IndexError, ValueError):
        update.message.reply_text('Использование: /grabit [ID_пользователя]')
    except Exception as e:
        update.message.reply_text(f'Произошла ошибка: {str(e)}')


def user_info(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id
    if user_id not in user_data:
        user_data[user_id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': [], 'businesses': []}

    user_stats = user_data[user_id]
    items = ", ".join(user_stats.get('items', [])) if 'items' in user_stats else "нет предметов"

    businesses = user_stats.get('businesses', [])
    if businesses:
        business_names = [business['name'] for business in
                          businesses]  # Assuming each business is a dict with a 'name' key
        business_list = ", ".join(business_names)
    else:
        business_list = "нет бизнесов"

    update.message.reply_text(
        f'👤 Статистика пользователя {user.first_name}:\n'
        f'🔇 Мьюты: {user_stats.get("mutes", 0)}\n'
        f'🚫 Баны: {user_stats.get("bans", 0)}\n'
        f'💸 Деньги: {user_stats.get("money", 0)}\n'
        f'🎁 Предметы: {items}\n'

    )

def sell_item(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id
    if user_id not in user_data:
        user_data[user_id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': []}

    try:
        item_name = context.args[0]
        item_price = int(context.args[1])
        marketplace.append({'seller_id': user_id, 'item': item_name, 'price': item_price})
        update.message.reply_text(f'🛒 Предмет "{item_name}" добавлен на рынок за {item_price} монет.')
        save_market()
    except (IndexError, ValueError):
        update.message.reply_text('Использование: /prodavat [название предмета] [цена]')


def show_market(update: Update, context: CallbackContext) -> None:
    if not marketplace:
        update.message.reply_text('📦 Рынок пуст!')
        return

    for item in marketplace:
        seller_id = item.get("seller_id", None)
        if seller_id is not None:
            button = InlineKeyboardButton(text=f'Купить за {item["price"]}',
                                          callback_data=f'buy_{item["item"]}_{seller_id}')
            keyboard = InlineKeyboardMarkup([[button]])
            update.message.reply_text(f'🏪 Владелец: {seller_id}\nПредмет: {item["item"]}\nЦена: {item["price"]} монет',
                                      reply_markup=keyboard)


def buy_item(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = query.data.split('_')

    if len(data) < 3:
        query.message.reply_text('❌ Некорректные данные для выполнения покупки.')
        return

    try:
        seller_id = int(data[2])
    except ValueError:
        query.message.reply_text('❌ Ошибка: неверный идентификатор продавца.')
        return

    buyer = query.from_user
    buyer_id = buyer.id

    for item in marketplace:
        if item['item'] == data[1] and item['seller_id'] == seller_id:
            if buyer_id not in user_data:
                user_data[buyer_id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': []}

            if user_data[buyer_id]['money'] >= item['price']:
                user_data[buyer_id]['money'] -= item['price']
                user_data[buyer_id]['items'].append(item['item'])
                user_data[seller_id]['money'] += item['price']
                marketplace.remove(item)
                query.message.reply_text(f'🎉 Вы купили "{item["item"]}" за {item["price"]} монет.')
                save_data()
                save_market()
            else:
                query.message.reply_text('❌ У вас недостаточно денег для покупки этого предмета.')
            return
    query.message.reply_text('❌ Этот предмет уже был куплен или удален.')


def send_money(update: Update, context: CallbackContext) -> None:
    sender = update.message.from_user
    sender_id = sender.id
    if sender_id not in user_data:
        user_data[sender_id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': []}

    try:
        if len(context.args) < 2:
            update.message.reply_text('Использование: /send [сумма] [ID_пользователя]')
            return

        amount = int(context.args[0])
        recipient_id = int(context.args[1])

        try:
            recipient = context.bot.get_chat_member(update.message.chat_id, recipient_id).user
        except:
            update.message.reply_text('Пользователь не найден.')
            return

        if recipient_id not in user_data:
            user_data[recipient_id] = {'mutes': 0, 'bans': 0, 'money': 0, 'last_farm': 0, 'items': []}

        if user_data[sender_id]['money'] >= amount:
            user_data[sender_id]['money'] -= amount
            user_data[recipient_id]['money'] += amount
            update.message.reply_text(f'💸 Вы перевели {amount} монет пользователю с ID {recipient_id}.')
            save_data()
        else:
            update.message.reply_text('❌ У вас недостаточно денег для перевода.')
    except (IndexError, ValueError):
        update.message.reply_text('Использование: /send [сумма] [ID_пользователя]')
    except Exception as e:
        update.message.reply_text(f'❌ Произошла ошибка: {str(e)}')


def probit(update: Update, context: CallbackContext) -> None:
    if context.args:
        user_id = context.args[0]
        try:
            user_id = int(user_id)
            if user_id in user_data:
                user_stats = user_data[user_id]
                username = context.bot.get_chat(user_id).username or 'Нет имени пользователя'

                # Retrieve items and businesses
                items = user_stats.get('items', [])
                item_count = len(items)

                businesses = user_stats.get('businesses', [])
                business_names = [business['name'] for business in businesses] if businesses else []
                business_count = len(businesses)

                update.message.reply_text(f'🔍 Имя пользователя: @{username}')
                update.message.reply_text(
                    f'📊 Статистика пользователя @{username}\n'
                    f'💸 Деньги: {user_stats.get("money", 0)}\n'
                    f'🔇 Количество мутов: {user_stats.get("mutes", 0)}\n'
                    f'🚫 Количество банов: {user_stats.get("bans", 0)}\n'
                    f'🎁 Количество предметов: {item_count}\n'

                )
            else:
                update.message.reply_text('Пользователь не найден.')
        except ValueError:
            update.message.reply_text('Неверный ID пользователя.')
    else:
        update.message.reply_text('Пожалуйста, предоставьте ID пользователя.')

def check(update: Update, context: CallbackContext) -> None:
    start_time = time.time()
    message = update.message.reply_text('На месте! ✅')
    end_time = time.time()

    # Вычисление пинга в миллисекундах
    ping = (end_time - start_time) * 1000
    message.edit_text(f'На месте! ✅\nПинг: {ping:.2f} ms')


def kazino(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    if user_id not in user_data:
        user_data[user_id] = {'money': 100}

    try:
        bet_amount = int(context.args[0])
        if bet_amount <= 0:
            update.message.reply_text('Ставка должна быть положительным числом.')
            return
        if user_data[user_id]['money'] < bet_amount:
            update.message.reply_text('У вас недостаточно денег для совершения этой ставки.')
            return

        # "Бросаем монету" - генерируем случайное число 0 или 1
        result = random.randint(0, 1)

        if result == 1:
            user_data[user_id]['money'] += bet_amount  # Если выигрыш, добавляем ставку к деньгам пользователя
            update.message.reply_text(
                f'Поздравляем! Вы выиграли {bet_amount} монет. Теперь у вас {user_data[user_id]["money"]} монет.')
        else:
            user_data[user_id]['money'] -= bet_amount  # Если проигрыш, вычитаем ставку из денег пользователя
            update.message.reply_text(
                f'К сожалению, вы проиграли {bet_amount} монет. Теперь у вас {user_data[user_id]["money"]} монет.')
        save_data()  # Сохраняем данные о пользователях после завершения игры
    except (IndexError, ValueError):
        update.message.reply_text('Использование: /kazino [ставка]')



def give(update, context):
    # Получаем сумму и айди пользователя из сообщения
    args = context.args
    if len(args) != 2:
        update.message.reply_text('Использование: /give [сумма] [айди пользователя]')
        return

    try:
        amount = float(args[0])
        user_id = int(args[1])
    except ValueError:
        update.message.reply_text('Пожалуйста, укажите правильную сумму и айди пользователя.')
        return

    # Проверяем, может ли пользователь использовать эту команду
    allowed_user_id = 6468904613  # Укажите нужный айди пользователя здесь
    if update.message.from_user.id != allowed_user_id:
        update.message.reply_text('Вы не имеете права использовать эту команду.')
        return

    # Выдача суммы указанному пользователю
    if user_id in user_data:
        user_data[user_id]['money'] += amount
        update.message.reply_text(f'Сумма {amount} успешно выдана пользователю с айди {user_id}.')
        save_data()
    else:
        update.message.reply_text('Пользователь не найден.')


# Команда для отображения баланса в банке
def bank(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    bank_data = load_bank_data()
    if str(user_id) in bank_data:
        bank_balance = bank_data[str(user_id)]
        update.message.reply_text(f'🏦 Ваш баланс в банке: {bank_balance} монет.')
    else:
        update.message.reply_text('🏦 У вас нет денег в банке.')


def izbank(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    if user_id not in user_data:
        user_data[user_id] = {'money': 100}

    try:
        amount = int(context.args[0])
        if amount <= 0:
            update.message.reply_text('❌ Сумма должна быть положительным числом.')
            return

        bank_data = load_bank_data()
        if str(user_id) not in bank_data or bank_data[str(user_id)] < amount:
            update.message.reply_text('🚫 У вас недостаточно денег в банке для вывода.')
            return

        user_data[user_id]['money'] += amount
        bank_data[str(user_id)] -= amount
        save_bank_data(bank_data)

        update.message.reply_text(
            f'💵 Вы вывели {amount} монет из банка. Теперь у вас {user_data[user_id]["money"]} монет на руках и {bank_data[str(user_id)]} монет в банке.')

    except (IndexError, ValueError):
        update.message.reply_text('❓ Использование: /izbank [сумма]')


def id(update: Update, context: CallbackContext) -> None:
    # Получаем ID пользователя, на сообщение которого ответил бот
    user_id = update.message.reply_to_message.from_user.id if update.message.reply_to_message else update.message.from_user.id
    # Отправляем ID пользователя
    update.message.reply_text(f'User ID: {user_id}')


def vbank(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    if user_id not in user_data:
        user_data[user_id] = {'money': 100}

    try:
        amount = int(context.args[0])
        if amount <= 0:
            update.message.reply_text('❌ Сумма должна быть положительным числом.')
            return
        if user_data[user_id]['money'] < amount:
            update.message.reply_text('🚫 У вас недостаточно денег для перевода.')
            return

        bank_data = load_bank_data()
        if str(user_id) not in bank_data:
            bank_data[str(user_id)] = 0

        user_data[user_id]['money'] -= amount
        bank_data[str(user_id)] += amount
        save_bank_data(bank_data)
        save_data()

        update.message.reply_text(
            f'💰 Вы перевели {amount} монет в банк. Теперь у вас {user_data[user_id]["money"]} монет на руках и {bank_data[str(user_id)]} монет в банке.')

    except (IndexError, ValueError):
        update.message.reply_text('❓ Использование: /vbank [сумма]')


def main() -> None:
    load_data()
    load_market()

    updater = Updater("Token")
    dispatcher = updater.dispatcher

    # Добавляем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("kick", kick))
    dispatcher.add_handler(CommandHandler("ban", ban))
    dispatcher.add_handler(CommandHandler("unban", unban))
    dispatcher.add_handler(CommandHandler("mute", mute))
    dispatcher.add_handler(CommandHandler("unmute", unmute))
    dispatcher.add_handler(CommandHandler("roll_dice", roll_dice))
    dispatcher.add_handler(CommandHandler("flip_coin", flip_coin))
    dispatcher.add_handler(CommandHandler("guess_number", guess_number))
    dispatcher.add_handler(CommandHandler("everyone", everyone))
    dispatcher.add_handler(CommandHandler("ferma", farm))
    dispatcher.add_handler(CommandHandler("stats", user_info))
    dispatcher.add_handler(CommandHandler("prodavat", sell_item))
    dispatcher.add_handler(CommandHandler("rynok", show_market))
    dispatcher.add_handler(CallbackQueryHandler(buy_item, pattern='^buy_'))
    dispatcher.add_handler(CommandHandler("send", send_money))
    dispatcher.add_handler(CommandHandler("probit", probit))
    dispatcher.add_handler(CommandHandler("check", check))
    dispatcher.add_handler(CommandHandler("kazino", kazino))
    dispatcher.add_handler(CommandHandler("grabit", grabit))
    dispatcher.add_handler(CommandHandler("ruletka", kazino_X))
    dispatcher.add_handler(CommandHandler("give", give))
    dispatcher.add_handler(CommandHandler("izbank", izbank))
    dispatcher.add_handler(CommandHandler("vbank", vbank))
    dispatcher.add_handler(CommandHandler("bank", bank))
    dispatcher.add_handler(CommandHandler('id', id))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()