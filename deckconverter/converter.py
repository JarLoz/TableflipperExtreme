from . import processor
from . import images

def convertDecklistToJSON(decklist, deckName, hires, reprint):
    """
    Converts a given decklist to the JSON format used by Tabletop Simulator, as well
    as generating the required images. The decklist is assumed to be a list of strings.
    """
    processedDecklist,processedDecklistSideboard,processedExtraCards = processor.processDecklist(decklist, reprint)

    deckObjects = []
    posX = 0.0
    deckObjects.append(generateDeckObjectFromProcessedDecklist(processedDecklist, deckName, posX, hires))
    posX += 4.0
    if (processedDecklistSideboard):
        deckObjects.append(generateDeckObjectFromProcessedDecklist(processedDecklistSideboard, deckName+'-sideboard', posX, hires))
        posX += 4.0
    if (processedExtraCards):
        deckObjects.append(generateDeckObjectFromProcessedDecklist(processedExtraCards, deckName+'-extra', posX, hires, doubleSided=True))

    return {'ObjectStates':deckObjects}

def generateDeckObjectFromProcessedDecklist(processedDecklist, deckName, posX, hires, doubleSided=False):
    """
    Downloads the cards and creates the TTS deck object for a given processed decklist.
    """
    print('Downloading card images')
    images.downloadCardImages(processedDecklist)
    print('Creating deck images')
    deckImageNames = images.createDeckImages(processedDecklist, deckName, hires, doubleSided)
    print('Creating deck object')
    return createDeckObject(processedDecklist, deckName, deckImageNames, posX)

def createDeckObject(processedDecklist, deckName, deckImageNames, posX):
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
