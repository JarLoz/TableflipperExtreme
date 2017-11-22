import sys
import json
from deckconverter import converter 
from deckconverter import scryfall
from deckconverter import queue
import argparse
import requests
import re
import os

def initApp():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

def main():
    initApp()
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--name', help='Name of the deck')
    parser.add_argument('-o','--output', help='Output folder for the deck files')
    parser.add_argument('--hires', help='Use high resolution versions of card images. Causes very large file sizes', action='store_true')
    parser.add_argument('--reprints', help='Use the latest reprints of the cards', action='store_true')
    parser.add_argument('--nocache', help='Do not use local cache for scryfall', action='store_true')
    parser.add_argument('--imgur', help='Imgur integration. Requires imgurInfo.json', action='store_true')
    parser.add_argument('input', help='Filename or URL of the decklist')
    args = parser.parse_args()

    deckName = 'Deck'
    if (args.name):
        deckName = args.name

    hires = args.hires
    reprint = args.reprints
    nocache = args.nocache
    imgur = args.imgur
    output = args.output
    if output == None:
        output = ''
    elif not os.path.isdir(output):
        print('Output path not valid! Path: '+output)
        return

    generate(args.input, deckName, hires, reprint, nocache, imgur, output)

def generate(inputStr, deckName, hires=False, reprint=False, nocache=False, imgur=False, output=''):
    print('Processing decklist')
    try:
        imgurInfo = None
        if (imgur):
            if (os.path.isfile('imgurInfo.json') == False):
                print('imgurInfo.json missing!')
                queue.sendMessage({'type':'error', 'text':'imgurInfo.json missing!'})
                return
            with open('imgurInfo.json', encoding='utf8') as imgurInfoFile:
                imgurInfo = json.load(imgurInfoFile)
        decklist = getDecklist(inputStr)
        ttsJson = converter.convertDecklistToJSON(decklist, deckName, hires, reprint, nocache, imgurInfo, output)
        ttsJsonFilename = os.path.join(output, deckName+'.json')
        with open(ttsJsonFilename, 'w',encoding='utf8') as outfile:
            json.dump(ttsJson, outfile, indent=2)
        queue.sendMessage({'type':'done'})
        print('All done')
    except FileNotFoundError:
        print('File ' + inputStr + ' not found!')
        queue.sendMessage({'type':'error', 'text':'File '+inputStr+' not found!'})
    except:
        print('Error!')
        queue.sendMessage({'type':'error', 'text':'Error!'})


def getDecklist(inputStr):
    """
    Finds the decklist list from a given input string. If the string is an URL to deckbox.org or tappedout.net,
    the function will try to download the decklist. Otherwise, the string is interpreted to be a filename.
    """
    if re.match('http', inputStr):
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
