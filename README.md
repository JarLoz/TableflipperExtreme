# TableflipperExtreme
This is TableflipperExtreme, a MTG deck creator for Tabletop Simulator. It eats decklists from files or from Tappedout.net and deckbox.org, and outputs files you can import to Tabletop Simulator.

The application will always use the oldest possible printing of a card, disregarding promo printings, with the exception of basic lands, which are always Guru lands. For those willing, there is an option to use the latest reprintings of cards, or even specific printings. See the `--reprint` option as well as the section about adding scryfall URLS to plaintext decklists.

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

Also, instead of giving card counts and numbers, it is possible to just list the URLS to their respective scryfall pages. This mode is very useful for generating tokens and getting specific prints of cards. Note that giving the count of the card is not supported. For example, the example below will result in a deck consisting of Krenko and a Goblin token.

    1 Krenko, Mob Boss
    https://scryfall.com/card/tdds/3

### URL

To create a decklist using an URL, simply use the `--url` option:

    python flipper.py --url "http://tappedout.net/mtg-decks/mono-black-8-rack-modern-discard/" --name 8-Rack

This works with deckbox.org URLS aswell.

## Getting the results into Tabletop Simulator

The application will generate a number of files for your deck. There will be a \<deckname\>.json file, as well as a number of \<deckname\>\_image\_#.jpg files. The image files contain the card faces for your deck. You will need to find a way to upload these to some publicly available host, such as Imgur or Dropbox, and then edit the .json file to point to these hosted files. In the .json file you will find lines such as `"FaceUrl": "<REPLACE WITH URL TO imagename.jpg>"`. (Ctrl-F will be your friend here). Change these to `"FaceUrl":"https://imgur.com/imagename.jpg"`.

Once this is done, you can drop the .json file in your Tabletop Simulator Saved Objects folder.

## Resolution

The application uses the large (672x936 pixels) jpg scans of cards available from scryfall. These images are then scaled down by a factor of 50%, resulting in card image sheets of around 4 megabytes in size. This results in a very acceptable quality for most people. For those willing to tolerate large file sizes, there is a `--hires` option available, which forfeits the scaling, resulting in card image sheets of around 16 megabytes. Note, that when hosted at Imgur, these images will undergo further compression, negating the usefulness of the `--hires` option. Using dropbox or some other generic file hosting is advisable in these cases.

## Reprints

While I personally enjoy the style of older magic cards, there is an option to use the latest non-promo reprints by simply adding the `--reprint` option:

    python flipper.py --file 8rack.txt --name 8-Rack --reprint

## Data sources

This application pulls card data from from [Scryfall API](https://scryfall.com/). Both API calls and image downloads are cached locally.

## Theme song

[Official Theme Song Of Tableflipper Extreme](https://www.youtube.com/watch?v=kQpaT9rhiog)

Happy topdecking, scrublords.
