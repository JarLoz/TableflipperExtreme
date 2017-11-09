import sys
import json

def main():
    allCards = json.load(open("json/AllSets.json"))
    setList = json.load(open("json/SetList.json"))
    setOrdered = sorted(setList, key=lambda s: s['releaseDate'])
    setNames = list(map(lambda s: s['code'], setOrdered))
    print(setNames)
    pass

if __name__ == '__main__':
    sys.exit(main())
