import sys
import json
import requests
import shutil
import os
import subprocess

def processDecklist(decklist):
    # Ensure we have the source data available.
    os.makedirs('json', exist_ok=True)
    if os.path.isfile('json/SetList.json') == False:
        print('SetList.json missing, downloading')
        response = requests.get('https://mtgjson.com/json/SetList.json')
        with open('json/SetList.json', 'w', encoding='utf8') as outFile:
            outFile.write(response.text)
        del response
    else:
        print('SetList.json found')

    if os.path.isfile('json/AllSets.json') == False:
        print('AllSets.json missing, downloading')
        response = requests.get('https://mtgjson.com/json/AllSets.json')
        with open('json/AllSets.json', 'w', encoding='utf8') as outFile:
            outFile.write(response.text)
        del response
    else:
        print('AllSets.json found')

    with open('json/AllSets.json', encoding="utf8") as inFile:
        allCards = json.load(inFile)
    with open('json/SetList.json', encoding="utf8") as inFile:
        setList = json.load(inFile)
    # Sort sets based on release date, this way we'll get the oldest sets first!
    setOrdered = sorted(setList, key=lambda s: s['releaseDate'])
    setNames = list(map(lambda s: s['code'], setOrdered))

    processedDecklist = []
    for line in decklist:
        splitLine = line.strip().split()
        if len(splitLine) <= 1:
            print('Skipping empty line')
            continue
        count = int(splitLine[0])
        cardName = ' '.join(splitLine[1:])
        processedCard = generateProcessedCardEntry(cardName, setNames, allCards);
        if processedCard != None:
            print('Found card ' + processedCard['name'])
            for i in range(count):
                processedDecklist.append(processedCard)
        else:
            print("Couldn't find card, line: " +  line)
    return processedDecklist

def generateProcessedCardEntry(cardName, setNames, allCards, badSets = []):
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
        # Some sets just suck. Including promos. Also this hack sucks.
        if setName in badSets or setName[0] == 'p':
            continue
        for cardInfo in allCards[setName]['cards']:
            if cardName.lower() == cardInfo['name'].lower():
                if 'number' in cardInfo.keys():
                    return {'name':cardName, 'set':setName, 'number':cardInfo['number']}
                elif 'mciNumber' in cardInfo.keys():
                    return {'name':cardName, 'set':setName, 'number':cardInfo['mciNumber']}
                else:
                    return None
    return None

def downloadCardImages(processedDecklist):
    for processedCard in processedDecklist:
        downloadCardImage(processedCard)

def downloadCardImage(processedCard):
    os.makedirs('imageCache', exist_ok=True)
    imageName = generateCardImageName(processedCard)
    if os.path.isfile(imageName):
        # No need to download images twice. Shrewd dudes can make cool MS PAINT alters like this wooo
        print('Image found for ' + processedCard['name'])
        return;
    print('Downloading card ' + processedCard['name'] + ' image to ' + imageName)
    imageUrl = 'https://img.scryfall.com/cards/large/en/' + processedCard['set'].lower() + '/' + processedCard['number'] + '.jpg'
    response = requests.get(imageUrl, stream=True)
    with open(imageName, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def generateCardImageName(processedCard):
    return 'imageCache/' + processedCard['set'] + '_' + processedCard['number'] + '.jpg'

def createDeckImages(processedDecklist):
    imageIndex = 0
    deckImageNames = []
    for i in range(0,len(processedDecklist),69) :
        chunk = processedDecklist[i:i+69]
        imageNames = list(map(lambda card: generateCardImageName(card), chunk))
        deckImageName = "deckimage-"+str(imageIndex)+".jpg"
        deckImageNames.append(deckImageName)
        subprocess.call(['montage'] + imageNames + ['-geometry', '50%x50%+0+0', '-tile', '10x7', deckImageName])
        imageIndex += 1
    return deckImageNames

def createTTSJSON(processedDecklist, deckImageNames):
    ttsJson = {'ObjectStates':[]}
    deckObject = {'Transform': {'posX':-0.0,'posY':'1.0','posZ':-0.0,'rotX':0,'rotY':180,'rotZ':180,'scaleX':1,'scaleY':1,'scaleZ':1},'Name': 'DeckCustom','Nickname':'COOLDECK'}
    containedObjects = []
    deckIds = []
    cardId = 100
    for card in processedDecklist:
        cardObject = {'Name':'Card','Nickname':card['name'],'CardID':cardId}
        cardObject['Transform'] = {'posX':2.5,'posY':2.5,'posZ':3.5,'rotX':0,'rotY':180,'rotZ':180,'scaleX':1,'scaleY':1,'scaleZ':1}
        containedObjects.append(cardObject)
        deckIds.append(cardId)
        cardId += 1
        if cardId == 169:
            cardId = 200
    deckObject['ContainedObjects'] = containedObjects
    deckObject['DeckIDs'] = deckIds
    #TODO calculate dis shit
    deckObject['CustomDeck'] = {
            "1":{'NumWidth':10,'NumHeight':7,'FaceUrl':'file:///home/jarloz/Coolstuff/TableflipperExtreme/deckimage-0.jpg','BackUrl':'http://i.imgur.com/P7qYTcI.png'},
            "2":{'NumWidth':10,'NumHeight':7,'FaceUrl':'file:///home/jarloz/Coolstuff/TableflipperExtreme/deckimage-1.jpg','BackUrl':'http://i.imgur.com/P7qYTcI.png'}}
    ttsJson['ObjectStates'].append(deckObject)

    return ttsJson
