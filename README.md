# TableflipperExtreme
This is TableflipperExtreme, a MTG deck creator for Tabletop Simulator. It will eventually eat Decklists from tappedout and output files that Tabletop simulator accepts.

This project was started because using online converters such as frogtown.me are a pain in the ass.

## Getting started

Install Python3.

Install Imagemagick.

Run `pip install -r requirements.txt`

Run `python3 flipper.py --file <decklist> --name <deckname>`

## Getting the results into Tabletop Simulator

The application will generate a number of files for your deck. There will be a \<deckname\>.json file, as well as a number of \<deckname\>\_image\_#.jpg files. The image files contain the card faces for your deck. You will need to find a way to upload these to some publicly available host, such as Imgur, and then edit the .json file to point to these hosted files. In the .json file you will find lines such as `"FaceUrl": "<REPLACE WITH URL TO imagename.jpg>"`. (Ctrl-F "REPLACE" will be your friend here). Change these to `"FaceUrl":"https://imgur.com/imagename.jpg"`.

Once this is done, you can drop the .json file to your Tabletop Simulator Saved Objects folder, and just spawn the deck ingame.

Happy topdecking, scrublords.

## Data sources

This application pulls card data from [MTGJSON](http://mtgjson.com/) and image data from [Scryfall](https://scryfall.com/).

