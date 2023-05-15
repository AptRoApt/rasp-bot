from vkbottle.bot import Message, BotLabeler
from vkbottle import BaseStateGroup
from scheduleRea import getDay
import datetime
from global_variables.states import ScheduleStates
from global_variables.config import state_dispenser, aioscheduler
from apscheduler.triggers.cron import CronTrigger
MNE_LEN_DELAT_VVOD_GROUPY = "15.27д-пи05/22б"
schedule_labeler = BotLabeler()
schedule_labeler.vbml_ignore_case = True
async def send_day_schedule(message: Message, groupName: str):
    date = datetime.date.today()
    day = await getDay(groupName, date.strftime("%d.%m.%Y"))
    await message.answer(day)

@schedule_labeler.chat_message(text="!включить")
async def parsing_on(message: Message):
    state = await state_dispenser.get(message.peer_id)
    if state:
    #state = StatePeer(peer_id, state='ScheduleStates:bot is on', payload={})
        if state.state.split(":")[-1] == ScheduleStates.IS_ON:
            return await message.answer("Бот уже включён!")
    await state_dispenser.set(message.peer_id, ScheduleStates.IS_ON)
    aioscheduler.add_job(send_day_schedule, CronTrigger(hour="5", timezone="Europe/Moscow"), args =(message, MNE_LEN_DELAT_VVOD_GROUPY), id = str(message.peer_id) )

@schedule_labeler.chat_message(text="!выключить")
async def parsing_off(message: Message):
    state = await state_dispenser.get(message.peer_id)
    if state:
        if state.state.split(":")[-1] == ScheduleStates.IS_OFF:
            return await message.answer("Бот уже выключён!")
    await state_dispenser.set(message.peer_id, ScheduleStates.IS_OFF)
    aioscheduler.remove_job(str(message.peer_id))