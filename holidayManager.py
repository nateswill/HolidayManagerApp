from datetime import datetime
from datetime import date
import datetime
import json
from xmlrpc.client import DateTime
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from config import initialListLocation

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

# fucntion to validate interger input
def get_int(prompt):
    my_int = 0

    is_valid = False

    while not is_valid:
        try:
            my_int = int(input(prompt))
            is_valid = True
        except:
            print('Invalid Integer, try again.')
    return my_int
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
            searchHoliday = self.findHoliday(HolidayName = Holiday(name, date))
            # [test] print(f"removeHoliday: searchHoliday result: {searchHoliday}")
            # remove the Holiday from innerHolidays
            if searchHoliday != None:
                self.innerHolidays.pop(searchHoliday)
                # inform user you deleted the holiday
                print(f"{name}: {date} removed successfully.")
                break
            else:
                print(f"Error: {name}: {date} not found.")
        return # [test] print(f"test result: {self.innerHolidays}")

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
        print("Saving a Holiday List")
        print("=====================")
        choice = input("Are you sure you want to save your changes? [y/n]: ")
        if choice == "y":
            holiList = [holi.__dict__ for holi in self.innerHolidays]
            finalHoliList = []
            for hol in holiList:
                tempDict = {}
                tempDict["name"] = hol["name"]
                tempDict["date"] = (hol["date"]).strftime("%Y/%m/%d")
                finalHoliList.append(tempDict)
            with open("holidayList.json", "w") as f:
                json.dump(finalHoliList, f)
            print("Success:\n Your changes have been saved.")
        else:
            print("Holiday list file save cancled.")

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

    def filterHolidaysByWeek(self, yearNum, weekNum = datetime.date.today().isocalendar()[2]):
        # Use a Lambda function to filter by week number and save this as holidays, use the filter on innerHolidays
        filteredHolidaysWeek = list(filter(lambda x: int(x.date.strftime("%U")) == weekNum, self.innerHolidays))
        filteredHolidaysYearWeek = list(filter(lambda x: x.date.isocalendar().year == yearNum, filteredHolidaysWeek))
        for holiday in filteredHolidaysYearWeek:
            print(holiday)
        return

    def viewHolidays(self):
        print("View Holidays")
        print("=============")
        yearChoice = get_int("Which year?")
        weekChoice = get_int("Which week? #[1-52, Enter 0 for the current week")
        if weekChoice == 0:
            self.filterHolidaysByWeek(yearNum = yearChoice)
        else:
            self.filterHolidaysByWeek(yearNum = yearChoice, weekNum = weekChoice)

    def exit(self):
        print('Exit')
        print('====')
        print('Any unsaved changes will be lost.')
        resp = input('Are you sure you want to exit? [y/n]')
        if resp == 'y':
            return False
        else:
            return True

def main():
    # Large Pseudo Code steps
    # -------------------------------------
    # 1. Initialize HolidayList Object
    Holidays = HolidayList()

    # 2. Load JSON file via HolidayList read_json function
    Holidays.readjson(filelocation=initialListLocation)

    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    #Holidays.scrapeHolidays()

    # 4. Create while loop for user to keep adding or working with the Calender
    validUse = True
    while validUse:

    # 5. Display User Menu (Print the menu)
        print('Holiday Menu')
        print('============')
        print('1 - Add a Holiday')
        print('2 - Remove a Holiday')
        print('3 - Save a Holiday List')
        print('4 - View Holidays')
        print('5 - Exit')
    # 6. Take user input for their action based on Menu and check the user input for errors
    # 7. Run appropriate method from the HolidayList object depending on what the user input is
        option = get_int('Enter preferred option to proceed')
        if option == 1:
            Holidays.addHoliday()
        elif option == 2:
            Holidays.removeHoliday()
        elif option == 3:
            Holidays.save_to_json()
        elif option == 4:
            Holidays.viewHolidays()
        else:
            validUse = Holidays.exit()
    

    # 8. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going.

if __name__ == "__main__":
    main();

#main()
# initialize HolidayList
# Holidays = HolidayList()
# Holidays.readjson(filelocation="initial_holidays.json")
# Holidays.numHolidays()
# Holidays.addHoliday()
# Holidays.removeHoliday()
# Holidays.scrapeHolidays()
# Holidays.save_to_json()
# Holidays.numHolidays()
# Holidays.viewHolidays()