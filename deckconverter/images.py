import os
import requests
import shutil
import subprocess
from . import queue

montagePath = None

def setMontagePath(path):
    global montagePath
    montagePath = path

def downloadCardImages(processedDecklist):
    """
    Downloads the individual card images for a given processed decklist.
    """
    imageNumber = 1
    imageCount = len(processedDecklist)
    for processedCard in processedDecklist:
        queue.sendMessage({'type':'message','text':'Downloading card ('+str(imageNumber)+'/'+str(imageCount)+')'})
        imageNumber += 1
        downloadCardImage(processedCard)

def downloadCardImage(processedCard):
    """
    Downloads the individual card image for a given processed card. To determine
    the download URL, first the image_url attribute is checked. If that is not available,
    the image_urls attribute is checked. Finally, the URL is constructed using
    the set and collectors number of the card.
    """
    os.makedirs('imageCache', exist_ok=True)
    if 'image_name' in processedCard.keys() :
        #Custom card, no need to do anything.
        return
    if 'image_url' in processedCard.keys() :
        imageUrls = [processedCard['image_url']]
    elif 'image_urls' in processedCard.keys() :
        imageUrls = processedCard['image_urls']
    else:
        imageUrls = ['https://img.scryfall.com/cards/large/en/' + processedCard['set'].lower() + '/' + processedCard['number'] + '.jpg']

    for imageUrl in imageUrls:
        downloadCardImageByUrl(imageUrl)

def generateFilenameFromUrl(url):
    """
    Transforms a card URL into a local filename in the format

    imageCache/setname_cardnumber.jpg.
    """
    reverse = url[::-1]
    filename = reverse[:reverse.find('/')][::-1]
    reverse = reverse[reverse.find('/')+1:]
    setname = reverse[:reverse.find('/')][::-1]
    return 'imageCache/'+ setname + '_' + filename
    return '_'.join(url.split('/')[1:])

def downloadCardImageByUrl(url):
    """
    Downloads the card image from a given URL. The function first checks
    if the card image is already available in imageCache, and only downloads
    if it is not.
    """
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
    """
    Transforms the processed card information into a local filename, similarly to
    the generateFilenameFromUrl() function.
    """
    if 'image_name' in processedCard.keys():
        return [processedCard['image_name']]
    elif 'image_url' in processedCard.keys():
        return [generateFilenameFromUrl(processedCard['image_url'])]
    elif 'image_urls' in processedCard.keys():
        imageNames = []
        for imageUrl in processedCard['image_urls']:
            imageNames.append(generateFilenameFromUrl(imageUrl))
        return imageNames
    return ['imageCache/' + processedCard['set'].lower() + '_' + processedCard['number'] + '.jpg']

def createDeckImages(processedDecklist, deckName, hires, doubleSided, output=''):
    """
    Creates the deck image sheets used by TTS from a given processed decklist. The generated images are of
    the format deckname_image_#_.jpg, where # is a running number. TTS has a limit of 69 cards per deck sheet,
    so a deck containing more than 69 cards will have to be spread between several sheets.
    If the deck is defined to be a double-sided deck, then two images are generated per sheet.
    """
    imageIndex = 0
    deckImageNames = []
    queue.sendMessage({'type':'message', 'text':'Generating images.'})
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
            callMontage(frontSideImageNames, frontDeckImageName, hires, output)
            callMontage(backSideImageNames, backDeckImageName, hires, output)
        else:
            imageNames = list(map(lambda card: generateCardImageNames(card)[0], chunk))
            deckImageName = deckName+'_image_'+str(imageIndex)+".jpg"
            deckImageNames.append([deckImageName])
            callMontage(imageNames, deckImageName, hires, output)
        imageIndex += 1
    return deckImageNames

def callMontage(imageNames, deckImageName, hires, output=''):
    """
    Calls the external montage tool from Imagemagick package to do the image composition.
    """
    global montagePath
    imagePath = os.path.join(output, deckImageName)
    if (hires):
        subprocess.call([montagePath] + imageNames + ['-geometry', '100%x100%+0+0', '-tile', '10x7', imagePath])
    else:
        subprocess.call([montagePath] + imageNames + ['-geometry', '50%x50%+0+0', '-tile', '10x7', imagePath])
