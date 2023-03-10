import json
import asyncio
import aiohttp
from scheduleRea import isGroupNameCorrect 

async def addUser(session, id: str, groupName: str):
    """
    Изменяет/добавляет связку id - группа
    """
    try:
        await isGroupNameCorrect(session, groupName)
        data = json.loads(open("users/users.json", "r").read())
        data[id] = groupName
        dataFile = open("users/users.json", "w").write(json.dumps(data))
    except json.decoder.JSONDecodeError:
        dataFile = open("users/users.json", "w").write(json.dumps({id: groupName}))
    except Exception as e:
        raise e



def deleteUser(id: str):
    """
    Удаляет пользователя.
    """
    try:
        data = json.loads(open("users/users.json", "r").read())
        data.pop(id)
        dataFile = open("users/users.json", "w").write(json.dumps(data))
    except Exception as e:
        print (e)

def getGroup(id: str) -> str:
    data = json.loads(open("users/users.json", "r").read())
    return data.get(id)



async def testUsers():
    """
    Ожидаемый вывод: 
    15.27д-пи05/22д
    None
    """
    async with aiohttp.ClientSession() as session:
        try:
            await addUser(session, "0", "15.27д-пи05/22г")
            print("Не работает проверка группы!")
        except:
            await addUser(session, "0", "15.27д-пи05/22б")
            print(getGroup("0"))
            deleteUser("0")
            print(getGroup("0"))





# asyncio.run(testUsers())
