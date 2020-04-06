import sys
import traceback
import json
from deckconverter import converter 
from deckconverter import scryfall
from deckconverter import queue
from deckconverter import images
import argparse
import requests
import re
import os
import subprocess
from gimgurpython import ImgurClient
from gimgurpython.helpers.error import ImgurClientError
import dropbox
from time import gmtime, strftime

def initApp():
    if getattr(sys, 'frozen', False) :
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

def main():
    initApp()
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--name', help='Name of the deck')
    parser.add_argument('-o','--output', help='Output folder for the deck files')
    parser.add_argument('--hires', help='Use high resolution versions of card images. Causes very large file sizes', action='store_true')
    parser.add_argument('--reprints', help='Use the latest reprints of the cards', action='store_true')
    parser.add_argument('--nocache', help='Do not use local cache for scryfall', action='store_true')
    parser.add_argument('--imgur', help="Imgur client ID for Imgur integration. See README.md for details. Doesn't work with --hires.")
    parser.add_argument('--dropbox', help='Dropbox oAuth2 token for Dropbox integration.')
    parser.add_argument('--basic', help='Which basics to use. Allowed values: guru, unstable, alpha, core, guay')
    parser.add_argument('input', help='Filename or URL of the decklist')
    args = parser.parse_args()

    deckName = 'Deck'
    if (args.name):
        deckName = args.name

    hires = args.hires
    reprint = args.reprints
    nocache = args.nocache
    imgur = args.imgur
    dropbox = args.dropbox
    output = args.output
    if output == None:
        output = ''
    elif not os.path.isdir(output):
        print('Output path not valid! Path: '+output)
        return
    basicSet = args.basic
    if basicSet != None and not basicSet in ['guru', 'unstable', 'alpha', 'core', 'guay', 'unsanctioned']:
        print('--basic must be one of the following values: guru, unstable, alpha, core, guay, unsanctioned')
        return

    generate(args.input, deckName, hires, reprint, nocache, imgur, dropbox, output, basicSet)

def generateDraft(setName, packCount, hires=False, imgurId=None, dropboxToken=None, output=''):
    try: 
        if not checkIntegrations(hires, imgurId, dropboxToken):
            return

        ttsJson = converter.convertSetToDraftJSON(setname, packCount, hires, imgurId, dropboxToken, output)
        ttsJsonFilename = os.path.join(output, setName+'-draft-'+strftime("%Y%m%d%H%M%S", gmtime())+'.json')
        with open(ttsJsonFilename, 'w',encoding='utf8') as outfile:
            json.dump(ttsJson, outfile, indent=2)
        queue.sendMessage({'type':'done'})
        print('All done')
    except:
        # Handle random uncaught exceptions "gracefully"
        errorMessage = 'Error: ' + sys.exc_info()[0].__name__
        queue.sendMessage({'type':'error', 'text':errorMessage})
        print(errorMessage)
        traceback.print_tb(sys.exec_info()[2])

def generate(inputStr, deckName, hires=False, reprint=False, nocache=False, imgurId=None, dropboxToken=None,output='',basicSet=None):

    try: 
        if not checkIntegrations(hires, imgurId, dropboxToken):
            return

        decklist = getDecklist(inputStr)
        if decklist == None:
            return

        print('Processing decklist')
        ttsJson = converter.convertDecklistToJSON(decklist, deckName, hires, reprint, nocache, imgurId, dropboxToken, output, basicSet)
        ttsJsonFilename = os.path.join(output, deckName+'.json')
        with open(ttsJsonFilename, 'w',encoding='utf8') as outfile:
            json.dump(ttsJson, outfile, indent=2)
        queue.sendMessage({'type':'done'})
        print('All done')
    except:
        # Handle random uncaught exceptions "gracefully"
        errorMessage = 'Error: ' + sys.exc_info()[0].__name__
        queue.sendMessage({'type':'error', 'text':errorMessage})
        print(errorMessage)
        traceback.print_tb(sys.exec_info()[2])

def checkIntegrations(hires, imgurId, dropboxToken):
    # Only one integration at a time, please
    if imgurId and dropboxToken:
        print('Only one integration at a time, please')
        return False

    if imgurId and hires:
        print('High resolution images are not supported for imgur integration')
        return False

    # Let's see if Imagemagick is installed
    if not checkMontage():
        return False

    # Let's see if Imgur integration is functioning
    if imgurId and not checkImgur(imgurId):
        return False

    if dropboxToken and not checkDropbox(dropboxToken):
        return False

    return True

def checkMontage():
    try:
        returnVal = subprocess.call(['montage', '--version'])
        if returnVal == 0:
            images.setMontagePath('montage')
            return True
    except FileNotFoundError:
        pass

    #Global montage not found, let's try to find the bundled version.

    try:
        montagePath = os.path.join('imagemagick', 'montage')
        returnVal = subprocess.call([montagePath, '--version'])
        if returnVal == 0:
            images.setMontagePath(montagePath)
            return True
    except FileNotFoundError:
        pass

    print('Imagemagick not found!')
    queue.sendMessage({'type':'error', 'text':'Imagemagick not found!'})
    return False

def checkImgur(imgurId):
    try:
        client = ImgurClient(imgurId, '')
    except ImgurClientError:
        print('Imgur client information incorrect')
        queue.sendMessage({'type':'error', 'text':'Imgur client ID wrong. See README for details.'})
        return False
    return True

def checkDropbox(dropboxToken):
    try:
        dbx = dropbox.Dropbox(dropboxToken)
        dbx.users_get_current_account()
    except:
        print('Problem with dropbox integration')
        queue.sendMessage({'type':'error', 'text':'Problem with Dropbox integration'})
        return False
    return True

def getDecklist(inputStr):
    """
    Finds the decklist list from a given input string. If the string is an URL to deckbox.org or tappedout.net,
    the function will try to download the decklist. Otherwise, the string is interpreted to be a filename.
    """
    if re.match('http', inputStr):
        print('Generating from URL ' + inputStr)
        if re.search('deckbox.org', inputStr):
            # Deckbox.org URL
            response = requests.get(inputStr+'/export')
            deckboxHtml = response.text
            bodyStart = re.search('<body>', deckboxHtml).end()
            bodyEnd = re.search('</body>', deckboxHtml).start()
            deckboxHtmlBody = deckboxHtml[bodyStart:bodyEnd]
            decklist = deckboxHtmlBody.replace('<p>','').replace('</p>','').replace('<strong>','').replace('</strong>','').split('<br/>')
        elif re.search('tappedout.net', inputStr):
            #Tappedout URL
            if inputStr.find('?') > 0:
                # We got some parameters here, let's get rid of them.
                inputStr = inputStr[:inputStr.find('?')]
            response = requests.get(inputStr+'?fmt=txt')
            decklist = response.text.split('\n')
        elif re.search('scryfall', inputStr):
            key = inputStr.split('/')[-1]
            response = requests.get(f'https://api.scryfall.com/decks/{key}/export/text')
            decklist = [line for line in response.text.split('\r\n') if not line.startswith('//')]
        else:
            print('Input URL must be to either to https://deckbox.org or https://tappedout.net.')
            queue.sendMessage({'type':'error', 'text':'Input URL must be either to https://deckbox.org or https://tappedout.net'})
            return None
        del response
        return decklist
    else:
        print('Generating from file ' +  inputStr)
        try:
            with open(inputStr,encoding='utf8') as decklistfile:
                decklist = decklistfile.readlines()
            return decklist
        except FileNotFoundError:
            print('File ' + inputStr + ' not found!')
            queue.sendMessage({'type':'error', 'text':'File '+inputStr+' not found!'})
            return None

if __name__ == '__main__':
    sys.exit(main())
