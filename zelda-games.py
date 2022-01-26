import requests
import json
import pandas as pd
from datetime import datetime
import sqlalchemy
import sqlite3

HOST = 'https://www.speedrun.com/api/v1/'
GAME_SERIES = 'zelda'
DATABASE_LOCATION = 'sqlite:///player_times.sqlite'

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
id_to_game = json.load(open('id-game-map.json'))

def main():
    startTime =  datetime.now()

    #id_list = list(id_to_game.keys())
    id_list = ['268zey6p', '4d709l17', 'j1l9qz1g']
    game_count = 1

    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    conn = sqlite3.connect('player_times.sqlite')
    print('Opened database successfully')

    engine.execute('DROP TABLE IF EXISTS Speedruns')

    for id in id_list:

        print('Fetching all runs for: ' + id_to_game[id] + ' (' + str(game_count) + '/' + str(len(id_list)) + ')',)

        # create and format the dataframe
        data = add_runs(id)

        df = pd.DataFrame(data, columns = ['Username', 'TotalTime', 'Game'])
        df = df.groupby(['Username', 'Game'], as_index=False).sum()
        df.sort_values(by=['TotalTime'], ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df['TotalTime'] = df['TotalTime'].apply(convert_to_hours)


        # engine = sqlalchemy.create_engine(DATABASE_LOCATION)
        # conn = sqlite3.connect('player_times.sqlite')
        #cursor = conn.cursor()

        #engine.execute('DROP TABLE IF EXISTS Speedruns')

        # sql_query = '''
        #     CREATE TABLE IF NOT EXISTS Speedruns (
        #     ID INTEGER PRIMARY KEY,
        #     Username TEXT NOT NULL,
        #     TotalTime TEXT NOT NULL,
        #     Game TEXT NOT NULL
        # )
        # '''

        #cursor.execute(sql_query)

        df.to_sql('Speedruns', engine, index=False, if_exists='append')




        game_count += 1

    conn.close()
    print('Closed database successfully')
    print('Execution time: ' + str(datetime.now() - startTime))

def make_list(game_id):
    full_list = []
    offset = 0
    runs = requests.get(HOST + 'runs?max=200&embed=players&game=' + game_id)
    dict = runs.json()

    while dict['pagination']['size'] == 200:
        runs = requests.get(HOST + 'runs?max=200&embed=players&game=' + game_id + '&offset=' + str(offset))
        dict = runs.json()
        full_list.extend(dict['data'])
        offset += 200

    return full_list


def add_runs(game_id):

    print('Making list for: ' + id_to_game[game_id] + '...')
    runs = make_list(game_id)
    usernames = []
    times = []
    games = []
    run_count = 1


    for i in range(len(runs)):
        print('Adding run data + (' + str(run_count) + '/' + str(len(runs)) + ')', end='\r')
        if runs[i]['players']['data'][0].get('names'):
            usernames.append(runs[i]['players']['data'][0]['names']['international'])
        else:
            usernames.append(runs[i]['players']['data'][0]['name'])

        times.append(runs[i]['times']['primary_t'])
        games.append(id_to_game[game_id])

        run_count += 1

    player_times = {
        'Username' : usernames,
        'TotalTime' : times,
        'Game' : games,
    }

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