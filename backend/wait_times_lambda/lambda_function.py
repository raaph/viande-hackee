import json
import pandas as pd
import numpy as np
import boto3

#delare a function to know if a game is playing today


def is_game_day(date_time, games_schedule):
    date = np.datetime_as_string(date_time, unit='D')
    date = str(date)
    games_today = games_schedule.loc[games_schedule['date'] == date]
    return games_today

#delare a function to know if a game is "currently" playing
#we don't consider the case where the game has overtime


def is_game_time(date_time, games_schedule):
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


def time_since_start(date_time, games_schedule):
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


def q_times(date_time):
    # read data frame from s3
    games_schedule = pd.read_json('/tmp/games_schedule.json')
    waiting_times = pd.read_csv(
        '/tmp/yb_waiting_times_minutes.csv', index_col=['minutes_since_start'])

    ret = {
    }
    game_day = is_game_day(date_time, games_schedule)
    gameTitle = game_day['home'].values+' vs '+game_day['Away'].values
    ret['GameTitle'] = gameTitle[0]

    game_day = len(game_day)
    if float(game_day) > 1:
        ret["response"] = "Error"
    elif float(game_day) == 0:
        ret["response"] = "No game today"
    elif is_game_time(date_time, games_schedule) == 0:
        ret["response"] = "Game hasn't started yet"
    elif is_game_time(date_time, games_schedule) == 2:
        ret["response"] = "Game has ended"
    else:

        delta = time_since_start(date_time, games_schedule)
        waiting_times_row = waiting_times.loc[delta]
        waiting_times_next_row = waiting_times.loc[min(delta+1, 120)]
        ret["response"] = "good"

        lst1 = ["catering_a", "catering_b", "catering_c", "catering_d",
                "catering_e", "men_1", "men_2", "women_1", "women_2"]
        lst2 = ["frites1", "saucisse1", "pizza", "saucisse2",
                "frites2", "homme1", "homme2", "femme1", "femme2"]
        lst_type = ['c', 'c', 'c', 'c', 'c', 'w', 'w', 'w', 'w']
        lst = []
        i = -1
        for name in lst1:
            i += 1
            lst.append({
                'title': lst2[i],
                'time': waiting_times_row[name],
                'forecast': waiting_times_next_row[name]-waiting_times_row[name],
                'type': lst_type[i]
            })

        ret['time'] = lst
    return ret


#---faudra supprimer dans le lambda
# sector='C'
# date_time=np.datetime64('2020-10-10T15:48:00.000000000')


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)
    date_time = np.datetime64(event['date_time'])  # 2020-10-10T15:15')
    # get reference to S3 client
    s3_resource = boto3.resource('s3')
    for filename in ["games_schedule.json", "yb_waiting_times_minutes.csv"]:
        first_object = s3_resource.Object(
            bucket_name="svg-seat-maps", key=filename)
        # get the object
        response = first_object.get()
        # read the contents of the file
        lines = response['Body'].read()
        # saving the file data in a new file test.csv
        with open(f'/tmp/{filename}', 'wb') as file:
            file.write(lines)

    ret = q_times(date_time)

    return {
        'statusCode': 200,
        'body': json.dumps(ret)
    }
