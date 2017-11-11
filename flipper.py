import sys
import json
from deckconverter import converter 
import argparse
import requests

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f','--file', help='Filename of the decklist, in tappedout.net txt format')
    group.add_argument('-u','--url', help='URL to tappedout.net decklist')
    group.add_argument('-j','--json', help='JSON file containing processed card list. Good for tokens.')
    parser.add_argument('-n','--name', help='Name of the deck')
    parser.add_argument('--hires', help='Use high resolution versions of card images. Causes very large file sizes', action='store_true')
    args = parser.parse_args()


    if (args.file == None and args.url == None and args.json == None):
        print('Need some input, either from -f, -u, or -j. See --help.')
        return

    deckName = 'Deck'
    if (args.name):
        deckName = args.name
    hires = False
    if (args.hires):
        hires = True

    if (args.file):
        print('Generating from file ' +  args.file)
        with open(args.file,encoding='utf8') as decklistfile:
            decklist = decklistfile.readlines()
        ttsJson = generateJsonFromDecklist(decklist, deckName, hires)
    elif (args.url):
        print('Generating from URL ' + args.url)
        response = requests.get(args.url+'?fmt=txt')
        decklist = response.text.split('\n')
        del response
        ttsJson = generateJsonFromDecklist(decklist, deckName, hires)
    elif (args.json):
        with open(args.json, encoding='utf8') as inFile:
            processedDecklist = json.load(inFile)
        ttsJson = generateJsonFromProcessedDecklist(processedDecklist, deckName, hires)


    with open(deckName+'.json', 'w',encoding='utf8') as outfile:
        json.dump(ttsJson, outfile, indent=2)
    print('All done')

def generateJsonFromDecklist(decklist, deckName, hires):
    print('Processing decklist')
    processedDecklist,processedDecklistSideboard,processedExtraCards = converter.processDecklist(decklist)

    deckObjects = []
    posX = 0.0
    deckObjects.append(generateDeckObjectFromProcessedDecklist(processedDecklist, deckName, posX, hires))
    posX += 4.0
    if (processedDecklistSideboard):
        deckObjects.append(generateDeckObjectFromProcessedDecklist(processedDecklistSideboard, deckName+'-sideboard', posX, hires))
        posX += 4.0
    if (processedExtraCards):
        deckObjects.append(generateDeckObjectFromProcessedDecklist(processedExtraCards, deckName+'-extra', posX, hires))

    return {'ObjectStates':deckObjects}

def generateJsonFromProcessedDecklist(processedDecklist, deckName, hires):
    deckObject = generateDeckObjectFromProcessedDecklist(processedDecklist, deckName, 0.0, hires)
    return {'ObjectStates':[deckObject]}

def generateDeckObjectFromProcessedDecklist(processedDecklist, deckName, posX, hires):
    print('Downloading card images')
    converter.downloadCardImages(processedDecklist)
    print('Creating deck images')
    deckImageNames = converter.createDeckImages(processedDecklist, deckName, hires)
    print('Creating deck object')
    return converter.createDeckObject(processedDecklist, deckName, deckImageNames, posX)

if __name__ == '__main__':
    sys.exit(main())
