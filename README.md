# Yingmotes
A customisable yinglet emote pack!

![ying](https://github.com/Mynotaurus/Yingmotes/assets/46263022/5b599ff6-df27-4fc4-9fa8-b640258e48e1) ![yinglemon_nom_clam](https://github.com/Mynotaurus/Yingmotes/assets/46263022/16aa4413-5f39-489a-98fb-dc655d87a53d) ![yinglime_comfy_mug](https://github.com/Mynotaurus/Yingmotes/assets/46263022/dece219b-99c1-4f07-8e90-2d8eca13cbc6) ![myno_aww](https://github.com/Mynotaurus/Yingmotes/assets/46263022/3c94f6cd-22f9-4e09-9371-2e7a5a384139) ![thio_laugh](https://github.com/Mynotaurus/Yingmotes/assets/46263022/2f8c55ea-5e85-4a0d-a714-43d5d253d5e7)


The repo only has svgs for the ying color scheme, but all color schemes have zipped pngs in the [Releases](https://github.com/Mynotaurus/Yingmotes/releases) section. You can get svgs for any color scheme by running `generate.py`.

For most purposes, I would recommend the **ying** color scheme, as it has the best contrast for most use cases, but the others are left in for variety and demonstration of what you can do with custom colors :>

Yinglets are the creation of [Valsalia](https://www.valsalia.com/)

The wonderful [dragn emote set](https://github.com/chr-1x/dragn-emoji) was made by khr

Neofoxes and Neocats are the creations of [Volpeon](https://volpeon.ink/emojis/)

The :ms_robot: emoji is from the [Mutant Standard](https://mutant.tech/) emote set

## Custom Colors
The script `generate.py` is used to generate all the different colour palettes and file types and zip files, and by running it, you can export your own custom emote set. To run it you will need some version of Python, [Inkscape](https://inkscape.org/) and the libraries in `requirements.txt` but i thiiiiink thats it. hopefully.

running it as `python generate.py palette1 palette2 ...` will only export specific palettes, and `python generate.py emote1.svg emote2.svg ...` will only export specific emotes, these can be mixed and matched to export specific emotes in specific palettes eg `python generate.py yinglime ying_sit.svg`

To add custom palettes, add the colors you want to `config.toml`, following the other `palette.name` tables as an example.  If you want hair and a tailpoof, set `show_all` to `true` in your palette. To hide any layer (ie if you want hair and no tailpoof), you can set its color to `#0000` to hide it completely.

Changing the array `res` allows you to set any number of custom export resolutions you may need. The defaults are 128x128px and 720x720px.
Setting the variable `reverse` to `true` will generate flipped versions of each emote as well, stored in a seperate /reversed/ folder for each palette.

The apng files for animated emotes produced by the generator fail to be read by ffmpeg, so if video transcoding is needed for you, you can set `webp` to `true`, which exports all the animated emojis as ffmpeg-compatible animated webp files.
## License
These are licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International https://creativecommons.org/licenses/by-nc-sa/4.0/
