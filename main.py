from vkbottle.bot import Bot, Message
from global_variables.variable_holder import TOKEN, labeler, state_dispenser, aioscheduler
from handlers.schedule_handlers import schedule_labeler
import asyncio

bot = Bot(token=TOKEN, labeler = labeler, state_dispenser = state_dispenser)
labeler.load(schedule_labeler)


aioscheduler.start()
bot.run_forever()