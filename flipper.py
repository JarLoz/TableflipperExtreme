import sys
import json
from deckconverter import converter 
from deckconverter import scryfall
import argparse
import requests
import re

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--name', help='Name of the deck')
    parser.add_argument('--hires', help='Use high resolution versions of card images. Causes very large file sizes', action='store_true')
    parser.add_argument('--reprints', help='Use the latest reprints of the cards', action='store_true')
    parser.add_argument('--nocache', help='Do not use local cache for scryfall', action='store_true')
    parser.add_argument('input', help='Filename or URL of the decklist')
    args = parser.parse_args()

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
        scryfall.bustCache()

    decklist = getDecklist(args.input)

    print('Processing decklist')
    ttsJson = converter.convertDecklistToJSON(decklist, deckName, hires, reprint)

    if (args.nocache == False):
        scryfall.dumpCacheToFile()

    with open(deckName+'.json', 'w',encoding='utf8') as outfile:
        json.dump(ttsJson, outfile, indent=2)
    print('All done')

def getDecklist(inputStr):
    """
    Finds the decklist list from a given input string. If the string is an URL to deckbox.org or tappedout.net,
    the function will try to download the decklist. Otherwise, the string is interpreted to be a filename.
    """
    if (re.match('http', inputStr)):
        print('Generating from URL ' + inputStr)
        if re.match('https://deckbox.org', inputStr):
            # Deckbox.org URL
            response = requests.get(inputStr+'/export')
            deckboxHtml = response.text
            bodyStart = re.search('<body>', deckboxHtml).end()
            bodyEnd = re.search('</body>', deckboxHtml).start()
            deckboxHtmlBody = deckboxHtml[bodyStart:bodyEnd]
            decklist = deckboxHtmlBody.replace('<p>','').replace('</p>','').replace('<strong>','').replace('</strong>','').split('<br/>')
        elif re.match('http://tappedout.net', inputStr):
            #Tappedout URL
            response = requests.get(inputStr+'?fmt=txt')
            decklist = response.text.split('\n')
        else:
            print('Input URL must be to either to https://deckbox.org or http://tappedout.net.')
        del response
        return decklist
    else:
        print('Generating from file ' +  inputStr)
        with open(inputStr,encoding='utf8') as decklistfile:
            decklist = decklistfile.readlines()
        return decklist

if __name__ == '__main__':
    sys.exit(main())
