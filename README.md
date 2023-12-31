# Yingmotes
A customisable yinglet emote pack!

![](/lemon/png128/ying_lurk.png)![](/lime/png128/ying_lurk.png)![](/myno/png128/ying_lurk.png)![](/orange/png128/ying_lurk.png)

![](/lemon/png128/ying_nom_pizza.png)![](/lime/png128/ying_nom_pizza.png)![](/myno/png128/ying_nom_pizza.png)![](/orange/png128/ying_nom_pizza.png)

![](/lemon/png128/ying_sleep.png)![](/lime/png128/ying_sleep.png)![](/myno/png128/ying_sleep.png)![](/orange/png128/ying_sleep.png)

Each color scheme has .svg files, .png files at 128px and 720px, and pre-zipped folders for each png format.

For most purposes, I would recommend the **orange** color scheme, as it has the best contrast for most use cases, but the others are left in for variety and demonstration of what you can do with custom colors :>

## Usage
if ive done it right, i think the prezipped @128px versions should work perfectly for importing into fediverse servers

do note that all the individual palettes use the same shortcodes, so if you wanted to upload more than one colour scheme, you would have to rename the files to avoid clashes

## Custom Colors
The script `generate.py` is used to generate all the different colour palettes and file types and zip files, and by adding your own colours to the dictionary inside called `palette` and running it, you can export your own custom emote set. To run it you will need some version of Python and [Inkscape](https://inkscape.org/) but i thiiiiink thats it. hopefully. This script can also be modified to export emotes at any resolution you need.

the code is so bad but hopefully in a way thats understandable at least, lol

## License
These are licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International https://creativecommons.org/licenses/by-nc-sa/4.0/
