import sys
import json
import requests
import shutil
import os
import subprocess
import re

scryfallCache = None

def doRequest(url, params=None):
    global scryfallCache
    if scryfallCache == None:
        if os.path.isfile('scryfallCache.json'):
            with open('scryfallCache.json',encoding='utf8') as cacheFile:
                scryfallCache = json.load(cacheFile)
        else:
            scryfallCache = {}
    urlBuggered = url.replace('/','.').replace(':','.')
    if (params != None):
        paramsBuggered = params['q'].replace(' ','').replace(':','.').replace('"','').replace("'",'')
        cacheKey = urlBuggered+paramsBuggered
    else:
        cacheKey = urlBuggered

    if cacheKey in scryfallCache.keys():
        print ('Cache hit!')
        return scryfallCache[cacheKey]

    response = requests.get(url,params).json()
    if response['object'] != 'error':
        scryfallCache[cacheKey] = response

    return response

def dumpCacheToFile():
    global scryfallCache
    if len(scryfallCache) > 0:
        with open('scryfallCache.json', 'w',encoding='utf8') as outfile:
            json.dump(scryfallCache, outfile)
        print('Cache dumped')

def bustCache():
    global scryfallCache
    scryfallCache = {}

def processDecklist(decklist, reprint=False):
    processedDecklist = []
    processedDecklistSideboard = []
    processedFlipCards = []
    sideboard = False
    for line in decklist:
        # Checking if we are in sideboard territory.
        if line.strip().lower() == 'sideboard:':
            print('Switching to sideboard')
            sideboard = True
            continue;
        if re.match('https://scryfall.com', line.strip()):
            # It's a URL!
            url = 'https://api.' + line.strip()[8:].replace('card','cards')
            cardInfo = doRequest(url)
            if cardInfo['object'] == 'error':
                print("Scryfall couldn't find "+url+"!")
                print(cardInfo)
                continue
            count = 1
            processedCard, extra = generateProcessedCardEntryFromCardInfo(cardInfo)
        else:
            cardName, count = parseDecklistLine(line.strip())
            if cardName == None:
                print('Skipping empty line')
                continue
            processedCard, extra = generateProcessedCardEntry(cardName, reprint);
        if processedCard != None:
            print('Found card ' + processedCard['name'])
            for i in range(count):
                if sideboard:
                    processedDecklistSideboard.append(processedCard)
                else:
                    processedDecklist.append(processedCard)
            processedFlipCards += extra
        else:
            print("Couldn't find card, line: " +  line)

    return (processedDecklist, processedDecklistSideboard, processedFlipCards)

def parseDecklistLine(line):
    splitLine = line.split()
    if len(splitLine) <= 1:
        return (None, None)
    count = int(splitLine[0])
    cardName = ' '.join(splitLine[1:])
    return (cardName, count)

def generateProcessedCardEntry(cardName, reprint):
    # Let's handle basics separately, since they are printed in every damn set. Guru lands are best.
    if cardName == 'Forest':
        return ({'name':'Forest','set':'pgru','number':'1'},[])
    elif cardName == 'Island':
        return ({'name':'Island','set':'pgru','number':'2'},[])
    elif cardName == 'Mountain':
        return ({'name':'Mountain','set':'pgru','number':'3'},[])
    elif cardName == 'Plains':
        return ({'name':'Plains','set':'pgru','number':'4'},[])
    elif cardName == 'Swamp':
        return ({'name':'Mountain','set':'pgru','number':'5'},[])

    if reprint:
        response = doRequest('https://api.scryfall.com/cards/search',{'q':'!"'+cardName+'"'})
    else:
        response = doRequest('https://api.scryfall.com/cards/search',{'q':'!"'+cardName+'" not:reprint'})


    if response['object'] == 'error':
        print("Scryfall couldn't find "+cardName+"!")
        return (None,None)

    cardInfo = response['data'][0]
    return generateProcessedCardEntryFromCardInfo(cardInfo, cardName)

def generateProcessedCardEntryFromCardInfo(cardInfo, cardName=None):

    cardEntry = {}
    if cardName == None:
        cardName = cardInfo['name']

    cardEntry['name'] = cardName
    cardEntry['set'] = cardInfo['set']
    cardEntry['number'] = cardInfo['collector_number']

    if cardInfo['layout'] == 'transform':
        frontFaceUrl = ""
        backFaceUrl = ""
        for cardFace in cardInfo['card_faces']:
            imageUrl = cardFace['image_uris']['large']
            if (cardFace['name'] == cardName):
                frontFaceUrl = stripUselessNumbers(imageUrl)
            else:
                backFaceUrl = stripUselessNumbers(imageUrl)
        cardEntry['image_url'] = frontFaceUrl
        extraCardEntry = {}
        extraCardEntry['name'] = cardInfo['name']
        extraCardEntry['transform'] = True
        extraCardEntry['set'] = cardInfo['set']
        extraCardEntry['number'] = cardInfo['collector_number']
        extraCardEntry['image_urls'] = [frontFaceUrl, backFaceUrl]
        return (cardEntry, [extraCardEntry])
    elif cardInfo['layout'] == 'meld':
        #Goddamn meld cards god damn them all. No cool tricks here, just treat them as double-faced cards.
        frontFaceUrl = stripUselessNumbers(cardInfo['image_uris']['large'])
        cardEntry['image_url'] = frontFaceUrl
        extraCardUrl = ""
        for part in cardInfo['all_parts']:
            if re.match('b',part['uri'][::-1]):
                extraCardUrl = part['uri']
                break
        extraCardInfo = doRequest(extraCardUrl)
        backFaceUrl = stripUselessNumbers(extraCardInfo['image_uris']['large'])
        extraCardEntry = {}
        extraCardEntry['name'] = extraCardInfo['name']
        extraCardEntry['set'] = extraCardInfo['set']
        extraCardEntry['number'] = extraCardInfo['collector_number']
        extraCardEntry['image_urls'] = [frontFaceUrl, backFaceUrl]
        return (cardEntry, [extraCardEntry])

    return (cardEntry, [])

def stripUselessNumbers(url):
    return url[:url.find('?')]

def findTokenInfo(cardInfo):
    #TODO Finish this, and fetch tokens for cards.
    if 'oracle_text' in cardInfo.keys():
        createIndex = cardInfo['oracle_text'].lower().find('create')
        if createIndex > -1:
            tokenIndex = cardInfo['oracle_text'].find('token')
            tokenInfo = cardInfo['oracle_text'][createIndex+6:tokenIndex].split()
            name = None
            colors = ""
            power = None
            toughness = None
            for part in tokenInfo:
                if part == 'white':
                    colors += 'w'
                elif part == 'blue':
                    colors += 'u'
                elif part == 'black':
                    colors += 'b'
                elif part == 'red':
                    colors += 'r'
                elif part == 'green':
                    colors += 'g'
                elif re.search('/',part):
                    split = part.split()
                    power = split[0]
                    toughness = split[1]
                elif re.search('[A-Z]', part):
                    if name == None:
                        name = part
                    else:
                        name += " "
                        name += part


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
    return ['imageCache/' + processedCard['set'].lower() + '_' + processedCard['number'] + '.jpg']

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
