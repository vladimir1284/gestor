import pygsheets
gc = pygsheets.authorize(
    service_file='trailer-rental-323614-d43be7453c41.json')

# open the google spreadsheet (where 'test' is the name of my sheet)
sh = gc.open('test')

# select the first sheet
wks = sh.sheet1

# update the first sheet with df, starting at cell B2.
wks.update_value('A3', "Numbers on Stuff")
