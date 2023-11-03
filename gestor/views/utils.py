from datetime import datetime, timedelta


def getWeek(dt=None):
    """ 
    The given code defines a function called "getWeek" which takes an optional 
    argument "dt". If no argument is provided, the current date and time are 
    obtained using the "datetime.now()" method. If an argument is provided, it 
    is expected to be a string in the format "mmddyyyy" and is converted to a 
    datetime object using the "datetime.strptime()" method. 
    The function then calculates the start and end dates of the week containing 
    the provided or current date. The start date is obtained by subtracting the 
    number of days equal to the weekday of the date. The end date is obtained by 
    adding 7 days to the start date. 
    Additionally, the function calculates the previous week by subtracting 7 
    days from the provided or current date, and the next week by adding 7 days 
    to the provided or current date. 
    Finally, the function returns a tuple containing the start and end dates of 
    the week, the previous week, and the next week
    """

    if dt is None:
        dt = datetime.now()
    else:
        dt = datetime.strptime(dt, "%m%d%Y")
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=7)
    previousWeek = dt - timedelta(days=7)
    nextWeek = dt + timedelta(days=7)
    return (start.date(), end.date(), previousWeek, nextWeek)


def getMonthYear(month=None, year=None):
    """ 
    This function,  `getMonthYear` , takes in two optional parameters,  
    `month`  and  `year` , and returns a tuple containing three tuples. 
    The first tuple within the result contains the previous month and year. 
    If the current month is January, the previous month will be December of the 
    previous year. 
    The second tuple within the result contains the current month and year. 
    If no values are provided for  `month`  and  `year` , the current month and 
    year are determined using the  `datetime.now()`  function. 
    The third tuple within the result contains the next month and year. If the 
    current month is December, the next month will be January of the next year. 
    If the  `month`  parameter is provided, it is validated to ensure it is a 
    valid month value (between 1 and 12). If it is not valid, a  `ValueError`  
    is raised. 
    If the  `year`  parameter is provided, it is converted to an integer. 
    The function returns the three tuples as a result.
    """
    # Current
    if month is None:
        currentMonth = datetime.now().month
    else:
        month = int(month)
        if month > 12 or month < 0:
            raise ValueError(F'Wrong month value: {month}!')
        currentMonth = month
    if year is None:
        currentYear = datetime.now().year
    else:
        year = int(year)
        currentYear = year

    # Next
    nextYear = currentYear
    nextMonth = currentMonth + 1
    if nextMonth > 12:
        nextMonth = 1
        nextYear = currentYear+1

    # Previous
    previousYear = currentYear
    previousMonth = currentMonth - 1
    if previousMonth < 1:
        previousMonth = 12
        previousYear = currentYear-1

    return ((previousMonth, previousYear), (currentMonth, currentYear), (nextMonth, nextYear))
