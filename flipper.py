import sys
import json
from deckconverter import converter 
import argparse

def main():
    with open('decklist.txt',encoding="utf8") as decklistfile:
        decklist = decklistfile.readlines()
    print('Processing Decklist')
    processedDecklist = converter.processDecklist(decklist)
    print('Downloading card images')
    converter.downloadCardImages(processedDecklist)
    print('Creating deck images')
    deckImageNames = converter.createDeckImages(processedDecklist)
    print('Creating TTS JSON')
    ttsJson = converter.createTTSJSON(processedDecklist, deckImageNames)
    with open('output.json', 'w') as outfile:
        json.dump(ttsJson, outfile)
    print('All done')

if __name__ == '__main__':
    sys.exit(main())
