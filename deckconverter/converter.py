from . import processor
from . import images
from . import scryfall
from . import queue
from gimgurpython import ImgurClient
import dropbox
import os

def convertDecklistToJSON(decklist, deckName, hires, reprint, nocache=False, imgurId=None, dropboxToken=None, output=''):
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
    deckObjects.append(generateDeckObjectFromProcessedDecklist(processedDecklist, deckName, posX, hires, imgurId=imgurId, dropboxToken=dropboxToken, output=output))
    posX += 4.0
    if (processedDecklistSideboard):
        deckObjects.append(generateDeckObjectFromProcessedDecklist(processedDecklistSideboard, deckName+'-sideboard', posX, hires, imgurId=imgurId, dropboxToken=dropboxToken, output=output))
        posX += 4.0
    if (processedExtraCards):
        deckObjects.append(generateDeckObjectFromProcessedDecklist(processedExtraCards, deckName+'-extra', posX, hires, doubleSided=True, imgurId=imgurId, dropboxToken=dropboxToken, output=output))

    return {'ObjectStates':deckObjects}

def generateDeckObjectFromProcessedDecklist(processedDecklist, deckName, posX, hires, doubleSided=False, imgurId=None, dropboxToken=None, output=''):
    """
    Downloads the cards and creates the TTS deck object for a given processed decklist.
    """
    print('Downloading card images')
    images.downloadCardImages(processedDecklist)
    print('Creating deck images')
    deckImageNames = images.createDeckImages(processedDecklist, deckName, hires, doubleSided, output)
    print('Creating deck object')
    deckObject = createDeckObject(processedDecklist, deckName, deckImageNames, posX, output, imgurId, dropboxToken)
    if imgurId or dropboxToken:
        print('Deleting local deck images')
        for deckImageName in deckImageNames:
            for imageName in deckImageName:
                imagePath = os.path.join(output,imageName)
                os.remove(imagePath)
    return deckObject


def createDeckObject(processedDecklist, deckName, deckImageNames, posX, output='', imgurId=None, dropboxToken=None):
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

        faceUrl = getDeckUrl(deckImageName[0], output, imgurId, dropboxToken)

        uniqueBack = False
        if len(deckImageName) == 2:
            uniqueBack = True
            backUrl = getDeckUrl(deckImageName[1], output, imgurId, dropboxToken)
        else:
            backUrl = 'https://i.imgur.com/P7qYTcI.png'

        customDeck[str(customDeckIndex)] = {'NumWidth':10,'NumHeight':7,'FaceUrl':faceUrl,'BackUrl':backUrl,'UniqueBack':uniqueBack}
        customDeckIndex += 1
    deckObject['CustomDeck'] = customDeck
    return deckObject

def getDeckUrl(deckImage, output, imgurId, dropboxToken):
    if (dropboxToken):
        return uploadToDropbox(deckImage, dropboxToken, output)
    if (imgurId):
        return uploadToImgur(deckImage, imgurId, output)
    return '<REPLACE WITH URL TO ' + deckImage + '>'

def uploadToImgur(deckImage, imgurId, output):
    imagePath = os.path.join(output, deckImage)
    print('Uploading file ' + deckImage + ' to Imgur!')
    queue.sendMessage({'type':'message', 'text':'Uploading file ' + deckImage + ' to Imgur!'})
    client = ImgurClient(imgurId, '')
    with open(imagePath, 'rb') as imageFp:
        response = client.upload(imageFp)
    return response['link']

def uploadToDropbox(deckImage, dropboxToken, output):
    imagePath = os.path.join(output, deckImage)
    print('Uploading file ' + deckImage + ' to Dropbox!')
    queue.sendMessage({'type':'message', 'text':'Uploading file ' + deckImage + ' to Dropbox!'})
    dbx = dropbox.Dropbox(dropboxToken)
    with open(imagePath, 'rb') as imageFp:
        data = imageFp.read()
    dropboxPath = '/'+deckImage
    dbx.files_upload(data, dropboxPath)
    share = dbx.sharing_create_shared_link(dropboxPath)
    return share.url.replace('dl=0','raw=1')
