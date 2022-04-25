from datetime import datetime
from itertools import cycle
import re
import urllib.request
import json
import ssl
import datetime

baseUrl = "https://iot.spyc.hk"


class APIError(Exception):
    pass


class HolidayException(Exception):
    pass


class Period:
    def __init__(self, periodJSON: dict):
        if not "subject" in periodJSON:
            raise KeyError("subject is missing from periodJSON")
        if not "venue" in periodJSON:
            raise KeyError("venue is missing from periodJSON")

        self.subject = periodJSON["subject"]
        self.venue = periodJSON["venue"]

    @property
    def formattedString(self):
        return f'{self.subject} @{self.venue}'


class Timetable:
    def __init__(self, timetableJSON):
        self.dict = {}
        for cycleDay in timetableJSON:
            if not re.fullmatch(r'[A-Ha-h]', cycleDay):
                raise ValueError(f'Invalid cycle day: {cycleDay}')

            periods = list(map(lambda p: Period(p),
                               timetableJSON[cycleDay.upper()]))
            self.dict[cycleDay] = periods

    def getDayPeriods(self, day) -> list[Period]:
        if not day in self.dict:
            raise KeyError("Invalid Day")

        return self.dict[day]

    def getPeriod(self, periodReference) -> Period | None:
        if not re.fullmatch(r'[A-Ha-h][1-7]', periodReference):
            raise ValueError(
                f'Invalid PeriodReference value {periodReference}')

        cycleDay = periodReference[0].upper()
        periodNumber = int(periodReference[1]) - 1

        dayLessons = self.getDayPeriods(cycleDay)

        try:
            period = dayLessons[periodNumber]
        except IndexError:
            period = None

        return period


class SpycAPI:
    def __init__():
        pass

    @staticmethod
    def fetchJSON(relpath: str = "/"):
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(f"{baseUrl}{relpath}") as url:
            results = url.read().decode()
            return json.loads(results)

    @staticmethod
    def getTimetable(_class: str = "1A") -> Timetable:
        if not re.fullmatch(r'[1-6][A-Ea-e]', _class):
            raise ValueError(f'Invalid class value {_class}')

        timetableJSON = SpycAPI.fetchJSON(f'/timetable?cl={_class.upper()}')
        timetable = Timetable(timetableJSON)
        return timetable

    @staticmethod
    def getCycleCalendar() -> dict:
        cycleCalendarJSON = SpycAPI.fetchJSON('/cyclecal')
        return cycleCalendarJSON

    @staticmethod
    def getCycleDay(queryDate: datetime.datetime | None = None) -> str:
        if queryDate is None:
            queryDate = datetime.datetime.now()

        if not isinstance(queryDate, datetime.datetime):
            raise TypeError("QueryDate must be in datetime type")

        cycleCalendarJSON = SpycAPI.getCycleCalendar()

        fQueryDate = queryDate.strftime('%a %b %d %Y')
        try:
            if not fQueryDate in cycleCalendarJSON:
                raise KeyError("Date is not in cycleCalendarJSON")
        except TypeError:
            raise APIError("API Data is invalid")

        cycleDay: str = cycleCalendarJSON[fQueryDate]
        return cycleDay

    @staticmethod
    def getLessons(_class: str, periodRefs: list[str]):
        timetable = SpycAPI.getTimetable(_class)

        periods = []

        for periodReference in periodRefs:
            periods.append(timetable.getPeriod(periodReference))

        return periods

    @staticmethod
    def getDateLessons(_class, datetime: datetime.datetime):
        if not re.fullmatch(r'[1-6][A-Ea-e]', _class):
            raise ValueError(f'Invalid class value {_class}')

        cycleday = SpycAPI.getCycleDay(datetime)
        if cycleday == '/':
            raise HolidayException()
        else:
            result = []
            for day in cycleday:
                periodrefs = []
                for period in range(6):
                    periodrefs.append(f'{day}{int(period) + 1}')
                result.extend(SpycAPI.getLessons(_class, periodrefs))
            return result
