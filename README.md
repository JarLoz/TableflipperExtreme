# TableflipperExtreme
This is TableflipperExtreme, a MTG deck creator for Tabletop Simulator. It eats decklists from files or from Tappedout.net, and outputs files you can import to Tabletop Simulator.

The application will always use the oldest possible printing of a card, disregarding promo printings, with the exception of basic lands, which are always Guru lands. This is due to my personal preferences, and is not negotiable. If you really want ugly Kaladesh Invocations in your decks, see the section about importing JSON files below.

This project was started because using online converters such as frogtown.me are a pain in the ass. This one is too, but not to me.

## Getting started

Install Python 3.5 or newer.

Install Imagemagick.

Run `pip install -r requirements.txt`

Run `python flipper.py --file <decklist> --name <deckname>`

## Usage

TableflipperExtreme supports three ways of importing deck data: as plaintext files, as URLS to tappedout.net, and as .json files. [Delicious example 8-Rack list](http://tappedout.net/mtg-decks/mono-black-8-rack-modern-discard/) created by The Professor from [Tolarian Community College](https://www.youtube.com/user/tolariancommunity).

### Plaintext

If you want to create a decklist from a plaintext file, you need to use the `--file` option:

    python flipper.py --file 8rack.txt --name 8-Rack

The format of the plaintext file is the same as when exporting as a .txt file from Tappedout:

    2 Dakmor Salvage
    4 Ensnaring Bridge
    3 Inquisition of Kozilek
    4 Liliana of the Veil
    4 Mutavault
    3 Pack Rat
    4 Raven's Crime
    4 Shrieking Affliction
    2 Slaughter Pact
    4 Smallpox
    10 Swamp
    4 The Rack
    4 Thoughtseize
    4 Urborg, Tomb of Yawgmoth
    4 Wrench Mind

    Sideboard:
    2 Darkblast
    2 Dismember
    2 Extirpate
    4 Grafdigger's Cage
    2 Surgical Extraction
    3 Torpor Orb

Sideboard is supported, and reading the decklist is done case-insensitively.

### URL

To create a decklist using an URL, simply use the `--url` option:

    python flipper.py --url "http://tappedout.net/mtg-decks/mono-black-8-rack-modern-discard/" --name 8-Rack
    
### JSON

If you want to bypass the decklist parsing, it is also possible to pass a JSON file mimicing the `processedDecklist` structure the application uses internally. This is useful if you just want certain prints of cards or tokens. Using the `--json` option is straightforward:

    python flipper.py --json tokens.json --name Tokens
    
The structure of the json file is as follows:

    [
      {"name":"Spirit","set":"tc15","number":"22"},
      {"name":"Spirit","set":"tavr","number":"4"},
      {"name":"Goblin","set":"tori","number":"6"}
    ]
    
The file contains an array of objects, and each object has three members: name, set and number. `name` is only used to nickname the card object in Tabletop Simulator. `set` specifies the MTG set code name, and `number` is the card's set number. The example JSON will result in a deck containing the following tokens: [BW Spirit](https://scryfall.com/card/tc15/22), [U Spirit](https://scryfall.com/card/tavr/4) and [Goblin](https://scryfall.com/card/tori/6).

## Getting the results into Tabletop Simulator

The application will generate a number of files for your deck. There will be a \<deckname\>.json file, as well as a number of \<deckname\>\_image\_#.jpg files. The image files contain the card faces for your deck. You will need to find a way to upload these to some publicly available host, such as Imgur or Dropbox, and then edit the .json file to point to these hosted files. In the .json file you will find lines such as `"FaceUrl": "<REPLACE WITH URL TO imagename.jpg>"`. (Ctrl-F will be your friend here). Change these to `"FaceUrl":"https://imgur.com/imagename.jpg"`.

Once this is done, you can drop the .json file in your Tabletop Simulator Saved Objects folder.

Happy topdecking, scrublords.

## Data sources

This application pulls card data from [MTGJSON](http://mtgjson.com/) and image data from [Scryfall](https://scryfall.com/).

## Theme song

[Official Theme Song Of Tableflipper Extreme](https://www.youtube.com/watch?v=kQpaT9rhiog)
