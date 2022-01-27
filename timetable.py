from datetime import datetime, timedelta
import urllib.request
import json
import ssl


def fetchAPI() -> dict:
    """Get the timetable from "https://iot.spyc.hk/timetable"

    Returns:
        dict: dictionary containing all classes' timetable
    """

    ssl._create_default_https_context = ssl._create_unverified_context
    with urllib.request.urlopen("https://iot.spyc.hk/timetable") as url:
        results = url.read().decode()

        # save data as /timetable.json
        with open("timetable.json", "w") as timetableJSON:
            timetableJSON.write(results)
        data = json.loads(results)

        # Return timetable
        return data


def getLessonList(class_: str, day: str) -> list:
    """Get lesson list for the given class and the given day

    Args:
        class_ (str): the given class
        day (str): the given day

    Returns:
        list: list of subjects
    """

    lessonsJSON = fetchAPI()
    # If the the lessonsJSON contains the class we want to get
    # and the day we want to get
    if class_ in lessonsJSON:
        if day in lessonsJSON[class_]:
            lessons = lessonsJSON[class_][day]
        else:
            return None, "不存在此 Day"
    else:
        return None, "找不到此班別"

    subjects = []
    for lesson in lessons:
        subjects.append(lesson["subject"])

    return subjects


def getDayOfCycle(tomorrow: bool) -> str:
    """Get Day of Cycle of today

    Returns:
        str: Day of cycle (A-H)
    """
    now = datetime.now() 
    queryDatetime = now + timedelta(days=1) if tomorrow else now
    
    date = queryDatetime.strftime('%a %b %d %Y')

    ssl._create_default_https_context = ssl._create_unverified_context
    with urllib.request.urlopen("https://iot.spyc.hk/cyclecal") as url:
        results = url.read().decode()
        data = json.loads(results)
        dayOfCycle = data[date]
        print(dayOfCycle)
        return dayOfCycle


if __name__ == "__main__":
    fetchAPI()
