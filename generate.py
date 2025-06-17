#!/usr/bin/env python

import os, shutil, subprocess, sys, json, tarfile, toml
from apng import APNG
from PIL import Image
from zipfile import ZipFile
import webp
from lxml import etree as ET

#first load all svgs
print("-- Finding SVGs...")
basepath = "./svg/"
svgs = []
for entry in os.listdir(basepath):
    if(entry.endswith(".svg")):
        svgs.append(entry)

temps = []
for entry in os.listdir(basepath+"temp/"):
    if(entry.endswith(".svg")):
        svgs.append("temp/"+entry)
        temps.append("temp/"+entry)

#load animation data
f = open('animations.json')
anim_data = json.load(f)


defaultcols = {
    "main":        "#ffcb4c", #primary colour
    "eye":         "#fefefe", #eye colour
    "line":        "#65471b", #line colours
    "dark":        "#f19020", #darker version of the primary colour for background details
    "lid":         "#d19020", #eyelid colour
    "hand":        "#a18020", #hand colour, needs to be different from others for contrast
    "tongue":      "#ff5678", #tongue colour (for all important bleps)
    "hair":        "#123456", #hair colour, only shown when show_all = True
    "tail":        "#234567", #tail colour, only shown when show_all = True
    "heart_inner": "#ff5555", #fill colour on hearts
    "heart_outer": "#b10020", #line colour on hearts
    
    "p2_main":        "#5fd3bc", #p2 primary colour
    "p2_eye":         "#ccfefe", #p2 eye colour
    "p2_line":        "#165044", #p2 line colours
    "p2_dark":        "#389482", #p2 darker version of the primary colour for background details
    "p2_lid":         "#2ca089", #p2 eyelid colour
    "p2_hand":        "#3a685f", #p2 hand colour, needs to be different from others for contrast
    "p2_tongue":      "#8b305c", #p2 tongue colour (for all important bleps)
    "p2_hair":        "#345612", #p2 hair colour, only shown when show_all = True
    "p2_tail":        "#456723", #p2 tail colour, only shown when show_all = True
    "p2_heart_inner": "#00c3ff", #p2 fill colour on hearts
    "p2_heart_outer": "#0080a2", #p2 line colour on hearts
    
    "show_all": False, #show_all shows all hidden layers, this renders both the hair and tail tuft
    
    "heterochromia": False #enable if you want each eye to have a different colour
    
    # to hide either hair or tail seperately, set its colour to #0000, this makes it transparent (must be exactly #0000 to work)
}

config = toml.load("config.toml") #load config file
# put config vars in place
res = config["res"]
reverse = config["reverse"]
palettes = config["palette"]
doWebp = config["webp"]

filtered_palettes = {} #specifying palette names in the command line arguments will only export those palettes
palette_count = 0
for pal in palettes.keys():
    if(pal in sys.argv):
        filtered_palettes[pal] = palettes[pal]
        palette_count += 1
if(len(filtered_palettes.keys())>0):
    palettes = filtered_palettes

def convert_with_inkscape(file,res,out):
    #call inkscape from command line to export - this renders svgs slowly but accurately
    inkscape_path = "inkscape" #if youre getting errors saying command called inkscape isnt found, change this to the file path of your inkscape executable!
    args = inkscape_path + " " + file + " --export-area-page -w "+ str(res)+" -h "+ str(res)+" --export-filename=" + out
    print(subprocess.run(args,shell=True)) #if this says "returncode=0" thats good! if its not a zero thats bad, smths going wrong

# find tags without namespace prepended by ElementTree
def trim_xmlns(tag):
    return tag.split('}', 1)[-1] if '}' in tag else tag

# ElementTree resolves xmlns of 'inkscape:label' like this i guess. angy angy
inkscapeLabel = "{http://www.inkscape.org/namespaces/inkscape}label"

# Find if the element is nested within a <g> with 'inkscape:label={name}'
def in_group_labelled(name, elem):
    while elem is not None:
        if (trim_xmlns(elem.tag)=="g") and (elem.attrib.get(inkscapeLabel)==name):
            return True
        elem = elem.getparent()
    return False

print("- Making output directory...")
try:
    os.mkdir("out")
except:
    print("- Output directory already exists.")

for pal in palettes.keys():
    newcols = {**defaultcols, **palettes[pal]} # merge palette overrides against default palette
    
    # cache opacity override for each palette key if specified (#rgba or #rrggbbaa)
    newOpacity = {}
    for key in newcols.keys():
        colourValue = newcols[key]
        if not isinstance(colourValue, str): continue # skip non strings
        
        opacityOverride = 1
        
        if(len(colourValue)==5): # #rgba
            opacityOverride = int(colourValue[4],16)/15
            newcols[key] = colourValue[0:4] # trim alpha
        elif(len(newcols[key])==9): # #rrggbbaa
            opacityOverride = int(colourValue[7:9],16)/255
            newcols[key] = colourValue[0:7] # trim alpha
        
        # override if needed
        if(opacityOverride < 1):
            newOpacity[key] = opacityOverride
    
    #make all the folders!!
    print("- Making required directories for "+pal+"...")
    
    for i in ["out/"+pal,"out/"+pal+"/svg","out/"+pal+"/svg/temp"]:
        try:
            os.mkdir(i)
        except:
            pass
    
    for i in res:
        try:
            os.mkdir("out/"+pal+"/png"+str(i))
        except:
            pass
        
        try:
            os.mkdir("out/"+pal+"/temp"+str(i))
        except:
            pass
        
        if(doWebp):
            try:
                os.mkdir("out/"+pal+"/webp"+str(i))
            except:
                pass
    
    if reverse: #make reversed directories too if we need them
        try:
            os.mkdir("out/"+pal+"/reversed/")
        except:
            pass
        
        for i in res:
            try:
                os.mkdir("out/"+pal+"/reversed/png"+str(i))
            except:
                pass
            
            try:
                os.mkdir("out/"+pal+"/reversed/temp"+str(i))
            except:
                pass
    
    for vectorfile in svgs:
        if(len(sys.argv)>1+palette_count):
            if(vectorfile not in sys.argv):
                continue #if files are specified as arguments, only export those files
        
        data = ""
        print("- Changing "+vectorfile+" to "+pal+"...")
        
        #hell yeah lets ctrl+h the heck out of this file
        with open("svg/"+vectorfile, 'r') as f:
            data = f.read()
        
        # context-aware parsing
        root = ET.XML(data.encode("UTF-8"))
        
        for elem in root.iter():
            # only looking for paths
            if (trim_xmlns(elem.tag)!="path"): continue
            
            # get style of path, or skip if it doesn't have style
            style_key = next((k for k in elem.attrib if trim_xmlns(k) == "style"), None)
            if style_key is None: continue
            style = elem.attrib[style_key]
            
            # Locate fill/stroke that have colour literals matching a key in defaultcols; if so, mark for replacement
            strokeKey = None
            strokeStyleText = None
            fillKey = None
            fillStyleText = None
            fillRpl = None
            
            for key, colour in defaultcols.items():
                sT = f"stroke:{colour};"
                fT = f"fill:{colour};"
                
                if sT in style:
                    strokeStyleText = sT
                    strokeKey = key
                if fT in style:
                    fillStyleText = fT
                    fillKey = key
            
            #<-- for elem in root.iter():
            if strokeKey is not None:
                rplKey = "wehh"
                # heterochromia mode gogo
                if (strokeKey=="eye") and ("heterochromia" in newcols) and (newcols["heterochromia"]):
                    if in_group_labelled("left eye", elem): # find if we are on left eye
                        rplKey = "eye_left"
                    else:
                        rplKey = "eye_right"
                else: # regular palette swap
                    rplKey = strokeKey
                
                opacityOverride = newOpacity.get(rplKey) # override opacity if necessary
                
                if(strokeKey==fillKey): # we can replace both at once if so
                    fillRpl = "fill:" + newcols[rplKey] + ";" # set fill's replacement here to save cycles (speedrunning)
                    
                    if opacityOverride is not None:
                        # we can just set 'opacity' instead of 'fill-opacity' or 'stroke-opacity' separately
                        if ";opacity:1" in style:
                            style = style.replace(";opacity:1", ";opacity:" + str(opacityOverride))
                        else:
                            style = "opacity:" + str(opacityOverride) + ";" + style #prepend
                elif opacityOverride is not None:
                    if ";stroke-opacity:1" in style:
                        style = style.replace(";stroke-opacity:1", ";stroke-opacity:" + str(opacityOverride))
                    else:
                        style = "stroke-opacity:" + str(opacityOverride) + ";" + style #prepend
                
                style = style.replace(strokeStyleText, "stroke:" + newcols[rplKey] + ";")
            
            #<-- for elem in root.iter():
            if fillKey is not None:
                if fillRpl is not None: # already know our fill replacement, and opacity already set
                    style = style.replace(fillStyleText, fillRpl)
                
                else:
                    rplKey = "wehh"
                    # heterochromia mode gogo
                    if (fillKey=="eye") and ("heterochromia" in newcols) and (newcols["heterochromia"]):
                        if in_group_labelled("left eye", elem): # find if we are on left eye
                            rplKey = "eye_left"
                        else:
                            rplKey = "eye_right"
                    else: # regular palette swap
                        rplKey = fillKey
                    
                    opacityOverride = newOpacity.get(rplKey) # override opacity if necessary
                    if opacityOverride is not None:
                        if ";fill-opacity:1" in style:
                            style = style.replace(";fill-opacity:1", ";fill-opacity:" + str(opacityOverride))
                        else:
                            style = "fill-opacity:" + str(opacityOverride) + ";" + style #prepend
                    
                    style = style.replace(fillStyleText, "fill:" + newcols[rplKey] + ";")
            
            # unhide fur if enabled
            if ("show_all" in newcols) and newcols["show_all"]:
                style = style.replace("display:none", "display:inline")
            
            # put back our style into elem
            elem.attrib[style_key] = style
        #<-- for elem in root.iter():
        
        # convert the elementtree back into a string
        data = ET.tostring(root, encoding="Unicode")
        
        #check if files are already exported and if so, skip them
        allpngs = False
        allreversed = False
        if(os.path.exists("out/"+pal+"/svg/"+vectorfile.replace("ying",pal))):
            with open("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), 'r') as f:
                if(f.read()==data):
                    allpngs = True
                    allreversed = True
                    for i in res:
                        if(not os.path.exists("out/"+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal)) and not os.path.exists("out/"+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/",""))):
                            allpngs = False
                        if(reverse and not os.path.exists("out/"+pal+"/reversed/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying","rev"+pal)) and not os.path.exists("out/"+pal+"/reversed/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying","rev"+pal).replace("temp/",""))):
                            allreversed = False
                    if(allpngs and allreversed):
                        print(" - SVGs match and all PNGs exist. Skipping...")
                        continue
        
        print(" - Saving vector "+pal+"/svg/"+vectorfile.replace("ying",pal)+"...")
        with open("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), 'w') as f:
            f.write(data)
        
        for i in res:
            if not allpngs:
                if(vectorfile in temps):
                    print(" - Saving image "+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/","")+"...")
                    convert_with_inkscape("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), i, "out/"+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/",""))
                
                else:
                    print(" - Saving image "+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal)+"...")
                    convert_with_inkscape("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), i, "out/"+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal))
            
            if reverse and not allreversed:
                if(vectorfile in temps):
                    print("  - Reversing "+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/","")+"...")
                    img = Image.open("out/"+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/",""))
                    img.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save("out/"+pal+"/reversed/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying","rev"+pal).replace("temp/",""))
                else:
                    print("  - Reversing "+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal)+"...")
                    img = Image.open("out/"+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal))
                    img.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save("out/"+pal+"/reversed/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying","rev"+pal))
    
    for i in res:
        for anim_name in anim_data["anims"].keys(): 
            anim = anim_data["anims"][anim_name]
            all_frames = True
            for frame in anim:
                if not os.path.exists("out/"+pal+"/png"+str(i)+"/"+frame[0].replace("ying",pal)) and not os.path.exists("out/"+pal+"/temp"+str(i)+"/"+frame[0].replace("ying",pal).replace("temp/","")):
                    all_frames = False
            if(all_frames):
                print(" - Making animated image "+pal+"/png"+str(i)+"/"+anim_name.replace("ying",pal))
                im = APNG()
                for frame in anim:
                    if os.path.exists("out/"+pal+"/temp"+str(i)+"/"+frame[0].replace("ying",pal).replace("temp/","")):
                        im.append_file("out/"+pal+"/temp"+str(i)+"/"+frame[0].replace("ying",pal).replace("temp/",""),delay=frame[1])
                    else:
                        im.append_file("out/"+pal+"/png"+str(i)+"/"+frame[0].replace("ying",pal),delay=frame[1])
                im.save("out/"+pal+"/png"+str(i)+"/"+anim_name.replace("ying",pal))
            
            if reverse: #do it again for reversed images if needed!
                for frame in anim:
                    if not os.path.exists("out/"+pal+"/reversed/png"+str(i)+"/"+frame[0].replace("ying","rev"+pal)) and not os.path.exists("out/"+pal+"/reversed/temp"+str(i)+"/"+frame[0].replace("ying","rev"+pal).replace("temp/","")):
                        all_frames = False
                if(all_frames):
                    print(" - Making animated image "+pal+"/reversed/png"+str(i)+"/"+anim_name.replace("ying","rev"+pal))
                    im = APNG()
                    for frame in anim:
                        if os.path.exists("out/"+pal+"/reversed/temp"+str(i)+"/"+frame[0].replace("ying","rev"+pal).replace("temp/","")):
                            im.append_file("out/"+pal+"/reversed/temp"+str(i)+"/"+frame[0].replace("ying","rev"+pal).replace("temp/",""),delay=frame[1])
                        else:
                            im.append_file("out/"+pal+"/reversed/png"+str(i)+"/"+frame[0].replace("ying","rev"+pal),delay=frame[1])
                    im.save("out/"+pal+"/reversed/png"+str(i)+"/"+anim_name.replace("ying","rev"+pal))
            
            if doWebp:
                enc = webp.WebPAnimEncoder.new(i, i)
                timestamp_ms = 0
                for frame in anim:
                    path = ""
                    if os.path.exists("out/"+pal+"/temp"+str(i)+"/"+frame[0].replace("ying",pal).replace("temp/","")):
                        path = "out/"+pal+"/temp"+str(i)+"/"+frame[0].replace("ying",pal).replace("temp/","")
                    else:
                        path = "out/"+pal+"/png"+str(i)+"/"+frame[0].replace("ying",pal)
                    picture = Image.open(path)
                    pic = webp.WebPPicture.from_pil(picture)
                    enc.encode_frame(pic, timestamp_ms)
                    timestamp_ms += frame[1]
                animd = enc.assemble(timestamp_ms)
                with open("out/"+pal+"/webp"+str(i)+"/"+anim_name.replace("ying",pal).replace(".png",".webp"), 'wb') as f:
                    f.write(animd.buffer())
    
    for i in ["export","export/tarballs"]:
        try:
            os.mkdir(i)
        except:
            pass
    for i in res:
        try:
            os.mkdir("export/zips@"+str(i)+"px")
        except:
            pass
        print("- Making zips for "+pal+"@"+str(i)+"px...")
        shutil.make_archive("export/zips@"+str(i)+"px/Yingmotes_"+pal+"@"+str(i)+"px", 'zip', "out/"+pal+"/png"+str(i))
        if reverse: 
            shutil.make_archive("export/zips@"+str(i)+"px/Reversed_Yingmotes_"+pal+"@"+str(i)+"px", 'zip', "out/"+pal+"/reversed/png"+str(i))
        if i==128:
            print("- Making tarballs for "+pal+"@"+str(i)+"px...")
            with tarfile.open("export/tarballs/Yingmotes_"+pal+"@"+str(i)+"px"+".tar.gz", "w:gz", format=tarfile.GNU_FORMAT) as tar:
                    tar.add("out/"+pal+"/png"+str(i)+"/", arcname="")
            if reverse: 
                with tarfile.open("export/tarballs/Reversed_Yingmotes_"+pal+"@"+str(i)+"px"+".tar.gz", "w:gz", format=tarfile.GNU_FORMAT) as tar:
                    tar.add("out/"+pal+"/png"+str(i)+"/", arcname="")

if(len(sys.argv)==1): #if youre exporting the whole set, include zips
    print("- Making final export zips...")
    for i in res:
        with ZipFile("export/yingmotes@"+str(i)+"px.zip","w") as zip:
            for pal in palettes.keys():
                for file in os.listdir("out/"+pal+"/png"+str(i)+"/"):
                    zip.write("out/"+pal+"/png"+str(i)+"/"+file, arcname=pal+"/"+file)
    shutil.make_archive("export/yingmotes_tarballs", 'zip', "export/tarballs")
    if reverse: 
        for i in res:
            with ZipFile("export/yingmotes_reversed@"+str(i)+"px.zip","w") as zip:
                for pal in palettes.keys():
                        for file in os.listdir("out/"+pal+"/reversed/png"+str(i)+"/"):
                            zip.write("out/"+pal+"/reversed/png"+str(i)+"/"+file, arcname=pal+"/"+file)
