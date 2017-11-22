from . import processor
from . import images
from . import scryfall
from gimgurpython import ImgurClient

def convertDecklistToJSON(decklist, deckName, hires, reprint, nocache=False, imgur=None):
    """
    Converts a given decklist to the JSON format used by Tabletop Simulator, as well
    as generating the required images. The decklist is assumed to be a list of strings.
    """
    if (nocache):
        scryfall.bustCache()

    processedDecklist,processedDecklistSideboard,processedExtraCards = processor.processDecklist(decklist, reprint)

    if (nocache == False):
        scryfall.dumpCacheToFile()

    deckObjects = []
    posX = 0.0
    deckObjects.append(generateDeckObjectFromProcessedDecklist(processedDecklist, deckName, posX, hires, imgur=imgur))
    posX += 4.0
    if (processedDecklistSideboard):
        deckObjects.append(generateDeckObjectFromProcessedDecklist(processedDecklistSideboard, deckName+'-sideboard', posX, hires, imgur=imgur))
        posX += 4.0
    if (processedExtraCards):
        deckObjects.append(generateDeckObjectFromProcessedDecklist(processedExtraCards, deckName+'-extra', posX, hires, doubleSided=True, imgur=imgur))

    return {'ObjectStates':deckObjects}

def generateDeckObjectFromProcessedDecklist(processedDecklist, deckName, posX, hires, doubleSided=False, imgur=None):
    """
    Downloads the cards and creates the TTS deck object for a given processed decklist.
    """
    print('Downloading card images')
    images.downloadCardImages(processedDecklist)
    print('Creating deck images')
    deckImageNames = images.createDeckImages(processedDecklist, deckName, hires, doubleSided)
    print('Creating deck object')
    return createDeckObject(processedDecklist, deckName, deckImageNames, posX, imgur)

def createDeckObject(processedDecklist, deckName, deckImageNames, posX, imgur=None):
    """
    Creates a TTS deck object from a given processed decklist.
    """
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
        if int(str(cardId)[1:]) == 69:
            cardId += 31
    deckObject['ContainedObjects'] = containedObjects
    deckObject['DeckIDs'] = deckIds
    customDeck = {}
    customDeckIndex = 1
    for deckImageName in deckImageNames:

        faceUrl = getDeckUrl(deckImageName[0], imgur)

        uniqueBack = False
        if len(deckImageName) == 2:
            uniqueBack = True
            backUrl = getDeckUrl(deckImageName[1], imgur)
        else:
            backUrl = 'https://i.imgur.com/P7qYTcI.png'

        customDeck[str(customDeckIndex)] = {'NumWidth':10,'NumHeight':7,'FaceUrl':faceUrl,'BackUrl':backUrl,'UniqueBack':uniqueBack}
        customDeckIndex += 1
    deckObject['CustomDeck'] = customDeck
    return deckObject

def getDeckUrl(deckImage, imgur):
    if (imgur):
        return uploadToImgur(deckImage, imgur)
    else:
        return '<REPLACE WITH URL TO ' + deckImage + '>'

def uploadToImgur(deckImage, imgurInfo):
    print('Uploading file ' + deckImage + ' to Imgur!')
    client = ImgurClient(imgurInfo['client_id'], imgurInfo['client_secret'])
    with open(deckImage, 'rb') as imageFp:
        response = client.upload(imageFp)
    return response['link']

