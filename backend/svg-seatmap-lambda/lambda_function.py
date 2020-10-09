import json
import svgwrite
import math
import os
import io
import shutil
import subprocess
import base64
import zipfile
import boto3
import requests
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
BALCONY_OFFSET_RIGHT = {0: 10, 1: 10, 2: 10, 3: 7, 4: 7, 5: 7, 6: 5, 13: -2}

BALCONY_FIRST_ROWS = 2
BALCONY_FIRST_ROWS_MIDDLE_SEATS = 12


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
        'output/balcony.svg', (max_right - min_left, max_y), profile='tiny', fill="#FFFFFF")
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'),
                     rx=None, ry=None, fill='#000000'))

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

        if row_number < 12:
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
        'output/parquett.svg', (max_right - min_left, max_y), profile='tiny', fill="#FFFFFF")
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'),
                     rx=None, ry=None, fill='#000000'))

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

    os.mkdir("/output")

    generate_parquett_svg([
        {"left": 10, "right": 10},
        {"left": 10, "right": 10},
        {"left": 10, "right": 10},
        {"left": 10, "right": 10},
        {"left": 10, "right": 8},
        {"left": 10, "right": 6},
        {"left": 10, "right": 4},
        {"left": 10, "right": 2}
    ], {"side": "right", "row": 1, "number": 1})

    generate_balcony_svg([
        {"left": 7, "right": 3},
        {"left": 7, "right": 3},
        {"left": 7, "right": 3},
        {"left": 10, "right": 6},
        {"left": 10, "right": 6},
        {"left": 10, "right": 6},
        {"left": 7, "right": 8},
        {"left": 7, "right": 9}
    ], {"side": "right", "row": 1, "number": 1})

    # get reference to S3 client
    s3_resource = boto3.resource('s3')
    first_object = s3_resource.Object(
        bucket_name="/svg-seat-maps", key="test.svg")

    first_object.upload_file("output/parquett.svg")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello romain')
    }
