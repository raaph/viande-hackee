import json
import pandas as pd
import numpy as np
import boto3

#read data frame from s3
games_schedule = pd.read_json ('games_schedule.json')
waiting_times = pd.read_csv('yb_waiting_times_minutes.csv', index_col=['minutes_since_start'])


#delare a function to know if a game is playing today
def is_game_day(date_time):
    date = np.datetime_as_string(date_time, unit='D')
    date=str(date)
    games_today = games_schedule.loc[games_schedule['date'] == date]
    return len(games_today)

#delare a function to know if a game is "currently" playing
#we don't consider the case where the game has overtime
def is_game_time(date_time):
    date = np.datetime_as_string(date_time, unit='D')
    date = str(date)
    games_today = games_schedule.loc[games_schedule['date'] == date]
    d = games_today['date'].values[0]
    t = games_today['kickoff'].values[0]
    d_t = np.datetime_as_string(d, unit='D') + 'T' + t
    game_start = np.datetime64(d_t) - np.timedelta64(30, 'm')
    game_end = np.datetime64(d_t) + np.timedelta64(120, 'm')
    ret = 0
    if np.datetime64(date_time) < game_start:
        ret = 0
    elif np.datetime64(date_time) > game_end:
        ret = 2
    else:
        ret = 1
    return ret

def time_since_start(date_time):
    date = np.datetime_as_string(date_time, unit='D')
    date = str(date)
    games_today = games_schedule.loc[games_schedule['date'] == date]
    d = games_today['date'].values[0]
    t = games_today['kickoff'].values[0]
    d_t = np.datetime_as_string(d, unit='D') + 'T' + t
    delta = date_time-np.datetime64(d_t)
    delta = delta.astype('timedelta64[m]')
    delta = delta / np.timedelta64(1, 'm')
    return delta

#declare the main function
#inputs : sector, time
#the sector argument won't be used in this function
#since we only focus on one sector
def q_times(sector, date_time):
    ret = {
    }
    game_day = is_game_day(date_time)

    if float(game_day)>1:
        ret["response"] = "Error"
    elif float(game_day)==0:
        ret["response"] = "No game today"
    elif is_game_time(date_time)==0:
        ret["response"] = "Game hasn't started yet"
    elif is_game_time(date_time)==2:
        ret["response"] = "Game has ended"
    else:

        delta = time_since_start(date_time)
        waiting_times_row = waiting_times.loc[delta]
        waiting_times_next_row = waiting_times.loc[min(delta+1,120)]
        ret["response"] = "good"
        ret["times"] = {
            'catering_a': waiting_times_row["catering_a"],
            'catering_a_prevision': waiting_times_next_row["catering_a"]-waiting_times_row["catering_a"],
            'catering_b': waiting_times_row["catering_b"],
            'catering_b_prevision': waiting_times_next_row["catering_b"]-waiting_times_row["catering_b"],
            'catering_c': waiting_times_row["catering_c"],
            'catering_c_prevision': waiting_times_next_row["catering_c"]-waiting_times_row["catering_c"],
            'catering_d': waiting_times_row["catering_d"],
            'catering_d_prevision': waiting_times_next_row["catering_d"]-waiting_times_row["catering_d"],
            'catering_e': waiting_times_row["catering_e"],
            'catering_e_prevision': waiting_times_next_row["catering_e"]-waiting_times_row["catering_e"],
            'men_1': waiting_times_row["men_1"],
            'men_1_prevision': waiting_times_next_row["men_1"]-waiting_times_row["men_1"],
            'women_1': waiting_times_row["women_1"],
            'women_1_prevision': waiting_times_next_row["women_1"]-waiting_times_row["women_1"],
            'men_2': waiting_times_row["men_2"],
            'men_2_prevision': waiting_times_next_row["men_2"]-waiting_times_row["men_2"],
            'women_2': waiting_times_row["women_2"],
            'women_2_prevision': waiting_times_next_row["women_2"]-waiting_times_row["women_2"],
        }

    return ret







#---faudra supprimer dans le lambda
sector='C'
date_time=np.datetime64('2020-10-10T15:48:00.000000000')










def lambda_handler(event, context):
    # get reference to S3 client
    s3_resource = boto3.resource('s3')
    first_object = s3_resource.Object(
        bucket_name="ybh-waiting-data", key="games_schedule.json")
    # get the object
    response = first_obj.get()
    # read the contents of the file
    lines = response['Body'].read()
    # saving the file data in a new file test.csv
    with open('/tmp/yb_waiting_times_minutes.csv', 'wb') as file:
        file.write(lines)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
