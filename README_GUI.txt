TableflipperExtreme

1 - Introduction

This is Tableflipper Extreme, a MTG deck creator for Tabletop Simulator. 
It eats decklists from files or directly from tappedout.net and deckbox.org, 
and outputs files you can import to Tabletop Simulator.

This is the brief version of the documentation, explaining the usage of the GUI
version of Tableflipper Extreme. For full explanation on how the options work,
refer to the CLI version documentation, found here:

https://github.com/JarLoz/TableflipperExtreme/blob/master/README.md

2 - Usage

Click the flipper.exe, input your settings, and click Generate.

2.1 - Options 

Deckname: 

The name of your deck. This will be used in generated filenames, and in Tabletop Simulator

File or Url:

The source of your Decklist. This can either be an URL to a decklist hosted
on Tappedout.net or Deckbox.org, OR the path to a text file containing the decklist.

For information on decklist formats, see full documentation here:

https://github.com/JarLoz/TableflipperExtreme/blob/master/README.md#plaintext

Output folder:

The folder where the resulting .json and .jpg files will be generated to. If left blank,
the files will be generated in the same folder as the executable.

ImgurID:

If you wish to use the Imgur integration, put your Imgur client ID in this field.
This value will be saved in file called "imgurId.txt" at the root of the application,
so you don't need to input it every time.

For more information on how to acquire the Imgur client ID, see the full documentation:

https://github.com/JarLoz/TableflipperExtreme/blob/master/README.md#imgur-integration

Dropbox Token:

If you wish to use the Dropbox integration, put your Dropbox Token in this field.
This value will be saved in file called "dropboxToken.txt" at the root of the application,
so you don't need to input it every time.

For more information on how to acquire the Dropbox token, see the full documentation:

https://github.com/JarLoz/TableflipperExtreme/blob/master/README.md#dropbox-integration

Basic Lands:

Selection for which style of basic lands to use for the generated deck.

High Resolution:

Checking this box will create high resolution versions of the deck images. These images
will be about four times as large as the default resolution.

Reprints:

Checking this box will use the most representative reprint of the card, as decided by
Scryfall. If not checked, then the first printing of the card will be used.

No cache:

Checking this box will bypass the scryfall API cache. For debugging purposes.

Imgur Upload:

Enables the imgur integration

Dropbox Upload:

Enables the dropbox integration.


3 - Getting the results into Tabletop Simulator

The application will generate a number of files for your deck. There will be a deckname.json 
file, as well as a number of deckname_image_#.jpg files. The image files contain the card 
faces for your deck. You will need to find a way to upload these to some publicly available 
host, such as Dropbox, and then edit the .json file to point to these hosted files. In the 
.json file you will find lines such as "FaceUrl": "<REPLACE WITH URL TO imagename.jpg>". 
(Ctrl-F will be your friend here). Change these to "FaceUrl":"https://example.com/imagename.jpg".

Once this is done, you can drop the .json file in your Tabletop Simulator Saved Objects folder.
This folder is usually located at C:\Users\username\My Documents\My Games\Tabletop Simulator\Saves\Saved Objects\

If you do not want to be bothered with this, you can use the Imgur and Dropbox integrations. 
In this case, the images are uploaded and the .json file will be edited automatically.
