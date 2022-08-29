from datetime import datetime
from datetime import date
import json
from xmlrpc.client import DateTime
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass

### Global functions ###

# function to send a get request to a url and return the response
def getResponse(url):
    return requests.get(url)

# function to extract the text from a get request
def getHTML(response):
    return response.text

#function to format dates
def date_formatter(date_text, year):
    date_index = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    day = date_text[-2:].replace(" ","0")
    month = date_index[date_text[:3]]
    formatted = f"{year}-{month}-{day}"
    return formatted

#function to format dates from user input
def get_date(prompt):
    is_valid = False

    while not is_valid:
        try:
            try_date = input(prompt)
            date_list = [int(x) for x in try_date.split("-")]
            y, m, d, = date_list[0], date_list[1], date_list[2]
            my_date = date(y, m, d)
            is_valid = True
        except:
            print('Invalid date, try again.')
    return my_date

# -------------------------------------------
# Modify the holiday class to 
# 1. Only accept Datetime objects for date.
# 2. You may need to add additional functions
# 3. You may drop the init if you are using @dataclasses
# --------------------------------------------
@dataclass
class Holiday:
    name: str
    date: date #= field(metadata={"units":"U.S. dollars"})
    
    def __str__(self):
        return f"Name: {self.name}, Date: {self.date}"
# test Holiday class
# holiday1 = Holiday("Valentine's Day", "2022-02-14")
# print(holiday1)

class HolidayList:
    def __init__(self):
       self.innerHolidays = []
   
    def addHoliday(self):
    # function to get new holiday from user and append to innerHolidays list
        print("Add a Holiday")
        print("=============")
        while True:
            name_input = input("Please enter new holiday name: ")
            name = name_input.strip().upper()
            date = get_date("Enter date in the format [YYYY-MM-DD]: ")
            new_holiday = Holiday(name, date)
             # Make sure holidayObj is an Holiday Object by checking the type
            if isinstance(new_holiday, object):
                # Use innerHolidays.append(holidayObj) to add holiday
                if new_holiday in self.innerHolidays:
                    print('Already in holiday list.')
                else:
                    self.innerHolidays.append(new_holiday)
                    print(f"You added {new_holiday} successfully.")
                    break
            else:
                print("Please enter a valid name and date.")
        # print to the user that you added a holiday
    
    def findHoliday(self, HolidayName):
        # function to find and print out holiday in innerHoliday list
        # search for Holiday Name & find Holiday in innerHolidays
        for index, holiday in enumerate(self.innerHolidays):
            # [test] print(index, holiday)
            if holiday == HolidayName:
                # [test] print(f"findHoliday index, type(index) result: {index, type(index)}")
                return index
        # [test] print(f"Holiday not found. Please try again.")
        # Return Holiday
        return None

        

    def removeHoliday(self):
        # Find Holiday in innerHolidays by searching the name and date combination.
        while True:
            print("Remove a Holiday")
            print("=============")
            # get input from user
            name_input = input("Please enter holiday name to remove: ")
            name = name_input.strip().upper()
            date = get_date("Enter date in the format [YYYY-MM-DD], i.e. [2021-06-02]: ")
            searchHoliday = Holidays.findHoliday(HolidayName = Holiday(name, date))
            # [test] print(f"removeHoliday: searchHoliday result: {searchHoliday}")
            # remove the Holiday from innerHolidays
            if searchHoliday != None:
                self.innerHolidays.pop(searchHoliday)
                # inform user you deleted the holiday
                print(f"{name}: {date} removed successfully.")
                break
            else:
                print(f"Error: {name}: {date} not found.")
        return print(f"test result: {self.innerHolidays}")

    def readjson(self, filelocation):
        # Read in things from json file location
        with open(filelocation) as initHolidays:
            initialHolidaysList = json.load(initHolidays)
        # [test] return initialHolidaysList
        # [test] test_list = []
        # Use addHoliday function to add holidays to inner list.
        for index, value  in enumerate(initialHolidaysList["holidays"]):
            date_list = [int(x) for x in value['date'].split("-")]
            y, m, d, = date_list[0], date_list[1], date_list[2]
            my_date = date(y, m, d)
            name = value['name'].strip().upper()
            newHoliday = Holiday(name, my_date)
                    # Make sure holidayObj is an Holiday Object by checking the type
            if isinstance(newHoliday, object):
                # Use innerHolidays.append(holidayObj) to add holiday
                self.innerHolidays.append(newHoliday)
        return # [test] print(f"test print {self.innerHolidays}")
    
    def save_to_json(self):
        holiList = [holi.__dict__ for holi in Holidays.innerHolidays]
        finalHoliList = []
        for hol in holiList:
            tempDict = {}
            tempDict["name"] = hol["name"]
            tempDict["date"] = (hol["date"]).strftime("%Y/%m/%d")
            finalHoliList.append(tempDict)
        with open("holidayList.json", "w") as f:
            json.dump(finalHoliList, f)

    def scrapeHolidays(self):
        yearList = ["2020", "2021", "", "2023", "2024"]

        # create empty holiday dict
        holidaysDict = {"holidays": []}

        # loop through pages of holiday tables to get holiday values
        for year in yearList:
            url = f"https://www.timeanddate.com/holidays/us/{year}"
            res = getResponse(url)
            soup = BeautifulSoup(getHTML(res))
            table = soup.find("table", attrs = {"id": "holidays-table"}).find("tbody")
            # loop through table rows to get names and dates
            for i in range(1, len(table)):
                table_row = table.find("tr", attrs = {"id": f"tr{i}"})
                # use if/else to skip rows that are not formatted wth id : tr{number}
                if table_row is None:
                    table_row = table.find("tr", attrs = {"id": f"tr1"})
                else:
                    # add year manually to 2022 as it's missing from the url
                    if year == "":
                        holiday_date = date_formatter(table_row.find("th", attrs = {"class": "nw"}).text, "2022")
                        holiday_name = table_row.find("a").text
                        holidaysDict["holidays"].append({"name": holiday_name, "date": holiday_date})
                    else:
                        holiday_date = date_formatter(table_row.find("th", attrs = {"class": "nw"}).text, year)
                        holiday_name = table_row.find("a").text
                        holidaysDict["holidays"].append({"name": holiday_name, "date": holiday_date})

        # load initial holiday list from file and add to temp list
        with open("initial_holidays.json") as initHolidays:
            initialHolidaysList = json.load(initHolidays)
        temp = []
        for holiday in initialHolidaysList["holidays"]:
            temp.append((holiday["name"], holiday["date"]))

        # remove duplicate values from dict list and Check to see if name and date of holiday is in innerHolidays array
        res = []
        for holiday in holidaysDict["holidays"]:
            result = (holiday["name"], holiday["date"])
            if result not in temp:
                temp.append(result)
                res.append(holiday)
        print(f'len temp: {len(temp)}')
        print(f'len res: {len(res)}')

        innerHolTestList = []
        for index, value in enumerate(res):
            # [test] print(index)
            date_list = [int(x) for x in value['date'].split("-")]
            y, m, d, = date_list[0], date_list[1], date_list[2]
            my_date = date(y, m, d)
            name = value['name'].strip().upper()
            newHoliday = Holiday(name, my_date)
                    # Make sure holidayObj is an Holiday Object by checking the type
            if isinstance(newHoliday, object):
                # Use innerHolidays.append(holidayObj) to add holiday
                self.innerHolidays.append(newHoliday)

    def numHolidays(self):
        # Return the total number of holidays in innerHolidays
        numHolidays = len(self.innerHolidays)
        return print(f"There are {numHolidays} holidays in the system currently")

# initialize HolidayList
Holidays = HolidayList()
Holidays.readjson(filelocation="initial_holidays.json")
Holidays.numHolidays()
Holidays.addHoliday()
Holidays.removeHoliday()
Holidays.scrapeHolidays()
Holidays.save_to_json()
Holidays.numHolidays()