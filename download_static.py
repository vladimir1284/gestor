import os
import requests

base_dir = "/home/vladimir/Sync/JA/ERM/"
fname = base_dir+"static_dir_2912.txt"

base_url = "http://towithouston.com/erp/media/"

with open(fname, 'r') as f:
    lines = f.readlines()

# Parse lines
lineno = 0
while lineno < len(lines):
    directory = lines[lineno][:-2].split("static/")[1]
    print(F"Directory: {directory}")
    try:
        os.mkdir(base_dir+'img_bk/'+directory)
    except FileExistsError:
        pass
    lineno += 2  # Skip dir size
    while (lineno < len(lines) and lines[lineno] != "\n"):
        file_name = lines[lineno].split()[-1]
        # Check if the file exists
        file_path = base_dir+'img_bk/'+directory+'/' + file_name
        if not os.path.exists(file_path):
            # Download
            print(F"downloading: {file_name}")
            myfile = requests.get(base_url+directory+'/'+file_name)
            open(file_path, 'wb').write(myfile.content)

        lineno += 1

    lineno += 1  # Skip empty line
