#! /usr/bin/python
#tileCutter v3 (February 12, 2006)
#by Peter Pesti, http://www.cc.gatech.edu/~pesti/tileCutter/

import popen2 #subprocess.Popen is only available from Python 2.4
import sys
import os
import tempfile
from random import random


if os.name=='nt': #Windows
    imdir= r"C:\Program Files\ImageMagick-6.2.6-Q16\\"
    nice= []
else:
    imdir= "" #Linux
    nice= ["nice"]

argnum= len(sys.argv) - 1

if argnum<13:
    print argnum
    print sys.argv
    print("USAGE: tileCutter3.py [outputDir] [extension] [source map] [map_x1] [map_x2] [map_y1] [map_y2] [tile_x1] [tile_y1] [tile_x2] [tile_y2] [background color] [logo image]")
    sys.exit(1)

outputDir= sys.argv[1]
ext= sys.argv[2]
if (ext=="jpg"):
    ext="jpeg"
if (ext!="png" and ext!="gif" and ext!="jpeg"):
    print "Invalid target extension: "+ext
    sys.exit(2)

filename= sys.argv[3]
if not(os.path.isfile(filename)):
       print "Input file '"+filename+"' does not exist."
       sys.exit(3)

#pixel-position of feature points on source map image: (top-left is 0,0)
map_x1, map_y1, map_x2, map_y2= int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])

z= int(sys.argv[8])
#pixel-position of feature points on Google map at given zoom level: (top-left is 0,0)
x1,y1,x2,y2= int(sys.argv[9]), int(sys.argv[10]), int(sys.argv[11]), int(sys.argv[12])

background= sys.argv[13]

if argnum<14:
    logofile= []
else:
    logofile= sys.argv[14]

[tileWidth, tileHeight]= [256, 256]

print "Processing '"+filename+"'..."

class ZoomLevel:
    z, scaling_x, scaling_y, x0, y0= 0,0,0,0,0
    def __init__(self, z, x1,y1,x2,y2,map_x1,map_y1,map_x2,map_y2):
        self.z= z
        self.scaling_x= (x2-x1+1) / float(map_x2-map_x1+1)
        self.scaling_y= (y2-y1+1) / float(map_y2-map_y1+1)
        self.x0= x1 - int(map_x1*self.scaling_x) #Gmap x
        self.y0= y1 - int(map_y1*self.scaling_y) #Gmap y
        
    def zoomIn(self):
        self.z+= 1
        self.scaling_x*= 2.0
        self.scaling_y*= 2.0
        self.x0*= 2
        self.y0*= 2

    def zoomOut(self):
        self.z-= 1
        self.scaling_x/= 2.0
        self.scaling_y/= 2.0
        self.x0= self.x0/2
        self.y0= self.y0/2


def mkdir(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)

level= ZoomLevel(z, x1,y1,x2,y2,map_x1,map_y1,map_x2,map_y2)

mkdir(outputDir)

#zoom in using Google-pixel-coords to just-zoom-in-after our map:
while level.scaling_x<1 or level.scaling_y<1:
    level.zoomIn()
    
#zoom out using Google-pixel-coords to just-zoom-out-before our map:
while level.scaling_x>2 or level.scaling_y>2:
    level.zoomOut()

print "Initial scaling: "+str(level.scaling_x)+", "+str(level.scaling_y)

#(tmpfile, tmppath)= tempfile.mkstemp()
(tmpout, tmperr)= popen2.popen2(nice+[imdir+r"identify", filename])
os.wait()

[width, height]= tmpout.read().split()[2].split('+')[0].split('x')
width, height= int(width), int(height)

while level.z>=0 and width*level.scaling_x>tileWidth/2:
    zdir= outputDir+"/"+str(level.z)
    print "\tzoom level "+zdir+"..."
    mkdir(zdir)
    todo=[]

    print "\t\tcutting tiles..."

    #resize to match this zoom level:
    w= int(width*level.scaling_x)
    h= int(height*level.scaling_y)
    todo+= ["-resize", str(w)+"x"+str(h)+"!"]

    todo+= ["-border",str(tileWidth)+"x"+str(tileHeight),"-bordercolor",background]
    #calculate padding at this zoom level:
    pad_x= level.x0 % tileWidth
    pad_y= level.y0 % tileHeight
    #calculate top-left tile coordinates at this zoom level:
    tile_x0= (level.x0 - pad_x)/tileWidth
    tile_y0= (level.y0 - pad_y)/tileHeight

    #add required padding to top-left:
    w+= pad_x
    h+= pad_y

    #pad bottom-right to make complete tiles:
    if w%tileWidth != 0:
        w+= tileWidth - (w%tileWidth)
    if h%tileHeight != 0:
        h+= tileHeight - (h%tileHeight)
    todo+=["-crop",str(w)+"x"+str(h)+"+"+str(tileWidth-pad_x)+"+"+str(tileHeight-pad_y)+"!"]

    todo+=["-crop",str(tileWidth)+"x"+str(tileHeight)]

    #execute:
    popen2.popen2(nice+[imdir+r"convert"]+todo+[filename, zdir+".png"])
    os.wait()

    tileYmax= h/tileHeight
    tileXmax= w/tileWidth
    for y in range(tileYmax):
        for x in range(tileXmax):
            if tileXmax==1 and tileYmax==1:
                sourcename= zdir+".png" #no tiles have been cut
            else:
#                sourcename= zdir+".png."+str(tileXmax*y+x) #tiles
                sourcename= zdir+"-"+str(tileXmax*y+x)+".png" #tiles
#            print 'rename', sourcename, zdir+"/"+str(tile_x0+x)+"-"+str(tile_y0+y)+".png"
            os.rename(sourcename, zdir+"/"+str(tile_x0+x)+"-"+str(tile_y0+y)+".png")

    level.zoomOut()


#    print "\t\tadjusting color depth, quality, format and logo..."
#    todo= []
#    #user-specified format:
#    todo+= ["-format",ext]
#    #adjust color depth and quality:
#    if ext=="gif":
#        todo+=["-colors","64"]
#    elif ext=="png":
#        todo+=["-colors","4096"]
##        todo+=["-quality","100"] #maximum compression
#    elif ext=="jpeg":
#        todo+=["-quality","70"]
#    #put logo:
#    if logofile!=[]:
#        todo+= ["-draw", "image Exclusion "+str(tileWidth*0.3)+","+str(tileHeight*0.45)+" 0,0 '"+logofile+"'"]
#    popen2.popen2(nice + [imdir+r"mogrify"] + todo + [zdir+"/*.png"])
#    os.wait()

    #remove temporary png-tiles:
    if (ext!="png"):
        for f in os.listdir(zdir):
            if f.find("png")!=-1:
                os.remove(os.path.join(zdir,f))

print "done."
