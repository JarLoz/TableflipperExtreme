import sys
import json
from deckconverter import converter 
import argparse
import requests
import re

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f','--file', help='Filename of the decklist, in tappedout.net txt format')
    group.add_argument('-u','--url', help='URL to tappedout.net decklist')
    parser.add_argument('-n','--name', help='Name of the deck')
    parser.add_argument('--hires', help='Use high resolution versions of card images. Causes very large file sizes', action='store_true')
    parser.add_argument('--reprints', help='Use the latest reprints of the cards', action='store_true')
    parser.add_argument('--nocache', help='Do not use local cache for scryfall', action='store_true')
    args = parser.parse_args()


    if (args.file == None and args.url == None):
        print('Need some input, either from -f or -u. See --help.')
        return

    deckName = 'Deck'
    if (args.name):
        deckName = args.name

    hires = False
    if (args.hires):
        hires = True

    reprint = False
    if (args.reprints):
        reprint = True

    if (args.nocache):
        converter.bustCache()

    if (args.file):
        print('Generating from file ' +  args.file)
        with open(args.file,encoding='utf8') as decklistfile:
            decklist = decklistfile.readlines()
    elif (args.url):
        print('Generating from URL ' + args.url)
        if re.match('https://deckbox.org', args.url):
            # Deckbox.org URL
            response = requests.get(args.url+'/export')
            deckboxHtml = response.text
            bodyStart = re.search('<body>', deckboxHtml).end()
            bodyEnd = re.search('</body>', deckboxHtml).start()
            deckboxHtmlBody = deckboxHtml[bodyStart:bodyEnd]
            decklist = deckboxHtmlBody.replace('<p>','').replace('</p>','').replace('<strong>','').replace('</strong>','').split('<br/>')
        elif re.match('http://tappedout.net', args.url):
            #Tappedout URL
            response = requests.get(args.url+'?fmt=txt')
            decklist = response.text.split('\n')
        del response

    print('Processing decklist')
    ttsJson = generateJsonFromDecklist(decklist, deckName, hires, reprint)

    if (args.nocache == False):
        converter.dumpCacheToFile()

    with open(deckName+'.json', 'w',encoding='utf8') as outfile:
        json.dump(ttsJson, outfile, indent=2)
    print('All done')

def generateJsonFromDecklist(decklist, deckName, hires, reprint):
    processedDecklist,processedDecklistSideboard,processedExtraCards = converter.processDecklist(decklist, reprint)

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
    print('Downloading card images')
    converter.downloadCardImages(processedDecklist)
    print('Creating deck images')
    deckImageNames = converter.createDeckImages(processedDecklist, deckName, hires, doubleSided)
    print('Creating deck object')
    return converter.createDeckObject(processedDecklist, deckName, deckImageNames, posX)

if __name__ == '__main__':
    sys.exit(main())
