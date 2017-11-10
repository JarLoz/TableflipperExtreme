import sys
import json
from deckconverter import converter 
import argparse

def main():
    with open('decklist.txt') as decklistfile:
        decklist = decklistfile.readlines()
    processedDecklist = []
    print('Processing Decklist')
    for line in decklist:
        splitLine = line.strip().split()
        if len(splitLine) <= 1:
            print('Skipping empty line')
            continue
        count = int(splitLine[0])
        cardName = ' '.join(splitLine[1:])
        processedCard = converter.generateProcessedCardEntry(cardName);
        if processedCard != None:
            print('Found card ' + processedCard['name'])
            converter.downloadCardImage(processedCard)
            for i in range(count):
                processedDecklist.append(processedCard)
        else:
            print("Couldn't find card, line: " +  line)
    print('Creating deck images')
    deckImageNames = converter.createDeckImages(processedDecklist)
    print('Creating TTS JSON')
    ttsJson = converter.createTTSJSON(processedDecklist, deckImageNames)
    with open('output.json', 'w') as outfile:
        json.dump(ttsJson, outfile)
    print('All done')

if __name__ == '__main__':
    sys.exit(main())
