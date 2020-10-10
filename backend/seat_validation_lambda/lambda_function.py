import json
import boto3

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

    validation_result = validate(block_number, row_number, seat_number)

    return {
        'statusCode': 200,
        'body': json.dumps({'result': validation_result})
    }

def validate(block_number, row_number, seat_number):
    validate = False
    try:
        validate = validate_seat(block_number, row_number, seat_number)
    finally:
        return validate
    

def validate_seat(block_number, row_number, seat_number):
    row = get_row(block_number, row_number)
    for seat in row['seats']:
        if int(seat) == int(seat_number):
            return True
    return False

def get_row(block_number, row_number):
    block = get_block(block_number)
    for row in block['rows']:
        if int(row['number']) == int(row_number):
            return row

    raise Exception('No row found with number {0!s}!'.format(row_number))  

def get_block(block_number):
    stadium_json = get_json("/tmp/stadium_data.json")
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

