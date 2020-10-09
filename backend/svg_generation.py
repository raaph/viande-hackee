import json

SMALLER_SIDE = 'left' # meaning 300 is smaller than 400
LARGER_SIDE = 'right'
MIDDLE_SIDE = 'middle'
MIDDLE_SEATS_COUNT = 12

def prepare_block_for_drawing(block_number):
    block = get_block(block_number)
    prepared_rows = []

    for row in block['rows']:
        prepared_row = {}
        prepared_rows.append(prepared_row)

        counted_seats_dict = count_seats(row['seats'])
        
        keys = list(counted_seats_dict.keys())
        if len(keys) == 1:
            if 1 in keys:
                counted_seats_dict[0] = 0
            else:
                counted_seats_dict[1000] = 0
            keys = list(counted_seats_dict.keys())

        subtract_amount = 0
        if block['level'] == 'Balkon' and row['number'] < 3:
            subtract_amount = MIDDLE_SEATS_COUNT

        if keys[0] < keys[1]:
            prepared_row[SMALLER_SIDE] = counted_seats_dict[keys[0]]
            prepared_row[LARGER_SIDE] = counted_seats_dict[keys[1]] - subtract_amount
        else:
            prepared_row[SMALLER_SIDE] = counted_seats_dict[keys[1]]
            prepared_row[LARGER_SIDE] = counted_seats_dict[keys[0]] - subtract_amount

    prepared_rows.reverse()
    return json.dumps(prepared_rows)

def get_highlighted_seat(block_number, row_number, seat_number):
    row = get_row(block_number, row_number)
    highlighted_seat = {}
    sorted_seats = sort_seats(row['seats'])

    keys = list(sorted_seats.keys())
    if len(keys) == 1:
        if 1 in keys:
            sorted_seats[0] = []
        else:
            sorted_seats[1000] = []
        keys = list(sorted_seats.keys())

    highlighted_seat['row'] = row_number

    if seat_number in sorted_seats[keys[0]]:
        sorted_seats[keys[0]].sort()
        if keys[0] < keys[1]:
            highlighted_seat['side'] = SMALLER_SIDE
            # count from top to bottom
            highlighted_seat['number'] = count_seats_from_stairs(sorted_seats[keys[0]], seat_number, False)
        else:
            highlighted_seat['side'] = LARGER_SIDE
            # count from bottom to top
            highlighted_seat['number'] = count_seats_from_stairs(sorted_seats[keys[0]], seat_number, True)
        
    else:
        sorted_seats[keys[1]].sort()
        if keys[0] < keys[1]:
            block = get_block(block_number)
            if block['level'] == 'Balkon' and row['number'] < 3:
                if seat_number % 100 < MIDDLE_SEATS_COUNT:
                    highlighted_seat['side'] = MIDDLE_SIDE
                    highlighted_seat['number'] = seat_number % 100
                else:
                    highlighted_seat['side'] = LARGER_SIDE
                    # count from bottom to top
                    highlighted_seat['number'] = count_seats_from_stairs(sorted_seats[keys[1]], seat_number, True) - MIDDLE_SEATS_COUNT

            else:
                highlighted_seat['side'] = LARGER_SIDE
                # count from bottom to top
                highlighted_seat['number'] = count_seats_from_stairs(sorted_seats[keys[1]], seat_number, True)
        else:
            highlighted_seat['side'] = SMALLER_SIDE
            # count from top to bottom
            highlighted_seat['number'] = count_seats_from_stairs(sorted_seats[keys[1]], seat_number, False)
    return json.dumps(highlighted_seat)
    

def get_block(block_number):
    stadium_json = get_json("./data/stadium_data.json")
    blocks = stadium_json['blocks']

    for block in blocks:
        if block['number'].lower() == block_number.lower():
            return block

    raise Exception('No block found with name {0!s}!'.format(block_number))        

def get_row(block_number, row_number):
    block = get_block(block_number)
    for row in block['rows']:
        if row['number'] == row_number:
            return row

    raise Exception('No row found with number {0!s}!'.format(row_number))    


def get_json(filepath):
    f = open(filepath, "r")
    content = f.read()
    f.close()
    return json.loads(content)

def count_seats_from_stairs(sorted_seats, seat_number, count_bottom_up):
    counter = 0
    if not count_bottom_up:
        sorted_seats.reverse()
    for seat in sorted_seats:
        if seat == seat_number:
            return counter
        counter += 1
    
    raise Exception('No seat found with number {0!s}!'.format(seat_number))    

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
