from vkbottle.bot import Message, BotLabeler
from vkbottle import BaseStateGroup
from scheduleRea import getDay
import datetime
from global_variables.states import BotChatStates
from global_variables.variable_holder import state_dispenser, aioscheduler, ctx
from apscheduler.triggers.cron import CronTrigger



schedule_labeler = BotLabeler()
schedule_labeler.vbml_ignore_case = True

@schedule_labeler.chat_message(text=["!Расписание"])
async def passing(message: Message):
    group = get_group_data(message.peer_id)
    if group:
        status = is_mailing_on(message.peer_id)
        await message.answer(f"Сохранённая группа: {group}\nСтатус рассылки: {status}")#ADD KB ADD STATUS
        
    else:
        await state_dispenser.set(message.peer_id, BotChatStates.GET_GROUP)
        await message.answer(f"Пожалуйста, введите номер вашей группы (Например: 15.27д-пи05/22б)")
        
@schedule_labeler.chat_message(text="Время рассылки")
async def mailing_management(message: Message):
    current_mailing_time = get_mailing_time(message.peer_id)
    await message.answer(f"Ваше текущее время рассылки:\n{current_mailing_time}")#add_kb
    state_dispenser.set(message.peer_id, BotChatStates.CHANGE_MAILING_TIME)
    
@schedule_labeler.chat_message(BotChatStates.CHANGE_MAILING_TIME)
async def change_mailing_time

@schedule_labeler.chat_message(text="!включить")
async def parsing_on(message: Message):
    state = await state_dispenser.get(message.peer_id)
    await message.answer("Бот включён!")
    if state:
        if state.state.split(":")[-1] == BotChatStates.SCHEDULE_IS_ON:
            return await message.answer("Бот уже включён!")
    await state_dispenser.set(message.peer_id, BotChatStates.SCHEDULE_IS_ON)
    aioscheduler.add_job(send_day_schedule, CronTrigger(hour="5", timezone="Europe/Moscow"), args =(message, MNE_LEN_DELAT_VVOD_GROUPY), id = str(message.peer_id) )

@schedule_labeler.chat_message(text="!выключить")
async def parsing_off(message: Message):
    state = await state_dispenser.get(message.peer_id)
    await message.answer("Бот выключён!")
    if state:
        if state.state.split(":")[-1] == BotChatStates.SCHEDULE_IS_OFF:
            return await message.answer("Бот уже выключён!")
    await state_dispenser.set(message.peer_id, BotChatStates.SCHEDULE_IS_OFF)
    aioscheduler.remove_job(str(message.peer_id))