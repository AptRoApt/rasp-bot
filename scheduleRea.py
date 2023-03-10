import aiohttp
from bs4 import BeautifulSoup
import asyncio
import time
from PIL import Image, ImageFont, ImageDraw


HEADERS = headers = {'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html, */*; q=0.01',
                    'Accept-Encoding': 'UTF-8',
                    'viewmode': 'list',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Connection': 'close'}

async def isGroupNameCorrect(session, groupName):
    """Вызывает исключение, если группы не существует (ну или сервер лежит).

    Args:
        session (aiohttp.ClientSession()): Активная сессия.
        groupName (str): Название группы.

    Raises:
        Exception: "Неправильное название группы"
    """
    targetUrl = f"https://rasp.rea.ru/Schedule/PageHeaderCard?selection={groupName.lower()}&catfilter=0"
    async with session.get(targetUrl, headers = HEADERS) as response:
            headerPage = await response.text()
    if "Найденные" in headerPage:
        raise Exception("Неправильное название группы!")
    


async def getPageText(session, url):
    """Возвращает html страницы в string.

    Args:
        session (aiohttp.ClientSession()): Активная сессия.
        url (str): ссылка, html которой требуется получить.

    Raises:
        Exception: "Расписание недоступно"

    Returns:
        str: html страницы.
    """
    async with session.get(url, headers = HEADERS) as response:
        page = await response.text()
        if response.status != 200 or "Найденные" in page:
            raise Exception("Расписание недоступно :-(")
        return page
    
def scaleText(text: str, type:str, size: tuple) -> ImageFont.truetype:
    """Масштабирует текст под нужный размер и шрифт.

    Args:
        text (str): текст для масштабирования.
        type (str): местоположение шрифта.
        size (tuple): ширина и высота области, в которой будет текст.

    Returns:
        ImageFont.truetype: Шрифт из библиотеки ImageFont
    """
    fontSize = 1
    jumpSize = 24
    font = ImageFont.truetype(type, fontSize)
    while True:
        if font.getbbox(text)[2] < size[0] and font.getbbox(text)[3] < size[1]:
            fontSize += jumpSize
        else:
            jumpSize = jumpSize // 2
            fontSize -= jumpSize
        font = ImageFont.truetype(type, fontSize)
        if jumpSize <= 1:
            break
    return ImageFont.truetype(type, fontSize)





class Lesson:
    def __init__(self):#Номер пары,азвание предмета, вид занятия (лекция/семинар...), первая подгруппа (Преподаватель, Аудитория)
        self.lessonNum = ""
        self.name = ""
        self.type = ""
        self.groups = []

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
    
    async def getLesson(self, groupName, date, timeSlot, session) :
        """
        Получение данных о паре, принимает название группы, дату и номер пары.
        """
        target_url = f"https://rasp.rea.ru/Schedule/GetDetails?selection={groupName.lower()}&date={date}&timeSlot={timeSlot}"
        pageText = await getPageText(session, target_url)
        soupDetailsPage = BeautifulSoup(pageText, 'html.parser')
        try:
            self.name = soupDetailsPage.find("h5").text #Тега не будет на странице, если пара пустая.
        except:
            return self
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
        return self
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
            answer = f"{self.date}\n"
            for lesson in self.lessons:
                answer += f"{lesson}" 
            return answer
# def getDay(groupName, date, session):
#         """
#         Заполняет расписание дня. Принимает название группы, дату.
#         """
#     self.date = date
#     tasks = []
#     for timeSlot in range (1, 9):
#         task = asyncio.create_task(Lesson().getLesson(groupName, date, timeSlot, session))
#         tasks.append(task)
#     self.lessons = await asyncio.gather(*tasks)
#     return self




async def getWeek(session, groupName: str, weekNum=-1) -> str:
    """Возвращает путь к файлу с расписанием на неделю.

    Args:
        session (aiohttp.ClientSession()): Активная сессия.
        gtoupName (str): Имя группы.
        weekNum (int): Номер недели (по-умолчанию -1).

    Returns:
        str: Путь к файлу с расписанием на неделю.
    """
    
    targetUrl = f"https://rasp.rea.ru/Schedule/ScheduleCard?selection={groupName.lower()}&weekNum={weekNum}&catfilter=0"
    pageText = await getPageText(session, targetUrl)
    soupMainPage = BeautifulSoup(pageText, "html.parser")
    divsWithDays = soupMainPage.find_all("div", class_="container")
    with Image.open("images/Расписание.png") as image:
        draw = ImageDraw.Draw(image) 
        for i in range(0, len(divsWithDays)):
            dayHeader = divsWithDays[i].thead.text.strip()
            if i % 2 == 0: #Если число чётное - заполняется левая часть листа. Иначе - правая.
                headerAnchor = (435, 328 + 261*i)
                lessonAnchor= [458, 374.5 + 261*i]
            else:
                headerAnchor = (1245, 328  + 261*(i-1))
                lessonAnchor = [1268, 374.5 + 261*(i-1)]
            headerFont = scaleText(dayHeader,"fonts/arial.ttf", (708, 40))
            draw.text(headerAnchor, dayHeader, font=headerFont, fill="black", anchor="mm")
            for lesson in divsWithDays[i].find_all("tr", class_ = "slot"):
                lessonInfo = lesson.find("a", class_="task")
                if lessonInfo == None:# если пары нет - пропускаем.
                    continue
                FirstIndex = str(lessonInfo).find("<i>") + 3 
                SecondIndex = str(lessonInfo).find("</i>")
                lessonType = str(lessonInfo)[FirstIndex: SecondIndex].strip()
                if "Практическое занятие" in lessonType:
                    draw.line([(lessonAnchor[0]-331, lessonAnchor[1]), (lessonAnchor[0]+331, lessonAnchor[1])],"#8fd3ee",41)
                elif "Лекция" in lessonType:
                    draw.line([(lessonAnchor[0]-331, lessonAnchor[1]), (lessonAnchor[0]+331, lessonAnchor[1])],"#a0ee8f",41)
                else:
                    draw.line([(lessonAnchor[0]-331, lessonAnchor[1]), (lessonAnchor[0]+331, lessonAnchor[1])],"#ea5959",41)
                FirstIndex = str(lessonInfo).find(")\">") + 3 # )">
                SecondIndex = str(lessonInfo).find("<br")
                lessonName = str(lessonInfo)[FirstIndex: SecondIndex].strip()
                
                lessonNameFont = scaleText(lessonName,"fonts/arial.ttf", (662, 41))
                draw.text(lessonAnchor, lessonName, font=lessonNameFont, fill="black", anchor="mm")
                lessonAnchor[1] += 48
        filepath = f"images/{time.time()}.png"
        image.save(filepath)
        return filepath
        """
            На длинных предметах едет вёрстка. При всём, кроме ариала
            Добавить даты недели
            Добавить легенду
            """ 

async def testDay():
    async with aiohttp.ClientSession() as session:
        day = Day()
        start = time.time()
        await day.getDay("15.27д-пи05/22б", "11.03.2023", session)
        end = time.time()
        print (end - start)
        print (day)

async def testWeek():
    async with aiohttp.ClientSession() as session:
        start = time.time()
        await getWeek(session, "15.27д-пи05/22б", 30)
        end = time.time()
        print (end - start)


# asyncio.run(testDay())
# Week().getImage()
asyncio.run(testWeek())

