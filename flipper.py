import sys
import json
from deckconverter import converter 
import argparse

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f','--file', help='Filename of the decklist, in tappedout.net txt format')
    group.add_argument('-u','--url', help='URL to tappedout.net decklist')
    group.add_argument('-j','--json', help='JSON file containing processed card list. Good for tokens.')
    parser.add_argument('-n','--name', help='Name of the deck')
    args = parser.parse_args()

    if (args.file == None and args.url == None and args.json == None):
        print('Need some input. Exiting.')
        return

    if (args.file == None):
        print('Other input not yet supported LOL')
        return

    with open(args.file,encoding="utf8") as decklistfile:
        decklist = decklistfile.readlines()

    deckName = 'Deck'
    if (args.name):
        deckName = args.name

    print('Processing Decklist')
    processedDecklist,processedExtraCards = converter.processDecklist(decklist)
    print('Downloading card images')
    converter.downloadCardImages(processedDecklist)
    converter.downloadCardImages(processedExtraCards)
    print('Creating deck images')
    deckImageNames = converter.createDeckImages(processedDecklist, deckName)
    extraImageNames = converter.createDeckImages(processedExtraCards, deckName+'-extra')
    print('Creating TTS JSON')
    baseDeckObject = converter.createDeckObject(processedDecklist, deckName, deckImageNames, -0.0)
    extraDeckObject = converter.createDeckObject(processedExtraCards, deckName+'-extra', extraImageNames, 4.0)
    ttsJson = {'ObjectStates':[baseDeckObject,extraDeckObject]}
    with open(deckName+'.json', 'w',encoding='utf8') as outfile:
        json.dump(ttsJson, outfile, indent=2)
    print('All done')

if __name__ == '__main__':
    sys.exit(main())


