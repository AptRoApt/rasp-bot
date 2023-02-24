
class Lesson:
    def __init__(self, name="", type="", first_group=[], second_group = []):#Название предмета, вид занятия (лекция/семинар...), первая подгруппа (Преподаватель, Аудитория)
        self.name = name
        self.type = type
        self.first_group = first_group
        self.second_group = second_group
    def __str__(self):
        group1 = ""
        group2 = ""
        for item in self.first_group:
            group1 += item + "\n"
        for item in self.second_group:
            group2 += item + "\n"
        return f"{self.name}\n{self.type}\n{group1}{group2}\n"
    def AddName(self, name):
        self.name = name
    def AddType(self, type):
        self.type = type
    def AddGroup(self, group):
        if len(self.first_group) != 0:
            self.second_group = group
        else:
            self.first_group = group


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


