# TableflipperExtreme
This is TableflipperExtreme, a MTG deck creator for Tabletop Simulator. It eats decklists from files or directly from tappedout.net and deckbox.org, and outputs files you can import to Tabletop Simulator.

The application will always use the oldest possible printing of a card, disregarding promo printings, with the exception of basic lands, which are always Guru lands. For those willing, there is an option to use the latest reprintings of cards, or even specific printings. See the `--reprint` option as well as the section about adding scryfall URLS to plaintext decklists.

This project was started because using online converters such as frogtown.me are a pain in the ass. This one is too, but not to me.

## Getting started

Install Python 3.5 or newer.

Install Imagemagick.

Run `pip install -r requirements.txt`

Run `python flipper.py -n <deckname> <decklist>`

## Usage

TableflipperExtreme supports two ways of importing deck data: as plaintext files or from URLs. [Delicious example 8-Rack list](http://tappedout.net/mtg-decks/mono-black-8-rack-modern-discard/) created by The Professor from [Tolarian Community College](https://www.youtube.com/user/tolariancommunity).

### Plaintext

If you want to create a decklist from a plaintext file, supply the filename as an argument:

    python flipper.py -n 8-Rack 8rack.txt

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

Also, instead of giving card counts and numbers, it is possible to just list the URLs to their respective scryfall pages. This mode is very useful for generating tokens and getting specific prints of cards. Note that giving the count of the card is not supported for direct URLs. For example, the example below will result in a deck consisting of Krenko and a Goblin token.

    1 Krenko, Mob Boss
    https://scryfall.com/card/tdds/3

### URL

To create a decklist using an URL, simply supply the URL to your decklist as you would with a filename:

    python flipper.py -n 8-Rack "http://tappedout.net/mtg-decks/mono-black-8-rack-modern-discard/"

This works with deckbox.org URLs aswell.

## Getting the results into Tabletop Simulator

The application will generate a number of files for your deck. There will be a \<deckname\>.json file, as well as a number of \<deckname\>\_image\_#.jpg files. The image files contain the card faces for your deck. You will need to find a way to upload these to some publicly available host, such as Imgur or Dropbox, and then edit the .json file to point to these hosted files. In the .json file you will find lines such as `"FaceUrl": "<REPLACE WITH URL TO imagename.jpg>"`. (Ctrl-F will be your friend here). Change these to `"FaceUrl":"https://imgur.com/imagename.jpg"`.

Once this is done, you can drop the .json file in your Tabletop Simulator Saved Objects folder.

## Resolution

The application uses the large (672x936 pixels) jpg scans of cards available from scryfall. These images are then scaled down by a factor of 50%, resulting in card image sheets of around 4 megabytes in size. This results in a very acceptable quality for most people. For those willing to tolerate large file sizes, there is a `--hires` option available, which forfeits the scaling, resulting in card image sheets of around 16 megabytes. Note, that when hosted at Imgur, these images will undergo further compression, negating the usefulness of the `--hires` option. Using dropbox or some other generic file hosting is advisable in these cases.

    python flipper.py -n 8-Rack --hires 8rack.txt

## Reprints

While I personally enjoy the style of older magic cards, there is an option to use the latest non-promo reprints by simply adding the `--reprint` option:

    python flipper.py -n 8-Rack --reprint 8rack.txt

## Custom cards

Creating custom magic cards is fun! Having been inspired by the incredible [Urza's Dream Engine](http://andymakes.com/urzasdreamengine/), I added support for custom cards in Tableflipper Extreme. By using the `--customcards` option and a decklist of image names, you can create decks from completely custom cards. For example, let's assume a `decklist.txt` file containing the following:

    custom_1.jpg
    custom_2.jpg
    custom_3.jpg

Now, as long as the named custom_#.jpg files are in the `imageCache/` folder, you can use the `--customcards`:

    python flipper.py -n CustomDeck --customcards decklist.txt


## Data sources and caching

This application pulls card data from from [Scryfall](https://scryfall.com/). Both API calls and image downloads are cached locally. The API calls are cached to a generated file called `scryfallCache.json`, and the images are cached to the directory `imageCache/`. 

If you want to avoid using the API cache, supply the command with `--nocache` option:

    python flipper.py -n 8-Rack --nocache 8rack.txt

If you want to redownload the card images, delete the `imageCache/`directory.

## Theme song

[Official Theme Song Of Tableflipper Extreme](https://www.youtube.com/watch?v=kQpaT9rhiog)

Happy topdecking, scrublords.
