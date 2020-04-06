import re
from . import scryfall
from . import queue
import random

basics = {
        'guru':{
            'forest': {'name':'Forest','set':'pgru','number':'1'},
            'island': {'name':'Island','set':'pgru','number':'2'},
            'mountain': {'name':'Mountain','set':'pgru','number':'3'},
            'plains': {'name':'Plains','set':'pgru','number':'4'},
            'swamp': {'name':'Swamp','set':'pgru','number':'5'}
            },
        'unstable':{
            'forest': {'name':'Forest','set':'ust','number':'216'},
            'island': {'name':'Island','set':'ust','number':'213'},
            'mountain': {'name':'Mountain','set':'ust','number':'215'},
            'plains': {'name':'Plains','set':'ust','number':'212'},
            'swamp': {'name':'Swamp','set':'ust','number':'214'}
            },
        'alpha':{
            'forest': {'name':'Forest','set':'lea','number':'294'},
            'island': {'name':'Island','set':'lea','number':'288'},
            'mountain': {'name':'Mountain','set':'lea','number':'292'},
            'plains': {'name':'Plains','set':'lea','number':'286'},
            'swamp': {'name':'Swamp','set':'lea','number':'290'}
            },
        'core':{
            'forest': {'name':'Forest','set':'10e','number':'381'},
            'island': {'name':'Island','set':'10e','number':'369'},
            'mountain': {'name':'Mountain','set':'10e','number':'376'},
            'plains': {'name':'Plains','set':'10e','number':'365'},
            'swamp': {'name':'Swamp','set':'10e','number':'372'}
            },
        'guay':{
            'forest': {'name':'Forest','set':'c16','number':'349'},
            'island': {'name':'Island','set':'c16','number':'340'},
            'mountain': {'name':'Mountain','set':'c16','number':'346'},
            'plains': {'name':'Plains','set':'c16','number':'337'},
            'swamp': {'name':'Swamp','set':'c16','number':'343'}
            },
        'unsanctioned':{
            'forest': {'name': 'Forest','set':'und','number':'96'},
            'island': {'name': 'Island','set':'und','number':'90'},
            'mountain': {'name': 'Mountain','set':'und','number':'94'},
            'plains': {'name': 'Plains','set':'und','number':'88'},
            'swamp': {'name': 'Swamp','set':'und','number':'92'}
            }
        }
def processDecklist(decklist, reprint=False, basicSet=None):
    """
    Processes a given decklist into a "processed decklist" form. This processed form is a list of maps that detail the
    name, set and collector's number of a card, as well as optionally the image url(s) of the card.
    """
    processedDecklist = []
    processedDecklistSideboard = []
    processedFlipCards = []
    sideboard = False
    lineNumber = 1
    lineCount = len(decklist)
    for line in decklist:
        if queue.flipperQueue:
            queue.flipperQueue.put({'type':'message','text':'Processing line ('+str(lineNumber)+'/'+str(lineCount)+')'})
        lineNumber += 1
        # Checking if we are in sideboard territory.
        if line.strip().lower() == 'sideboard:':
            print('Switching to sideboard')
            sideboard = True
            continue;
        cardName, count = parseDecklistLine(line.strip())
        if cardName == None:
            print('Skipping empty line')
            continue

        if re.match('https://scryfall.com', cardName):
            # It's a URL!
            url = 'https://api.' + cardName[8:].replace('card','cards')
            cardInfo = scryfall.doRequest(url)
            if cardInfo['object'] == 'error':
                print("Scryfall couldn't find "+url+"!")
                print(cardInfo)
                continue
            processedCard, extra = generateProcessedCardEntryFromCardInfo(cardInfo)
        elif re.search('(\.jpg|\.png)$', cardName):
            # Custom card!
            name = ''.join(cardName.split('.')[:-1])
            imageName = 'imageCache/' + cardName.strip()
            processedCard = {'name':name, 'set':'custom', 'number':'1', 'image_name':imageName}
            extra = []
        else:
            # It's just a card name!
            processedCard, extra = generateProcessedCardEntry(cardName, reprint, basicSet);

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
    """
    Parses the relevant information from a decklist line.
    """
    splitLine = line.split()
    if len(splitLine) < 1:
        return (None, None)
    if (re.match('\d+$',splitLine[0])):
        # A digit means a count. I hope.
        count = int(splitLine[0])
        cardName = ' '.join(splitLine[1:])
    else:
        # No digit, assuming count of one.
        count = 1
        cardName = line
    return (cardName, count)

def generateProcessedCardEntryFromCardInfo(cardInfo, cardName=None):
    """
    Generates the processed card entry from card information downloaded from scryfall API. Returns a tuple
    consisting of the actual card information, as well as an array possibly containing additional card
    definitions, such as double-sided cards.
    """
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
        extraCardInfo = scryfall.doRequest(extraCardUrl)
        backFaceUrl = stripUselessNumbers(extraCardInfo['image_uris']['large'])
        extraCardEntry = {}
        extraCardEntry['name'] = extraCardInfo['name']
        extraCardEntry['set'] = extraCardInfo['set']
        extraCardEntry['number'] = extraCardInfo['collector_number']
        extraCardEntry['image_urls'] = [frontFaceUrl, backFaceUrl]
        return (cardEntry, [extraCardEntry])

    cardEntry['image_url'] = stripUselessNumbers(cardInfo['image_uris']['large'])
    return (cardEntry, [])

def stripUselessNumbers(url):
    """
    Scryfall API has a cryptic numeric parameter appended to image URLs. We strip this away because
    it would complicate things.
    """
    return url[:url.find('?')]

def generateProcessedCardEntry(cardName, reprint, basicSet=None):
    """
    Generates a processed card entry from a given cardname. The function will do a lookup to
    scryfall api to find the card information, and then pass it on to generateProcessedCardEntryFromCardInfo().

    If the reprint parameter is set to True, it will find the most relevant reprint given by Scryfall.
    Otherwise, we'll search for the first printing.
    """
    # Let's handle basics separately, since they are printed in every damn set. Guru lands are best.
    global basics
    set_ = ''
    number_ = ''
    if cardName.lower() in ['forest','island','mountain','plains','swamp']:
        if basicSet:
            set_ = f"set:{basics[basicSet][cardName.lower()]['set']}"
            number_ = f"number:{basics[basicSet][cardName.lower()]['number']}"
        else:
            set_ = f"set:{basics['guru'][cardName.lower()]['set']}"
            number_ = f"number:{basics['guru'][cardName.lower()]['number']}"

    if reprint:
        response = scryfall.doRequest('https://api.scryfall.com/cards/search',{'q':'!"'+cardName+'" ' + set_ + ' ' + number_})
    else:
        response = scryfall.doRequest('https://api.scryfall.com/cards/search',{'q':'!"'+cardName+'" ' + set_ + ' ' + number_})


    if response['object'] == 'error':
        print("Scryfall couldn't find "+cardName+"!")
        return (None,None)

    cardInfo = response['data'][0]
    return generateProcessedCardEntryFromCardInfo(cardInfo, cardName)

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

def generateDraftPackLists(setName, packCount):
    mythics = []
    rares = []
    uncommons = []
    commons = []
    hasMore = True
    nextPage = None
    while hasMore:
        response = scryfall.doRequest()
        if nextPage:
            response = scryfall.doRequest(nextPage)
        else:
            response = scryfall.doRequest('https://api.scryfall.com/cards/search',{'q':'set:'+setName, 'order':'rarity'})
        hasMore = response['has_more']
        if hasMore:
            nextPage = response['next_page']
        for cardInfo in response['data']:
            cardEntry = generateProcessedCardEntryFromCardInfo(cardInfo)[0]
            rarity = cardInfo['rarity']
            if rarity == 'mythic':
                mythics.append(cardEntry)
            elif rarity == 'rare':
                rares.append(cardEntry)
            elif rarity == 'uncommon':
                uncommons.append(cardEntry)
            elif rarity == 'common':
                commons.append(cardEntry)

    packIndex = 0
    packs = []
    while packIndex < packCount:
        random.shuffle(commons)
        random.shuffle(uncommons)
        random.shuffle(rares)
        random.shuffle(mythics)
        pack = commons[:10]
        pack =+ uncommons[:3]
        if random.random() <= 1/8: #one in eight packs contains a mythic
            pack.append(mythics[0])
        else:
            pack.append(rares[0])
        packs.append(pack)
        packIndex = packIndex + 1
    
    return packs


