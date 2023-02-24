import requests
from bs4 import BeautifulSoup


HEADERS = headers = {'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html, */*; q=0.01',
                    'Accept-Encoding': 'UTF-8',
                    'viewmode': 'list',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Connection': 'close'}


def getMainPage(groupName, weekNum=-1) -> requests:  
    """
    Возвращает объект класса requests c расписанием на неделю. В качестве аргументов принимает название группы и номер недели (по-умолчанию "-1")
    """
    try:
        target_url = f"https://rasp.rea.ru/Schedule/ScheduleCard?selection={groupName.lower()}&weekNum={weekNum}&catfilter=0"
        mainPage = requests.get(target_url, headers=HEADERS)
        if mainPage.status_code != 200:
                raise Exception("Расписание недоступно :-(")
        if "не найдено результатов" in mainPage.text:
                raise Exception("Неправильно название группы!")
        return mainPage
    except:
        return Exception


class Lesson:
    def __init__(self):#Название предмета, вид занятия (лекция/семинар...), первая подгруппа (Преподаватель, Аудитория)
        self.name = ""
        self.type = ""
        self.groups = []

    def __str__(self):
        groupsInfo = ""
        num = 1
        for group in self.groups:
            groupsInfo += f"{num}-я подгруппа:\n"
            for item in group:
                groupsInfo += f"{item}\n"
            num += 1
            groupsInfo+="\n"
        return f"{self.name}\n{self.type}\n{groupsInfo}\n"
    
    def getLesson(self, groupName, date, timeSlot):
        """
        Получение данных о паре, принимает название группы, дата и номер пары.
        """
        try:
            #Получение страницы с деталями.
            target_url = f"https://rasp.rea.ru/Schedule/GetDetails?selection={groupName.lower()}&date={date}&timeSlot={timeSlot}"
            detailsPage = requests.get(target_url, headers=HEADERS)
            if detailsPage.status_code != 200:
                    raise Exception("Расписание недоступно :-(")

            soupDetailsPage = BeautifulSoup(detailsPage.text, 'html.parser')
            try:
                self.name = soupDetailsPage.find("h5").text #Тега не будет на странице, если пара пустая.
            except:
                return
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

            8 корпус -\r\n        507
            \________/\_________/\__/
                10         9      4
            \___________________/___/
                      19      + 4 = 23   
            """
        except:
            return Exception


class Day:
    def __init__(self, date="ERROR"):#Дата занятия, пары
        self.date = date
        self.lessons = []
    def __str__(self):
        if len(self.lessons) == 0:
            return f"{self.date}\nВ этот день занятий нет.\n\n"
        else:
            timetable = [
                "1 пара (08:30 - 10:00)",
                "2 пара (10:10 - 11:40)",
                "3 пара (11:50 - 13:20)",
                "4 пара (14:00 - 15:30)",
                "5 пара (15:40 - 17:10)",
                "6 пара (17:20 - 18:50)",
                "7 пара (18:55 - 20:25)",
                "8 пара (20:30 - 22:00)"
            ]
            lesson_num = 0
            answer = f"{self.date}\n"
            for lesson in self.lessons:
                answer += f"{timetable[lesson_num]}\n {lesson}" 
                lesson_num += 1
            return answer
    def AddLesson(self, lesson):
        self.lessons.append(lesson)
    def setDate(self, date):
        self.date = date

day = Lesson()
day.getLesson("15.27д-пи05/22б", "27.02.2023", "8" )
print(day)