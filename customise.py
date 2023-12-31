import os
import shutil
import subprocess

#first we get all the svgs
print("Finding SVGs...")
basepath = "./"
svgs = []
for entry in os.listdir(basepath):
    if(entry.endswith(".svg")):
        svgs.append(entry)


defaultcols = {
    "main":  "#ffcb4c",     #primary colour
    "eye" :  "#fefefe",    #eye colour
    "line" : "#65471b",   #line colours
    "dark" : "#f19020",   #darker version of the primary colour for background details
    "lid" :  "#d19020",    #eyelid colour
    "hand" : "#a18020",   #hand colour, needs to be different from others for contrast
    "tongue":"#ff5678", #tongue colour (for all important bleps)
    "hair" : "#123456",   #hair colour, only shown when enabled
    "show_all":False      #show_all shows all hidden layers, this adds hair and tail tuft (atm, these cannot be enabled seperately in this script :/ sorry)
}

palettes = {
    "orange" : {
        #nothing is changed!
    },

    "lemon" : {
        "main" : "#ffff00", 
        "line" : "#6a6a1c", 
        "dark" : "#cccc00", 
        "lid"  : "#808000", 
        "hand" : "#aaaa00",
        "tongue":"#d40000"  
    },

    "lime" : {
        "main":"#9f8",
        "eye":"#cff",
        "line":"#131",
        "dark":"#3b4",
        "lid": "#474",
        "hand":"#474",
        "tongue":"#141",
        "hair":"#262",
        "show_all":True
    },

    "myno" : {
        "main":"#e4d9b9",
        "eye" : "#cdebfd",
        "line" : "#880056",
        "dark" : "#a99f8b",
        "lid" : "#a99f8b",
        "hand" : "#a99f8b",
        "hair" : "#913fef",
        "tongue":"#ff66aa",
        "show_all":True
    }
}

res = [128,720] #resolutions to export at!

def convert_with_inkscape(file,res,out):
    #call inkscape from command line to export - this renders svgs slowly but accurately
    args = "inkscape --without-gui " + file + " --export-area-page -w "+ str(res)+" -h "+ str(res)+" --export-filename=" + out
    print(subprocess.run(args))

for pal in palettes.keys():
    newcols = palettes[pal]
    #make all the folders!!
    try:
        print("Making new directory...")
        os.mkdir(pal)
        os.mkdir(pal+"/svg")
        for i in res:
            os.mkdir(pal+"/png"+str(i))
    except:
        print("Directory already exists.")
    
    for vectorfile in svgs:
        data = ""
        print("Changing "+vectorfile+" to "+pal+"...")
        #hell yeah lets ctrl+h the heck out of this file
        with open(vectorfile, 'r') as f:
            data = f.read()
            for key in newcols.keys():
                if(key!="show_all"):
                    data = data.replace(defaultcols[key],"PLACEHOLDER_"+key)
            for key in newcols.keys():
                if(key!="show_all"):
                    data = data.replace("PLACEHOLDER_"+key,newcols[key])
            if("show_all" in newcols.keys()):
                if(newcols["show_all"]):
                    data = data.replace("display:none;","display:inline;")

        print("Saving vector "+pal+"/svg/"+vectorfile+"...")
        with open(pal+"/svg/"+vectorfile, 'w') as f:
            f.write(data)

        for i in res:
            print("Saving image "+pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png")+"...")
            convert_with_inkscape(pal+"/svg/"+vectorfile, i, pal+"/png"+str(i)+"/"+vectorfile.replace(".svg",".png"))
    
    print("Making zips for "+pal)
    for i in res:
        shutil.make_archive("Yingmotes_"+pal+"@"+str(i)+"px", 'zip', pal+"/png"+str(i))

