import requests
import json


urlBlocks = 'https://static.pacifa3d.com/StadeDeSuisseBERN/WIMS/BSCYB_FOOTBALL_v2020-2021/f/w/blocks.json'
responseBlocks = requests.get(urlBlocks)
blocksJson = json.loads(responseBlocks.text)
blocks = []

for blockName in blocksJson:
    block = {}
    blocks.append(block)
    block['number'] = blockName.split(' ')[0]
    block['level'] = blockName.split(' ')[1]

    urlRows = 'https://static.pacifa3d.com/StadeDeSuisseBERN/WIMS/BSCYB_FOOTBALL_v2020-2021/f/w/{0!s}.json'.format(blockName)
    responseRows = requests.get(urlRows)
    rowsJson = json.loads(responseRows.text)
    block['rows'] = []

    for rowNumber in rowsJson:
        row = {}
        block['rows'].append(row)
        row['number'] = int(rowNumber)

        urlSeats = 'https://static.pacifa3d.com/StadeDeSuisseBERN/WIMS/BSCYB_FOOTBALL_v2020-2021/f/w/{0!s}.{1!s}.json'.format(blockName, rowNumber)
        responseSeats = requests.get(urlSeats)
        panoJson = json.loads(responseSeats.text)
        row['seats'] = []

        for pano in panoJson:
            seatsJson = pano['seats']

            for seatNumber in seatsJson:
                row['seats'].append(int(seatNumber))

stadium = {}
stadium['blocks'] = blocks

stadiumJson = json.dumps(stadium)

f = open("stadium_data.json", "w")
f.write(stadiumJson)
f.close()

