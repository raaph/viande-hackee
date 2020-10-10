import json
import svgwrite
import math
import os
import io
import base64
import boto3
import sys


PERRSPECTIVE_X = 4
LENGTH_TOP = 10
HEIGTH = 6
WIDTH = 15
MAX_LEFT = 30
SEAT_PADDING = 15
STAIRS_WITH_LEFT = 0.9 * SEAT_PADDING
STAIRS_WITH_RIGHT = 2.1 * SEAT_PADDING
SEAT_VERTICAL_SHIFT = 7
CIRCLE_RADIUS = 5

BALCONY_OFFSET_LEFT = {0: 3, 1: 3, 2: 3}
BALCONY_OFFSET_RIGHT = {0: 10, 1: 10, 2: 10, 3: 7, 4: 7, 5: 7, 6: 5, 20: -2}

BALCONY_FIRST_ROWS = 2
BALCONY_FIRST_ROWS_MIDDLE_SEATS = 12

SMALLER_SIDE = 'left'  # meaning seat number e.g. 300 is smaller than 400
LARGER_SIDE = 'right'
MIDDLE_SIDE = 'middle'


def generate_balcony_svg(rows_json, seat):
    min_left = 0
    max_right = 0
    max_y = 0

    for row_number, row in enumerate(rows_json):
        x_offset = PERRSPECTIVE_X * row_number
        y_offset = -(LENGTH_TOP + HEIGTH) * row_number

        x_left_additional = 0
        x_right_additional = 0

        if row_number in BALCONY_OFFSET_LEFT:
            x_left_additional = BALCONY_OFFSET_LEFT[row_number] * SEAT_PADDING
        if row_number in BALCONY_OFFSET_RIGHT:
            x_right_additional = BALCONY_OFFSET_RIGHT[row_number] * \
                SEAT_PADDING

        min_left = min(min_left, x_offset - x_left_additional)
        max_right = max(max_right, x_offset + x_right_additional)
        max_y = max(max_y, -y_offset + HEIGTH + LENGTH_TOP)

        for seatNumber in range(row["left"]):
            min_left = min(min_left, x_offset - x_left_additional - STAIRS_WITH_LEFT -
                           SEAT_PADDING * seatNumber - CIRCLE_RADIUS)
        for seatNumber in range(row["right"]):
            max_right = max(max_right, x_offset + x_right_additional + STAIRS_WITH_RIGHT +
                            SEAT_PADDING * seatNumber + CIRCLE_RADIUS)

    dwg = svgwrite.Drawing(
        '/tmp/output.svg', (max_right - min_left, max_y), profile='tiny', fill="#FFFFFF")

    for row_number, row in enumerate(rows_json):

        x_offset = -min_left + PERRSPECTIVE_X * row_number
        y_offset = max_y - (LENGTH_TOP + HEIGTH) * (row_number+1)

        x_left_additional = 0
        x_right_additional = 0

        if row_number in BALCONY_OFFSET_LEFT:
            x_left_additional = BALCONY_OFFSET_LEFT[row_number] * SEAT_PADDING
        if row_number in BALCONY_OFFSET_RIGHT:
            x_right_additional = BALCONY_OFFSET_RIGHT[row_number] * \
                SEAT_PADDING

        if row_number < BALCONY_FIRST_ROWS:
            draw_stairs(dwg, x_offset + x_right_additional, y_offset)

            for seatNumber in range(BALCONY_FIRST_ROWS_MIDDLE_SEATS):
                draw_seat(dwg, x_offset - x_left_additional + STAIRS_WITH_RIGHT +
                          (SEAT_PADDING * 0.9) * seatNumber, y_offset, seat["side"] == "middle" and seat["row"] == row_number and seat["number"] == seatNumber)

        if row_number < 20:
            draw_stairs(dwg, x_offset - x_left_additional, y_offset)

        for seatNumber in range(row["left"]):
            draw_seat(dwg, x_offset - x_left_additional - STAIRS_WITH_LEFT -
                      SEAT_PADDING * seatNumber, y_offset, seat["side"] == "left" and seat["row"] == row_number and seat["number"] == seatNumber)
        for seatNumber in range(row["right"]):
            draw_seat(dwg, x_offset + x_right_additional + STAIRS_WITH_RIGHT +
                      SEAT_PADDING * seatNumber, y_offset, seat["side"] == "right" and seat["row"] == row_number and seat["number"] == seatNumber)
    dwg.save()


def generate_parquett_svg(rows_json, seat):

    min_left = 0
    max_right = 0
    max_y = 0

    for row_number, row in enumerate(rows_json):
        x_offset = -PERRSPECTIVE_X * row_number
        y_offset = (LENGTH_TOP + HEIGTH) * row_number

        min_left = min(min_left, x_offset)
        max_right = max(max_right, x_offset)
        max_y = max(max_y, y_offset + HEIGTH + LENGTH_TOP)

        min_left = min(min_left, x_offset - STAIRS_WITH_LEFT -
                       SEAT_PADDING * row["left"] - CIRCLE_RADIUS)

        max_right = max(max_right,  x_offset +
                        STAIRS_WITH_RIGHT + SEAT_PADDING * row["right"] + CIRCLE_RADIUS)

    dwg = svgwrite.Drawing(
        '/tmp/output.svg', (max_right - min_left, max_y), profile='tiny', fill="#FFFFFF")

    for row_number, row in enumerate(rows_json):
        x_offset = -min_left - PERRSPECTIVE_X * row_number
        y_offset = (LENGTH_TOP + HEIGTH) * row_number
        draw_stairs(dwg, x_offset, y_offset)

        for seatNumber in range(row["left"]):
            draw_seat(dwg, x_offset - STAIRS_WITH_LEFT -
                      SEAT_PADDING * seatNumber, y_offset, seat["side"] == "left" and seat["row"] == row_number and seat["number"] == seatNumber)

        for seatNumber in range(row["right"]):
            draw_seat(dwg, x_offset + STAIRS_WITH_RIGHT +
                      SEAT_PADDING * seatNumber, y_offset, seat["side"] == "right" and seat["row"] == row_number and seat["number"] == seatNumber)

    dwg.save()


def draw_stairs(dwg, x_offset, y_offset):
    line_color = svgwrite.rgb(255, 255, 255, '%')
    dwg.add(dwg.line((x_offset + PERRSPECTIVE_X, y_offset), (x_offset, y_offset + LENGTH_TOP),
                     stroke=line_color))
    dwg.add(dwg.line((x_offset, y_offset + LENGTH_TOP), (x_offset + WIDTH, y_offset + LENGTH_TOP),
                     stroke=line_color))
    dwg.add(dwg.line((x_offset + WIDTH, y_offset + LENGTH_TOP), (x_offset + WIDTH + PERRSPECTIVE_X, y_offset),
                     stroke=line_color))
    dwg.add(dwg.line((x_offset, y_offset + LENGTH_TOP), (x_offset, y_offset + LENGTH_TOP + HEIGTH),
                     stroke=line_color))
    dwg.add(dwg.line((x_offset, y_offset + LENGTH_TOP + HEIGTH), (x_offset + WIDTH, y_offset + LENGTH_TOP +
                                                                  HEIGTH), stroke=line_color))
    dwg.add(dwg.line((x_offset + WIDTH, y_offset + LENGTH_TOP + HEIGTH),
                     (x_offset + WIDTH, y_offset + LENGTH_TOP), stroke=line_color))


def draw_seat(dwg, x_offset, y_offset, hot_seat):

    if hot_seat:
        dwg.add(dwg.circle(
            center=(x_offset, SEAT_VERTICAL_SHIFT + y_offset), r=5, stroke="#FACE48", fill="#FACE48"))
    else:
        dwg.add(dwg.circle(
            center=(x_offset, SEAT_VERTICAL_SHIFT + y_offset), r=5, stroke="#000000", fill="#a6a6a6"))


def lambda_handler(event, context):
    inputParameters = event['seat_name'].split('-')
    block_number = inputParameters[0]
    row_number = int(inputParameters[1])
    seat_number = int(inputParameters[2])

    # get reference to S3 client
    s3_resource = boto3.resource('s3')

    # get stadium_data.json
    second_object = s3_resource.Object(
        bucket_name="svg-seat-maps", key="stadium_data.json")
    response = second_object.get()

    # read the contents of the file
    lines = response['Body'].read()
    # saving the file data in a new file test.csv
    with open('/tmp/stadium_data.json', 'wb') as file:
        file.write(lines)

    rows = prepare_block_for_drawing(block_number)
    highlighted_seat = get_highlighted_seat(
        block_number, row_number, seat_number)

    block = get_block(block_number)

    if block['level'] == 'Balkon':
        generate_balcony_svg(rows, highlighted_seat)
    else:
        generate_parquett_svg(rows, highlighted_seat)

    filename = f"{block_number}-{row_number}-{seat_number}.svg"

    first_object = s3_resource.Object(
        bucket_name="svg-seat-maps", key=filename)

    first_object.upload_file(
        "/tmp/output.svg", ExtraArgs={'ContentType': 'image/svg+xml'})

    return {
        'statusCode': 200,
        'body': json.dumps({'filename': filename})
    }


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
            subtract_amount = BALCONY_FIRST_ROWS_MIDDLE_SEATS

        if keys[0] < keys[1]:
            prepared_row[SMALLER_SIDE] = counted_seats_dict[keys[0]]
            prepared_row[LARGER_SIDE] = counted_seats_dict[keys[1]
                                                           ] - subtract_amount
        else:
            prepared_row[SMALLER_SIDE] = counted_seats_dict[keys[1]]
            prepared_row[LARGER_SIDE] = counted_seats_dict[keys[0]
                                                           ] - subtract_amount

    prepared_rows.reverse()
    return prepared_rows


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

    highlighted_seat['row'] = row_number - 1

    if seat_number in sorted_seats[keys[0]]:
        sorted_seats[keys[0]].sort()
        if keys[0] < keys[1]:
            highlighted_seat['side'] = SMALLER_SIDE
            # count from top to bottom
            highlighted_seat['number'] = count_seats_from_stairs(
                sorted_seats[keys[0]], seat_number, False)
        else:
            highlighted_seat['side'] = LARGER_SIDE
            # count from bottom to top
            highlighted_seat['number'] = count_seats_from_stairs(
                sorted_seats[keys[0]], seat_number, True)

    else:
        sorted_seats[keys[1]].sort()
        if keys[0] < keys[1]:
            block = get_block(block_number)
            if block['level'] == 'Balkon' and row['number'] < 3:
                if seat_number % 100 < BALCONY_FIRST_ROWS_MIDDLE_SEATS:
                    highlighted_seat['side'] = MIDDLE_SIDE
                    highlighted_seat['number'] = seat_number % 100
                else:
                    highlighted_seat['side'] = LARGER_SIDE
                    # count from bottom to top
                    highlighted_seat['number'] = count_seats_from_stairs(
                        sorted_seats[keys[1]], seat_number, True) - BALCONY_FIRST_ROWS_MIDDLE_SEATS

            else:
                highlighted_seat['side'] = LARGER_SIDE
                # count from bottom to top
                highlighted_seat['number'] = count_seats_from_stairs(
                    sorted_seats[keys[1]], seat_number, True)
        else:
            highlighted_seat['side'] = SMALLER_SIDE
            # count from top to bottom
            highlighted_seat['number'] = count_seats_from_stairs(
                sorted_seats[keys[1]], seat_number, False)
    return highlighted_seat


def get_block(block_number):
    stadium_json = get_json("/tmp/stadium_data.json")
    blocks = stadium_json['blocks']

    for block in blocks:
        if block['number'].lower() == block_number.lower():
            return block

    raise Exception('No block found with name {0!s}!'.format(block_number))


def get_row(block_number, row_number):
    block = get_block(block_number)
    for row in block['rows']:
        if int(row['number']) == int(row_number):
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
        if int(seat) == int(seat_number):
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
