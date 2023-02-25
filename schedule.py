import requests
from bs4 import BeautifulSoup
import asyncio


HEADERS = headers = {'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html, */*; q=0.01',
                    'Accept-Encoding': 'UTF-8',
                    'viewmode': 'list',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Connection': 'close'}

def isGroupNameCorrect(groupName):
    """
    Обработка ошибок при обращении к расписанию.
    """
    target_url = f"https://rasp.rea.ru/Schedule/PageHeaderCard?selection={groupName.lower()}&catfilter=0"
    headerPage = requests.get(target_url, headers=HEADERS)
    if "Найденные" in headerPage.text:
        raise Exception("Неправильное название группы!")


def getMainPage(groupName, weekNum=-1) -> requests:  
    """
    Возвращает объект класса requests c расписанием на неделю. В качестве аргументов принимает название группы и номер недели (по-умолчанию "-1")
    """
    target_url = f"https://rasp.rea.ru/Schedule/ScheduleCard?selection={groupName.lower()}&weekNum={weekNum}&catfilter=0"
    mainPage = requests.get(target_url, headers=HEADERS)
    if mainPage.status_code != 200:
        raise Exception("Расписание недоступно :-(")
    return mainPage


def getDetailsPage (groupName, date, timeSlot):
    """
    Возвращает объект класса requests c детельным расписанием. В качестве аргументов принимает название группы, дату и номер пары.
    """
    target_url = f"https://rasp.rea.ru/Schedule/GetDetails?selection={groupName.lower()}&date={date}&timeSlot={timeSlot}"
    detailsPage = requests.get(target_url, headers=HEADERS)
    if detailsPage.status_code != 200:
        raise Exception("Расписание недоступно :-(")
    return detailsPage


class Lesson:
    def isEmpty(self) -> bool:
            return (self.name == "")
    def __init__(self):#Номер пары,азвание предмета, вид занятия (лекция/семинар...), первая подгруппа (Преподаватель, Аудитория)
        self.lessonNum = ""
        self.name = ""
        self.type = ""
        self.groups = []

    def __str__(self):
        if self.isEmpty():
            return ""
        timetable = {
                "1 пара": "(08:30 - 10:00):",
                "2 пара": "(10:10 - 11:40):",
                "3 пара": "(11:50 - 13:20):",
                "4 пара": "(14:00 - 15:30):",
                "5 пара": "(15:40 - 17:10):",
                "6 пара": "(17:20 - 18:50):",
                "7 пара": "(18:55 - 20:25):",
                "8 пара": "(20:30 - 22:00):"
        }
        groupsInfo = ""
        num = 1
        for group in self.groups:
            if len(self.groups) == 2:# если есть деление на подгруппы.
                groupsInfo += f"{num}-я подгруппа:\n"
            for item in group:
                groupsInfo += f"{item}\n"
            num += 1
        time = timetable.get(self.lessonNum, "" )
        return f"{self.lessonNum} {time}\n{self.name}\n{self.type}\n{groupsInfo}\n"
    
    def getLesson(self, groupName, date, timeSlot):
        """
        Получение данных о паре, принимает название группы, дату и номер пары.
        """
        isGroupNameCorrect(groupName)
        detailsPage =   getDetailsPage(groupName, date, timeSlot)
        soupDetailsPage = BeautifulSoup(detailsPage.text, 'html.parser')
        try:
            self.name = soupDetailsPage.find("h5").text #Тега не будет на странице, если пара пустая.
        except:
            return
        lessonNumIndex = soupDetailsPage.div.text.find("пара")-2
        self.lessonNum = soupDetailsPage.div.text[lessonNumIndex:lessonNumIndex+6]
        self.type = soupDetailsPage.find("strong").text
        groups = soupDetailsPage.find_all("div", class_="element-info-body")
        teachers = soupDetailsPage.find_all("a")# Первое - ссылка на занятие.
        k = 1
        for group in groups: #Если подгруппа только одна - он возьмёт только её, иначе запишет две.
            index = group.text.find("корпус") - 2 
            room = group.text[index:index + 10] + group.text[index + 19:index + 23]
            self.groups.append([teachers[k].text[7:], room])# [7:] - обрезаем "school "
            k += 1
            """ 
            escape-последовательности - один символ
            room =
            8 корпус -\r\n        507
            \________/\_________/\__/
                10         9      4
            \___________________/___/
                      19      + 4 = 23   
            """
        


class Day:
    def __init__(self):#Дата занятия, пары
        self.date = "Ошибка получения даты."
        self.lessons = []
    def __str__(self):
        if len(self.lessons) == 0:
            return f"{self.date}\nВ этот день занятий нет.\n\n"
        else:
            lessonNum = 0
            answer = f"{self.date}\n"
            for lesson in self.lessons:
                answer += f"{lesson}" 
                lessonNum += 1
            return answer
    def getDay(self, groupName, date):
        """
        Заполняет расписание дня. Принимает название группы, дату.
        """
        isGroupNameCorrect(groupName)
        self.date = date
        for timeSlot in range (1,9):
            theLesson = Lesson()
            theLesson.getLesson(groupName,date,timeSlot)
            if theLesson.isEmpty:
                continue
            self.lessons.append(theLesson)
