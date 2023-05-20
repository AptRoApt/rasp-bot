from vkbottle import BaseStateGroup

class BotChatStates(BaseStateGroup):
    MAILING_IS_ON = "mailing is on"
    MAILING_IS_OFF = "mailing is off"
    CHANGE_MAILING_TIME = "changing mailing time"