import sys
import json
import requests
import shutil
import os
import subprocess

def processDecklist(decklist):
    processedDecklist = []
    processedDecklistSideboard = []
    processedExtraCards = []
    sideboard = False
    for line in decklist:
        # Checking if we are in sideboard territory.
        if line.strip().lower() == 'sideboard:':
            print('Switching to sideboard')
            sideboard = True
            continue;
        cardName, count = parseDecklistLine(line)
        if cardName == None:
            print('Skipping empty line')
            continue
        processedCard, extra = generateProcessedCardEntry(cardName);
        if processedCard != None:
            print('Found card ' + processedCard['name'])
            for i in range(count):
                if sideboard:
                    processedDecklistSideboard.append(processedCard)
                else:
                    processedDecklist.append(processedCard)
            processedExtraCards += extra
        else:
            print("Couldn't find card, line: " +  line)

    return (processedDecklist, processedDecklistSideboard, processedExtraCards)

def parseDecklistLine(line):
    splitLine = line.strip().split()
    if len(splitLine) <= 1:
        return (None, None)
    count = int(splitLine[0])
    cardName = ' '.join(splitLine[1:])
    return (cardName, count)

def generateProcessedCardEntry(cardName, reprint=False):
    # Let's handle basics separately, since they are printed in every damn set. Guru lands are best.
    if cardName == 'Forest':
        return ({'name':'Forest','set':'PGRU','number':'1'},[])
    elif cardName == 'Island':
        return ({'name':'Island','set':'PGRU','number':'2'},[])
    elif cardName == 'Mountain':
        return ({'name':'Mountain','set':'PGRU','number':'3'},[])
    elif cardName == 'Plains':
        return ({'name':'Plains','set':'PGRU','number':'4'},[])
    elif cardName == 'Swamp':
        return ({'name':'Mountain','set':'PGRU','number':'5'},[])

    if reprint:
        response = requests.get('https://api.scryfall.com/cards/search',{'q':'!"'+cardName+'"'}).json()
    else:
        response = requests.get('https://api.scryfall.com/cards/search',{'q':'!"'+cardName+'" not:reprint'}).json()


    if response['object'] == 'error':
        print("Scryfall couldn't find "+cardName+"!")
        return (None,None)

    cardInfo = response['data'][0]
    cardEntry = {}

    cardEntry['name'] = cardName
    cardEntry['set'] = cardInfo['set']
    cardEntry['number'] = cardInfo['collector_number']

    if cardInfo['layout'] == 'transform':
        frontFaceUrl = ""
        backFaceUrl = ""
        for cardFace in cardInfo['card_faces']:
            imageUrl = cardFace['image_uris']['large']
            if (cardFace['name'] == cardName):
                frontFaceUrl = imageUrl[:imageUrl.find('?')]
            else:
                backFaceUrl = imageUrl[:imageUrl.find('?')]
        cardEntry['image_url'] = frontFaceUrl
        extraCardEntry = {}
        extraCardEntry['name'] = cardInfo['name']
        extraCardEntry['transform'] = True
        extraCardEntry['set'] = cardInfo['set']
        extraCardEntry['number'] = cardInfo['collector_number']
        extraCardEntry['image_urls'] = [frontFaceUrl, backFaceUrl]
        return (cardEntry, [extraCardEntry])

    return (cardEntry, [])

def downloadCardImages(processedDecklist):
    for processedCard in processedDecklist:
        downloadCardImage(processedCard)

def downloadCardImage(processedCard):
    os.makedirs('imageCache', exist_ok=True)
    if 'image_url' in processedCard.keys() :
        imageUrls = [processedCard['image_url']]
    elif 'image_urls' in processedCard.keys() :
        imageUrls = processedCard['image_urls']
    else:
        imageUrls = ['https://img.scryfall.com/cards/large/en/' + processedCard['set'].lower() + '/' + processedCard['number'] + '.jpg']

    for imageUrl in imageUrls:
        downloadCardImageByUrl(imageUrl)

def generateFilenameFromUrl(url):
    reverse = url[::-1]
    filename = reverse[:reverse.find('/')][::-1]
    reverse = reverse[reverse.find('/')+1:]
    setname = reverse[:reverse.find('/')][::-1]
    return 'imageCache/'+ setname + '_' + filename

def downloadCardImageByUrl(url):
    imageName = generateFilenameFromUrl(url)
    if os.path.isfile(imageName):
        print('Image found for ' + imageName)
        return
    print('Downloading ' + imageName)
    response = requests.get(url, stream=True)
    with open(imageName, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return

def generateCardImageNames(processedCard):
    if 'image_url' in processedCard.keys():
        return [generateFilenameFromUrl(processedCard['image_url'])]
    elif 'image_urls' in processedCard.keys():
        imageNames = []
        for imageUrl in processedCard['image_urls']:
            imageNames.append(generateFilenameFromUrl(imageUrl))
        return imageNames
    return ['imageCache/' + processedCard['set'] + '_' + processedCard['number'] + '.jpg']

def createDeckImages(processedDecklist, deckName, hires, doubleSided):
    imageIndex = 0
    deckImageNames = []
    for i in range(0,len(processedDecklist),69) :
        chunk = processedDecklist[i:i+69]
        if doubleSided:
            frontSideImageNames = []
            backSideImageNames = []
            for card in chunk:
                imageNames = generateCardImageNames(card)
                frontSideImageNames.append(imageNames[0])
                backSideImageNames.append(imageNames[1])
            frontDeckImageName = deckName+'_front_image_'+str(imageIndex)+".jpg"
            backDeckImageName = deckName+'_back_image_'+str(imageIndex)+".jpg"
            deckImageNames.append([frontDeckImageName,backDeckImageName])
            callMontage(frontSideImageNames, frontDeckImageName, hires)
            callMontage(backSideImageNames, backDeckImageName, hires)
        else:
            imageNames = list(map(lambda card: generateCardImageNames(card)[0], chunk))
            deckImageName = deckName+'_image_'+str(imageIndex)+".jpg"
            deckImageNames.append([deckImageName])
            callMontage(imageNames, deckImageName, hires)
        imageIndex += 1
    return deckImageNames

def callMontage(imageNames, deckImageName, hires):
    if (hires):
        subprocess.call(['montage'] + imageNames + ['-geometry', '100%x100%+0+0', '-tile', '10x7', deckImageName])
    else:
        subprocess.call(['montage'] + imageNames + ['-geometry', '50%x50%+0+0', '-tile', '10x7', deckImageName])

def createDeckObject(processedDecklist, deckName, deckImageNames, posX):
    deckObject = {'Transform': {'posX':posX,'posY':1.0,'posZ':-0.0,'rotX':0,'rotY':180,'rotZ':180,'scaleX':1,'scaleY':1,'scaleZ':1},'Name': 'DeckCustom','Nickname':deckName}
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
    customDeck = {}
    customDeckIndex = 1
    for deckImageName in deckImageNames:
        if len(deckImageName) == 1:
            customDeck[str(customDeckIndex)] = {'NumWidth':10,'NumHeight':7,'FaceUrl':'<REPLACE WITH URL TO '+deckImageName[0]+'>','BackUrl':'http://i.imgur.com/P7qYTcI.png','UniqueBack':False}
        else:
            customDeck[str(customDeckIndex)] = {'NumWidth':10,'NumHeight':7,'FaceUrl':'<REPLACE WITH URL TO '+deckImageName[0]+'>','BackUrl':'<REPLACE WITH URL TO '+deckImageName[1]+'>','UniqueBack':True}
        customDeckIndex += 1
    deckObject['CustomDeck'] = customDeck
    return deckObject
