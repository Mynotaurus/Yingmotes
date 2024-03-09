#!/usr/bin/env python

import os
import shutil
import subprocess
import sys
from apng import APNG
import json

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
    "main":  "#ffcb4c",   #primary colour
    "eye" :  "#fefefe",   #eye colour
    "line" : "#65471b",   #line colours
    "dark" : "#f19020",   #darker version of the primary colour for background details
    "lid" :  "#d19020",   #eyelid colour
    "hand" : "#a18020",   #hand colour, needs to be different from others for contrast
    "tongue":"#ff5678",   #tongue colour (for all important bleps)
    "hair" : "#123456",   #hair colour, only shown when show_all = True
    "tail" : "#234567",   #tail colour, only shown when show_all = True
    "show_all":False,      #show_all shows all hidden layers, this renders both the hair and tail tuft
    # to hide either hair or tail seperately, set its color to #0000, this makes it transparent (must be exactly #0000 to work)
    "heart_inner":"#ff5555",
    "heart_outer":"#b10020"
}

palettes = { #this is where the palettes to export are defined
    "ying" : {
        #nothing is changed!
    },

    "yinglemon" : {
        "main" : "#ffff00", 
        "line" : "#6a6a1c", 
        "dark" : "#cccc00", 
        "lid"  : "#808000", 
        "hand" : "#aaaa00",
        "tongue":"#d40000"  
    },

    "yinglime" : {
        "main":"#9f8",
        "eye":"#cff",
        "line":"#131",
        "dark":"#3b4",
        "lid": "#474",
        "hand":"#474",
        "tongue":"#498",
        "hair":"#262",
        "tail":"#262",
        "show_all":True,
        "heart_inner":"#0f0",
        "heart_outer":"#131"
    },

    "myno" : {
        "main":"#e4d9b9",
        "eye" : "#cdebfd",
        "line" : "#880056",
        "dark" : "#a99f8b",
        "lid" : "#a99f8b",
        "hand" : "#998f7b",
        "hair" : "#913fef",
        "tail" : "#913fef",
        "tongue":"#ff66aa",
        "show_all":True,
        "heart_inner":"#fc037b",
        "heart_outer":"#94017b"
    },
    
    "thio" : {
        "main":"#b79879",
        "eye" : "#6574c1",
        "line" : "#3a332d",
        "dark" : "#b58765",
        "lid" : "#ddcdbd",
        "hand" : "#3a332d",
        "hair" : "#6dadfb",
        "tongue":"#953036",
        "tail":"#ddcdbd",
        "show_all":True
    }

    #you can add your own palettes to this list
}

res = [128,720] # resolutions to export at!

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
    args = "inkscape " + file + " --export-area-page -w "+ str(res)+" -h "+ str(res)+" --export-filename=" + out
    print(subprocess.run(args,shell=True)) #if this says "returncode=0" thats good! if its not a zero thats bad, smths going wrong

print("- Making output directory...")
try:
    os.mkdir("out")
except:
    print("- Output directory already exists.")

for pal in palettes.keys():
    newcols = palettes[pal]
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
    for vectorfile in svgs:
        if(len(sys.argv)>1+palette_count):
            if(vectorfile not in sys.argv):
                continue #if files are specified as arguments, only export those files
        data = ""
        print("- Changing "+vectorfile+" to "+pal+"...")
        #hell yeah lets ctrl+h the heck out of this file
        with open("svg/"+vectorfile, 'r') as f:
            data = f.read()
            for key in newcols.keys():
                if(newcols[key]=="#0000"):
                    #if any color is set to #0000, set its opacity to zero
                    #(yes i could implement partial transparency relatively trivially but im eepy so this will do for now)
                    data = data.replace(defaultcols[key]+";fill-opacity:1","PLACEHOLDER_"+key+";fill-opacity:0")
                if(key!="show_all"):
                    data = data.replace(defaultcols[key],"PLACEHOLDER_"+key)
            for key in newcols.keys():
                if(key!="show_all"):
                    data = data.replace("PLACEHOLDER_"+key,newcols[key])
            if("show_all" in newcols.keys()):
                if(newcols["show_all"]):
                    data = data.replace("display:none;","display:inline;")
    
        #check if files are already exported and if so, skip them
        if(os.path.exists("out/"+pal+"/svg/"+vectorfile.replace("ying",pal))):
            with open("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), 'r') as f:
                if(f.read()==data):
                    allpngs = True
                    for i in res:
                        if(not os.path.exists("out/"+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal)) and not os.path.exists("out/"+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/",""))):
                            allpngs = False
                    if(allpngs):
                        print(" - SVGs match and all PNGs exist. Skipping...")
                        continue
        
        print(" - Saving vector "+pal+"/svg/"+vectorfile+"...")
        with open("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), 'w') as f:
            f.write(data)

        for i in res:
            if(vectorfile in temps):
                print(" - Saving image "+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("temp/","")+"...")
                convert_with_inkscape("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), i, "out/"+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/",""))
            else:
                print(" - Saving image "+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png")+"...")
                convert_with_inkscape("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), i, "out/"+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal))
    
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
            


    
    print("- Making zips for "+pal)
    for i in res:
        shutil.make_archive("out/Yingmotes_"+pal+"@"+str(i)+"px", 'zip', "out/"+pal+"/png"+str(i))

