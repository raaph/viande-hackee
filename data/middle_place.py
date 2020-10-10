import math
import json

blocks = []
with open('stadium_data.json') as file:
    blocks = json.load(file)["blocks"]


SMALLER_SIDE = 'left'  # meaning seat number e.g. 300 is smaller than 400
LARGER_SIDE = 'right'
MIDDLE_SIDE = 'middle'

BALCONY_FIRST_ROWS = 2
BALCONY_FIRST_ROWS_MIDDLE_SEATS = 12

res = {}
for block in blocks:

    min_seat = 100000000
    max_seat = 0
    for row in block["rows"]:
        tmp_min = min(row["seats"])
        tmp_max = max(row["seats"])
        min_seat = min(min_seat, tmp_min)
        max_seat = max(max_seat, tmp_max)

    res[block["number"]] = {"min": min_seat, "max": max_seat}


with open("minmax.json", "+w") as file:
    json.dump(res, file)


def prepare_block_for_drawing(block_number):
    block = get_block(block_number)
    prepared_rows = []

    for row in block['rows']:
        prepared_row = {}
        prepared_rows.append(prepared_row)

        print("###################")
        print(row["seats"])
        counted_seats_dict = count_seats(row['seats'])
        print(counted_seats_dict)
        keys = list(counted_seats_dict.keys())
        print(keys)
        if len(keys) == 1:
            if 1 in keys:
                counted_seats_dict[0] = 0
            else:
                counted_seats_dict[1000] = 0
            keys = list(counted_seats_dict.keys())

        subtract_amount = 0
        if block['level'] == 'Balkon' and row['number'] < 3:
            subtract_amount = BALCONY_FIRST_ROWS_MIDDLE_SEATS

        if keys[0] < keys[1]:
            prepared_row[SMALLER_SIDE] = counted_seats_dict[keys[0]]
            prepared_row[LARGER_SIDE] = counted_seats_dict[keys[1]
                                                           ] - subtract_amount
        else:
            prepared_row[SMALLER_SIDE] = counted_seats_dict[keys[1]]
            prepared_row[LARGER_SIDE] = counted_seats_dict[keys[0]
                                                           ] - subtract_amount
        if block['level'] == 'Parkett':
            prepared_rows.reverse()
    return prepared_rows


def get_block(block_number):
    stadium_json = get_json("stadium_data.json")
    blocks = stadium_json['blocks']

    for block in blocks:
        if block['number'].lower() == block_number.lower():
            return block

    raise Exception('No block found with name {0!s}!'.format(block_number))


def get_json(filepath):
    f = open(filepath, "r")
    content = f.read()
    f.close()
    return json.loads(content)


def count_seats(seats):
    count_dict = {}
    sorted_seats = sort_seats(seats)

    for seat_key in sorted_seats.keys():
        count_dict[seat_key] = len(sorted_seats[seat_key])

    return count_dict


def sort_seats(seats):
    sorted_dict = {}
    for seat in seats:
        key_value = int(seat/100)
        if key_value in sorted_dict:
            sorted_dict[key_value].append(seat)
        else:
            sorted_dict[key_value] = [seat]
    return sorted_dict


print(prepare_block_for_drawing("C4"))
