import requests
import json
import pandas as pd
from datetime import datetime

HOST = 'https://www.speedrun.com/api/v1/'
GAME_ID = '268zey6p' # id for majora's mask
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

def main():
    startTime =  datetime.now()

    final_data = add_time()
    df = pd.DataFrame.from_dict({'Username':final_data.keys(), 'Total Time':final_data.values()})
    df.sort_values(by=['Total Time'], ascending=False, inplace=True)
    df['Total Time'] = df['Total Time'].apply(convert_to_hours)
    df.reset_index(drop=True, inplace=True)

    df.to_csv('output.csv', index=False)

    print('Execution time: ' + str(datetime.now() - startTime))

def make_list():
    full_list = []
    offset = 0
    runs = requests.get(HOST + 'runs?max=200&embed=players&game=' + GAME_ID, headers=headers)
    dict = runs.json()

    # loop through all pages (max 200 runs/page) and add to one big list
    while dict['pagination']['size'] == 200:
        runs = requests.get(HOST + 'runs?max=200&embed=players&game=' + GAME_ID + '&offset=' + str(offset), headers=headers)
        dict = runs.json()
        ##new test code
        if not dict.get('data'):
            print ('number of runs processed: ' + str(len(full_list)))
        full_list.extend(dict['data'])
        offset += 200

    return full_list


def add_time():
    print('Fetching runs...')
    runs = make_list()
    player_times = {}

    for i in range(len(runs)):
        if runs[i]['players']['data'][0].get('names'):
            player = runs[i]['players']['data'][0]['names']['international']
        else:
            player = runs[i]['players']['data'][0]['name']


        time = runs[i]['times']['primary_t']

        if player in player_times:
            player_times[player] += time
        else:
            player_times[player] = time

    print('All done! Check output.csv')

    return player_times

def convert_to_hours(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    h = str(int(h))
    m = str(int(m))
    s = str(int(s))

    if len(m) == 1:
        m = '0' + m

    if len(s) == 1:
        s = '0' + s

    return h + ':' + m + ':' + s

if __name__ == '__main__':
    main()