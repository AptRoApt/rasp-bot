from bs4 import BeautifulSoup
import requests
from datetime import date
from schedule import *


"""
Что интересно, есть готовая функция на странице, которая позволяет экспортировать расписание ics-файлом. Чтоб её открыть нужно сменить строку
<div class="modal fade" id="modal-export-dlg" tabindex="-1" role="dialog" aria-labelledby="modal-export-title" aria-hidden="true">
на
<div class="modal fade show" id="modal-export-dlg" tabindex="-1" role="dialog" aria-labelledby="modal-export-title" aria-hidden="true" style = "display: block">
"""

"""
Добавить возможность выбора группы поэтапно (как на самом сайте)
расписание в закреп?
"""

"""
Мне нужно удалённо запускать скрипты и получать готовый html.
    curl -H "X-Requested-With: XMLHttpRequest"
    -H "Accept: text/html, */*; q=0.01"
    -H "Accept-Encoding: UTF-8" 
    -H "Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"
    -H "Connection: close"  
    https://rasp.rea.ru/Schedule/ScheduleCard?selection=15.27%D0%B4-%D0%BF%D0%B805%2F22%D0%B1&weekNum=-1&catfilter=0 

    https://rasp.rea.ru/Schedule/GetDetails?selection=15.27д-пи05/22б&date=20.02.2023&timeSlot=2
"""

"""
# Выполнение запроса для получения основной страницы
        headers = {'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html, */*; q=0.01',
                    'Accept-Encoding': 'UTF-8',
                    'viewmode': 'list',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Connection': 'close'}
        target_url = "https://rasp.rea.ru/Schedule/ScheduleCard?selection=" + group_name+ "&weekNum=-1&catfilter=0"
        page = requests.get(target_url, headers = headers)
"""

        # if page.status_code != 200:
        #     raise Exception("Расписание недоступно :-(")
        # soup_page = BeautifulSoup(page.text, 'html.parser')

def get_schedule(group_name): 
 #   try:
        # Выполнение запроса для получения основной страницы и создания объекта BeautifulSoup для удобной навигации по html'ке.
        headers = {'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html, */*; q=0.01',
                    'Accept-Encoding': 'UTF-8',
                    'viewmode': 'list',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Connection': 'close'}
        target_url = "https://rasp.rea.ru/Schedule/ScheduleCard?selection=" + group_name.lower() + "&weekNum=-1&catfilter=0"
        main_page = requests.get(target_url, headers = headers)
        soup_main_page = BeautifulSoup(main_page.text, 'html.parser')

        # Обработка исключений
        if main_page.status_code != 200:
            raise Exception("Расписание недоступно :-(")
        if "не найдено результатов" in main_page.text:
            raise Exception("Неправильно название группы!")

        #Массив, что будет возвращаться функцией. Содержит расписание на неделю.
        schedule = [] 
        s=0

        #Создаём массив div'ов, в которых содержится расписание на день. 
        days = soup_main_page.find_all("div", class_="col-lg-6 col-12")
        for day in days:
            # Заготовка ссылки для отдельных пар. Предыдущая нам уже не нужна, потому переинициализируем её.
            # today = date.today().strftime("%d.%m.%Y")
            the_day = Day()
            current_date = day.find("h5").text
            the_day.setDate(current_date)
            target_url = f"https://rasp.rea.ru/Schedule/GetDetails?selection={group_name.lower()}&date={current_date[-10:]}&timeSlot="

            if "Занятия отсутствуют" in day.text:
                pass
            else:
                for i in range (1, 9):# А если нет занятия?!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    the_lesson = Lesson()
                    details_page = requests.get(target_url+str(i), headers=headers)
                    soup_details_page = BeautifulSoup(details_page.text, 'html.parser')
                    try:
                        the_lesson.AddName(soup_details_page.find("h5").text)
                    except:
                        the_day.AddLesson(the_lesson)
                        continue
                    the_lesson.AddType(soup_details_page.find("strong").text)
                    groups = soup_details_page.find_all("div", class_="element-info-body")
                    teachers = soup_details_page.find_all("a")
                    k = 0
                    for group in groups: #Если подгруппа только одна - он возьмёт только её, иначе запишет две.
                        first_index = group.text.find("корпус") - 2 
                        second_index = first_index +19 #захардкожено 
                        room = group.text[first_index:first_index+10] + group.text[second_index:second_index+4]
                        the_lesson.AddGroup([teachers[k].text, room])
                    the_day.AddLesson(the_lesson)
            schedule.append(the_day)
        return schedule
  #  except Exception as error:
  #      return error
"""
escape-последовательности - один символ

8 корпус -\r\n        507
\________/\_________/\__/
    10         9      4
"""

# headers = {'X-Requested-With': 'XMLHttpRequest',
#                     'Accept': 'text/html, */*; q=0.01',
#                     'Accept-Encoding': 'UTF-8',
#                     'viewmode': 'list',
#                     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
#                     'Connection': 'close'}
# # today = date.today().strftime("%d.%m.%y")
# target_url = "https://rasp.rea.ru/Schedule/GetDetails?selection=15.27д-пи05/22б&date=27.02.2023&timeSlot=1"
# page = requests.get(target_url, headers=headers)
# print (page.text)

s = get_schedule("15.27д-ПИ05/22б")
for i in s:
     print(i)


