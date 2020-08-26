import subprocess
import os

import pandas as pd
import numpy as np

from datetime import datetime

# Access websites
import requests
# Access json files
import json

def get_john_hopkins():
   # Running a process using 'git' to get the data from 'cwd'
   # shell == True the specified command will be executed through the shell.
   # stdin, stdout and stderr specify the executed program’s standard input, standard output and standard error file handles, respectively.
   # .communicate() writes input, reads all output, and waits for the subprocess to exit.
    git_pull = subprocess.Popen('/usr/bin/git pull' ,
    cwd = os.path.dirname('data/raw/COVID-19/'),
    shell = True,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE)

    (out, error) = git_pull.communicate()

    print("Error: " + str(error))
    print("out: " + str(out))


def get_current_data_germany():
    data = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json')

    json_object = json.loads(data.content)
    full_list = []
    for pos, each_dict in enumerate(json_object['features'][:]):
        full_list.append(each_dict['attributes'])

    pd_full_list = pd.DataFrame(full_list)
    pd_full_list.to_csv('data/raw/NPGEO/GER_state_data.csv',sep=';')
    print('Number of region rows:' +str(pd_full_list.shape[0]))

if __name__ == '__main__':
    get_john_hopkins()
    get_current_data_germany()
