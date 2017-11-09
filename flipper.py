import sys
import json
import requests
import shutil
import os

allCards = json.load(open('json/AllSets.json'))
setList = json.load(open('json/SetList.json'))
setOrdered = sorted(setList, key=lambda s: s['releaseDate'])
setNames = list(map(lambda s: s['code'], setOrdered))
badSets = []

def main():
    decklist = open('decklist.txt').readlines()
    processedDecklist = []
    for line in decklist:
        splitLine = line.strip().split()
        if len(splitLine) <= 1:
            continue
        count = splitLine[0]
        cardName = ' '.join(splitLine[1:])
        processedCard = generateProcessedCardEntry(cardName);
        if processedCard != None:
            downloadCardImage(processedCard)

def generateProcessedCardEntry(cardName):
    # Let's handle basics separately, since they are printed in every damn set. Guru lands are best.
    if cardName == 'Forest':
        return {'name':'Forest','set':'PGRU','number':'1'}
    elif cardName == 'Island':
        return {'name':'Island','set':'PGRU','number':'2'}
    elif cardName == 'Mountain':
        return {'name':'Mountain','set':'PGRU','number':'3'}
    elif cardName == 'Plains':
        return {'name':'Plains','set':'PGRU','number':'4'}
    elif cardName == 'Swamp':
        return {'name':'Mountain','set':'PGRU','number':'5'}

    for setName in setNames:
        # Some sets just suck. Including promos.
        if setName in badSets or setName[0] == 'p':
            continue
        for cardInfo in allCards[setName]['cards']:
            if cardName.lower() == cardInfo['name'].lower():
                if 'mciNumber' in cardInfo.keys():
                    return {'name':cardName, 'set':setName, 'number':cardInfo['mciNumber']}
                elif 'number' in cardInfo.keys():
                    return {'name':cardName, 'set':setName, 'number':cardInfo['number']}
    return None

def downloadCardImage(processedCard):
    os.makedirs('imageCache', exist_ok=True)
    imageName = 'imageCache/' + processedCard['set'] + '_' + processedCard['number'] + '.jpg'
    if os.path.isfile(imageName):
        #No need to download images twice.
        return;
    print('Downloading card image' + processedCard['name'] + ' to ' + imageName)
    imageUrl = 'https://img.scryfall.com/cards/large/en/' + processedCard['set'].lower() + '/' + processedCard['number'] + '.jpg'
    response = requests.get(imageUrl, stream=True)
    with open(imageName, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

if __name__ == '__main__':
    sys.exit(main())
