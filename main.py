from calendar import week
from config import *
import json
from flask import Flask, request
import os
import requests
import re
from requests_ntlm import HttpNtlmAuth
import time
import pandas as pd
from pandas import ExcelFile, json_normalize
import datetime
# Файл с бекендом
import backend

# Файл с обновлением расписания
import parse
server = Flask(__name__)

#TODO Сделать лог систему

# Antiflood
last_time = {}


@bot.message_handler(commands=['start', 'help'])
def startbot(message):
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    inlineMarkup = telebot.types.InlineKeyboardMarkup();
    inlineMarkup.add(telebot.types.InlineKeyboardButton(text='Разработчик в ВК', url='https://vk.com/igor69696'))
    
    """Старт бота
    Args:
        message (string): Сообщение от пользователя
    """
    bot.send_message(message.from_user.id,
                     "Здравствуйте, данный бот поможет вам быстро и удобно узнать расписание занятий Петровского колледжа.\n"
                     "\nНиже представлен ряд команд, которыми <strong>вы можете воспользоваться через <i>меню</i> или <i>нажав на выбранную команду</i> ниже:</strong>\n"
                     "\n/start или /help - Выводит список доступных команд;\n\n/today - Расписание и замены(если есть) на текущий день;"
                     "\n\n/next_day - Расписание и замены(если есть) на следующий день;\n\n/all_days - Расписание на все две недели(числитель и знаменатель);\n\n/by_day - Расписание по конкретному дню;\n\n/by_week - Расписание на текущую неделю;\n\n/internship - Выводит группы на практике и их сроки практики;"
                     "\n\n/week - Узнать числитель сейчас или знаменатель;\n\n/all_changes - Выводит все замены на следующий день. <strong>Для получения замен по поисковому запросу (по номеру группы и т.д.) пользуйтесь следующей командой!</strong>\n\n/changes - Выводит замены <i>по поисковому запросу</i> на следующий, текущий или прошлый день;"
                     "\n\n/subscribe - Подписаться/отписаться на рассылку расписания. (Расписание высылается <i>на следующую неделю!</i> Отправляется 1 раз в неделю в воскресенье).\n\n", parse_mode='HTML', reply_markup=inlineMarkup)


@bot.message_handler(commands=['admin_rassilka'])
def send_rassilka(message):
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]
    if message.from_user.id ==123:
        backend.PetroBot.sendScheduleToSubs()
    else:
        return 0 
    
@bot.message_handler(commands=['admin_statistic'])
def send_rassilka(message):
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]
    if message.from_user.id ==123:
        bot.send_message('123', 'На рассылку подписалось: ')
        bot.send_message('123', Subscribe().count())
    else:
        return 0 
    


@bot.message_handler(commands=['internship'])
def groupsInternship(message):

    """Выводит группы на практике

    Args:
        message (string): Сообщение от пользователя
    """
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    bot.send_message(message.from_user.id,
                     "<strong>Группы на практике: </strong>", parse_mode="HTML")
    # обращается к функции которая парсит группы на практике с портала
    try:
        bot.send_message(message.from_user.id, parse.PetroSchedule(username, password).internship(), parse_mode="HTML", reply_markup=telebot.types.ReplyKeyboardRemove())
    except:
        bot.send_message(message.from_user.id, "Не удалось получить группы на практике, попробуйте позже", parse_mode="HTML", reply_markup=telebot.types.ReplyKeyboardRemove())
    



@bot.message_handler(commands=['all_days'])
def all_days_first(message):
    """Функция инициирующая вывод всего расписания, передает тип название файла расписания
    Args:
        message (string): Сообщение от пользователя
    """
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    # фунция выбора типа расписания
    backend.PetroBot.sendWeekNumber(message)
    backend.PetroBot.scheduleType(message)
    bot.register_next_step_handler(message, all_days_sched_type)
        



def all_days_sched_type(message):
    """Получает тип расписания и перенаправляет на нужную функцию

    Args:
        message (string): Сообщение от пользователя

    """
    if message.text == "По номеру группы":
        # Вызов функции возвращающей список групп в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.groups(message)
        # Файл с расписанием по группе
        file = "raspisaniye.xlsx"
        bot.register_next_step_handler(message, all_days_output, file)
    elif message.text == "По ФИО преподавателя":
        # Вызов функции предлагающей пользователю ввести ФИО преподавателя
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.prepodSelect(message)
        # Файл с расписанием по преподавателю
        file = "raspisaniyebyprepod.xlsx"
        bot.register_next_step_handler(message, all_days_output, file)
    elif message.text == "По номеру аудитории":
        # Вызов функции возвращающей список аудиторий в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.auditSelect(message)
        # Файл с расписанием по аудитории
        file = "raspisaniyebyaudit.xlsx"
        bot.register_next_step_handler(message, all_days_output, file)
    else:
        bot.send_message(message.from_user.id,
                         "Пожалуйста, введите верное значение, запустив функцию заново", reply_markup=telebot.types.ReplyKeyboardRemove())
        return 0


def all_days_output(message, file):
    """Выводит расписание на все дни недели (числитель и знаменатель)
    Args:
        message (string): Сообщение от пользователя
        file(string): Название файла с расписанием
    """
    try:
        backend.PetroBot.all_days_output(message, file)
    except:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, пожалуйста попробуйте позже.\n Возможно портал сейчас не доступен или сейчас еще нет расписания.", reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['by_day'])
def by_day_first(message):
    """Функция, передающая необходимые данные(по выбору) в функцию по выводу расписания по конретному дню

    Args:
        message (string): Сообщение от пользователя
    """
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    backend.PetroBot.scheduleType(message)
    bot.register_next_step_handler(message, by_day_day_sched_type)


def by_day_day_sched_type(message):
    """Получает типа расписания и перенаправляет на нужную функцию

    Args:
        message (string): Сообщение от пользователя
    """
    if message.text == "По номеру группы":
        # Вызов функции возвращающей список групп в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.groups(message)
        # Файл с расписанием по группе
        file = "raspisaniye.xlsx"
        bot.register_next_step_handler(message, by_day_day_select, file)
    elif message.text == "По ФИО преподавателя":
        # Вызов функции предлагающей пользователю ввести ФИО преподавателя
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.prepodSelect(message)
        # Файл с расписанием по преподавателю
        file = "raspisaniyebyprepod.xlsx"
        bot.register_next_step_handler(message, by_day_day_select, file)
    elif message.text == "По номеру аудитории":
        # Вызов функции возвращающей список аудиторий в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.auditSelect(message)
        # Файл с расписанием по аудитории
        file = "raspisaniyebyaudit.xlsx"
        bot.register_next_step_handler(message, by_day_day_select, file)
    else:
        bot.send_message(message.from_user.id,
                         "Пожалуйста, введите верное значение, запустив функцию заново", reply_markup=telebot.types.ReplyKeyboardRemove())
        return 0


def by_day_day_select(message, file):
    """Функция передающая выбор с клавиатуры дня недели для вывода конкретного раписания

    Args:
        message (string): Сообщение от пользователя
        file (string): Название файла с расписанием
    """
    column = message.text

    backend.PetroBot.sendWeekNumber(message)
    reply = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True, row_width=2)
    reply.add("Понедельник числитель", "Понедельник знаменатель")
    reply.add("Вторник числитель", "Вторник знаменатель")
    reply.add("Среда числитель", "Среда знаменатель")
    reply.add("Четверг числитель", "Четверг знаменатель")
    reply.add("Пятница числитель", "Пятница знаменатель")
    reply.add("Суббота числитель", "Суббота знаменатель")

    bot.send_message(message.from_user.id,
                     "На какой день требуется расписание", reply_markup=reply)
    bot.register_next_step_handler(message, by_day_output, column, file)


def by_day_output(message, column, file):
    """Вывод расписания по конкретному дню недели
    Args:
        message (string): Сообщение от пользователя
        column (string): Номер группы, либо номер аудитории, либо ФИО преподавателя
        file(string): Название файла(тип нужного расписания)
    """
    try:
        backend.PetroBot.by_day_output(message, column, file)
    except:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, пожалуйста попробуйте позже.\n Возможно портал сейчас не доступен или сейчас еще нет расписания.", reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['next_day'])
def next_day_start(message):
    """Функция, передающая необходимые данные в функцию по выводу расписания на текущий или след день

    Args:
        message (string): Сообщение от пользователя
    """

    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    # Переменная дающая понять, что нам нужно расписание на след день
    next_day_bool = 1

    backend.PetroBot.scheduleType(message)
    bot.register_next_step_handler(message, next_day_sched_type, next_day_bool)


def next_day_sched_type(message, next_day_bool):
    """Получает тип расписания и перенаправляет на нужную функцию

    Args:
        message (string): Сообщение от пользователя
        next_day_bool (bool): Если переменная = 1, то расписание выводится на след день, если = 0, то на текущий
    """
    if message.text == "По номеру группы":
        # Вызов функции возвращающей список групп в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.groups(message)
        # Файл с расписанием по группе
        file = "raspisaniye.xlsx"
        bot.register_next_step_handler(
            message, todayOrNextDayOutput, file, next_day_bool)
    elif message.text == "По ФИО преподавателя":
        # Вызов функции предлагающей пользователю ввести ФИО преподавателя
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.prepodSelect(message)
        # Файл с расписанием по преподавателю
        file = "raspisaniyebyprepod.xlsx"
        bot.register_next_step_handler(
            message, todayOrNextDayOutput, file, next_day_bool)
    elif message.text == "По номеру аудитории":
        # Вызов функции возвращающей список аудиторий в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.auditSelect(message)
        # Файл с расписанием по аудитории
        file = "raspisaniyebyaudit.xlsx"
        bot.register_next_step_handler(
            message, todayOrNextDayOutput, file, next_day_bool)
    else:
        bot.send_message(message.from_user.id,
                         "Пожалуйста, введите верное значение, запустив функцию заново", reply_markup=telebot.types.ReplyKeyboardRemove())
        return 0


@bot.message_handler(commands=['today'])
def today_start(message):
    """Функция, передающая необходимые данные в функцию по выводу расписания на текущий или след день

    Args:
        message (string): Сообщение от пользователя
    """

    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    next_day_bool = 0
    # Переменная дающая понять, что нам нужно расписание на текущий день
    backend.PetroBot.scheduleType(message)
    bot.register_next_step_handler(message, today_sched_type, next_day_bool)


def today_sched_type(message, next_day_bool):
    """Получает тип расписания и перенаправляет на нужную функцию

    Args:
        message (string): Сообщение от пользователя
        next_day_bool (bool): Если переменная = 1, то расписание выводится на след день, если = 0, то на текущий

    """
    if message.text == "По номеру группы":
        # Вызов функции возвращающей список групп в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.groups(message)
        # Файл с расписанием по группе
        file = "raspisaniye.xlsx"
        bot.register_next_step_handler(
            message, todayOrNextDayOutput, file, next_day_bool)
    elif message.text == "По ФИО преподавателя":
        # Вызов функции предлагающей пользователю ввести ФИО преподавателя
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.prepodSelect(message)
        # Файл с расписанием по преподавателю
        file = "raspisaniyebyprepod.xlsx"
        bot.register_next_step_handler(
            message, todayOrNextDayOutput, file, next_day_bool)
    elif message.text == "По номеру аудитории":
        # Вызов функции возвращающей список аудиторий в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.auditSelect(message)
        # Файл с расписанием по аудитории
        file = "raspisaniyebyaudit.xlsx"
        bot.register_next_step_handler(
            message, todayOrNextDayOutput, file, next_day_bool)
    else:
        bot.send_message(message.from_user.id,
                         "Пожалуйста, введите верное значение, запустив функцию заново", reply_markup=telebot.types.ReplyKeyboardRemove())
        return 0


def todayOrNextDayOutput(message, file, next_day_bool):
    """Вывод расписания на текущий или на следующий день

    Args:
        message (string): Сообщение от пользователя
        next_day_bool (bool): Если переменная = 1, то расписание выводится на след день, если = 0, то на текущий
        file(string): Название файла(тип нужного расписания)
    """
    try:
        backend.PetroBot.todayOrNextDayOutput(message, file, next_day_bool)
    except:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, пожалуйста попробуйте позже.\n Возможно портал сейчас не доступен или сейчас еще нет расписания.", reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['week'])
def sendWeekNumber(message):

    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    try:
        backend.PetroBot.sendWeekNumber(message)
    except:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, пожалуйста попробуйте позже.\n Возможно портал сейчас не доступен или сейчас еще нет расписания.", reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['by_week'])
def by_week_start(message):
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    backend.PetroBot.scheduleType(message)
    bot.register_next_step_handler(message, by_week_sched_type)


def by_week_sched_type(message):
    if message.text == "По номеру группы":
        # Вызов функции возвращающей список групп в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.groups(message)
        # Файл с расписанием по группе
        file = "raspisaniye.xlsx"
        bot.register_next_step_handler(
            message, by_week_output, file)
    elif message.text == "По ФИО преподавателя":
        # Вызов функции предлагающей пользователю ввести ФИО преподавателя
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.prepodSelect(message)
        # Файл с расписанием по преподавателю
        file = "raspisaniyebyprepod.xlsx"
        bot.register_next_step_handler(
            message, by_week_output, file)
    elif message.text == "По номеру аудитории":
        # Вызов функции возвращающей список аудиторий в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.auditSelect(message)
        # Файл с расписанием по аудитории
        file = "raspisaniyebyaudit.xlsx"
        bot.register_next_step_handler(
            message, by_week_output, file)
    else:
        bot.send_message(message.from_user.id,
                         "Пожалуйста, введите верное значение, запустив функцию заново", reply_markup=telebot.types.ReplyKeyboardRemove())
        return 0


def by_week_output(message, file):
    try:
        backend.PetroBot.by_week_output(message, file)
    except:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, пожалуйста попробуйте позже.\n Возможно портал сейчас не доступен или сейчас еще нет расписания.", reply_markup=telebot.types.ReplyKeyboardRemove())


"""    
#ЗАМЕНЫ#
"""


@bot.message_handler(commands=['all_changes'])
def send_all_changes(message):
    
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    try:
        backend.PetroBot.send_all_changes(message)
    except:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, пожалуйста попробуйте позже.\n Возможно портал сейчас не доступен или сейчас еще нет расписания.", reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['changes'])
def changesByQueryStart(message):
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    reply = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True, row_width=1)
    reply.add("Вчера")
    reply.add("Сегодня")
    reply.add("Завтра")
    bot.send_message(message.from_user.id,
                     "На какой день требуются изменения", reply_markup=reply)
    bot.register_next_step_handler(message, getChangesQuery)


def getChangesQuery(message):
    if message.text == "Вчера":
        date = datetime.datetime.today() + datetime.timedelta(days=-1)
        date_formatted = date.strftime('%d%m%Y')
    elif message.text == "Сегодня":
        date = datetime.datetime.today()
        date_formatted = date.strftime('%d%m%Y')
    elif message.text == "Завтра":
        date = datetime.datetime.today() + datetime.timedelta(days=1)
        date_formatted = date.strftime('%d%m%Y')
    else:
        bot.send_message(message.from_user.id,
                         "Вы ввели неправильное значение, запустите команду заново", reply_markup=telebot.types.ReplyKeyboardRemove())
        return 0

    bot.send_message(message.from_user.id, "Пожалуйста введите желаемый запрос для поиска, это может быть:  <strong>ФИО преподавателя</strong> (например: Иванов И.И. или просто Иванов), <strong>номер группы</strong>, <strong>название предмета</strong> (можно ввести первые буквы или же часть названия)", parse_mode='HTML')
    bot.register_next_step_handler(message, changesByQuery, date_formatted)


def changesByQuery(message, date_formatted):
    try:
        backend.PetroBot.changesByQuery(message, date_formatted)
    except:
        bot.send_message(message.from_user.id,
                         "Что-то пошло не так, пожалуйста попробуйте позже.\n Возможно портал сейчас не доступен или сейчас еще нет расписания.", reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['subscribe'])
def subscribe_start(message):
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 1500:
            return 0
        del last_time[message.from_user.id]

    user = Subscribe().get_one_user_by_id(message.from_user.id)
    if user:
        Subscribe().delete_by_user_id(message.from_user.id)
        bot.send_message(message.from_user.id,
                         "Вы успешно отписаны от рассылки, чтобы подписаться снова используйте эту же команду - /subscribe")
        return 0
    else:
        bot.send_message(message.from_user.id,
                         "Чтобы подписаться на рассылку расписания, вам необходимо пройти процедуру выбора необходимого расписания. <strong>ВНИМАНИЕ</strong> расписание высылается на следующую неделю! Отправляется 1 раз в неделю в воскресенье 21:00.", parse_mode='HTML')
        backend.PetroBot.scheduleType(message)
        bot.register_next_step_handler(message, subscribe_schedule_type)


def subscribe_schedule_type(message):
    if message.text == "По номеру группы":
        # Вызов функции возвращающей список групп в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.groups(message)
        # Файл с расписанием по группе
        file = "raspisaniye.xlsx"
        bot.register_next_step_handler(
            message, subscribe_save_choice, file)
    elif message.text == "По ФИО преподавателя":
        # Вызов функции предлагающей пользователю ввести ФИО преподавателя
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.prepodSelect(message)
        # Файл с расписанием по преподавателю
        file = "raspisaniyebyprepod.xlsx"
        bot.register_next_step_handler(
            message, subscribe_save_choice, file)
    elif message.text == "По номеру аудитории":
        # Вызов функции возвращающей список аудиторий в виде клавиатуры для ввода
        bot.send_message(message.from_user.id,
                         parse.dateRasp, parse_mode="HTML")
        backend.PetroBot.auditSelect(message)
        # Файл с расписанием по аудитории
        file = "raspisaniyebyaudit.xlsx"
        bot.register_next_step_handler(
            message, subscribe_save_choice, file)
    else:
        bot.send_message(message.from_user.id,
                         "Пожалуйста, введите верное значение, запустив функцию заново", reply_markup=telebot.types.ReplyKeyboardRemove())
        return 0


def subscribe_save_choice(message, file):
    try:
        backend.PetroBot.subscribeSaveChoice(message, file)
    except:
        bot.send_message(message.from_user.id,
                         "Не удалось сохранить выбор, пожалуйста попробуйте позже", reply_markup=telebot.types.ReplyKeyboardRemove())
        return 0


@bot.message_handler(commands=['pashalka'])
def pashalka(message):
    """Антифлуд """
    if message.from_user.id not in last_time:
        last_time[message.from_user.id] = time.time()
    else:
        if (time.time() - last_time[message.from_user.id]) * 1000 < 5000:
            return 0
        del last_time[message.from_user.id]

    bot.send_message(message.from_user.id,
                         "Молодец! Ты нашел пасхалку! (=^-ω-^=)")



@server.route('/' + "TOKEN", methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="appURl" +
                    "TOKEN")
    return '!', 200


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

