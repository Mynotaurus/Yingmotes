#!/usr/bin/env python

import os, shutil, subprocess, sys, json, tarfile, toml
from apng import APNG
from PIL import Image
from zipfile import ZipFile

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

config = toml.load("config.toml") #load config file
# put config vars in place
res = config["res"]
reverse = config["reverse"]
palettes = config["palette"]

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
        allpngs = True
        allreversed = True
        if(os.path.exists("out/"+pal+"/svg/"+vectorfile.replace("ying",pal))):
            with open("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), 'r') as f:
                if(f.read()==data):
                    for i in res:
                        if(not os.path.exists("out/"+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal)) and not os.path.exists("out/"+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/",""))):
                            allpngs = False
                        if(reverse and not os.path.exists("out/"+pal+"/reversed/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying","rev"+pal)) and not os.path.exists("out/"+pal+"/reversed/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying","rev"+pal).replace("temp/",""))):
                            allreversed = False
                    if(allpngs and allreversed):
                        print(" - SVGs match and all PNGs exist. Skipping...")
                        continue
        
        print(" - Saving vector "+pal+"/svg/"+vectorfile+"...")
        with open("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), 'w') as f:
            f.write(data)

        for i in res:
            if not allpngs:
                if(vectorfile in temps):
                    print(" - Saving image "+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("temp/","")+"...")
                    convert_with_inkscape("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), i, "out/"+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/",""))
                    
                else:
                    print(" - Saving image "+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png")+"...")
                    convert_with_inkscape("out/"+pal+"/svg/"+vectorfile.replace("ying",pal), i, "out/"+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal))

            if reverse and not allreversed:
                if(vectorfile in temps):
                    print("  - Reversing "+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/","")+"...")
                    img = Image.open("out/"+pal+"/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying",pal).replace("temp/",""))
                    img.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save("out/"+pal+"/reversed/temp"+str(i)+"/"+vectorfile.replace(".svg",".png").replace("ying","rev"+pal).replace("temp/",""))
                else:
                    print("  - Reversing "+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png")+"...")
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