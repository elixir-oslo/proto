try:
    import Image, ImageDraw
except ImportError:
    from PIL import Image, ImageDraw
# from Pycluster import *
from numpy import *
import re

def draw_line(draw,n1,n2,height,scale):
    h0 = 900
    draw.line((n1[0],n1[1],n1[0],h0-height*scale),fill=(255,0,0))
    draw.line((n2[0],n2[1],n2[0],h0-height*scale),fill=(255,0,0))
    draw.line((n1[0],h0-height*scale,n2[0],h0-height*scale),fill=(255,0,0))


def draw_dendrogram(tree,repeatnames,filename): #tree is the output of a hierarchical clustring using Pycluster
    pic_h = 1000 #picture height
    pic_w = 1000 #picture broad
    w_scale = pic_w/(len(repeatnames)+1)
    #h_scale = 10000000

    img = Image.new('RGB',(pic_w,pic_h),(255,255,255))
    draw = ImageDraw.Draw(img)

    r1 = r'\((-?\d+), (-?\d+)\)' #extract the nodes
    r2 = r'.*:\s(.*)' #extract the distance between two clusters
        
    reordered_names = []
    cl_dist = []
    nodes = {}
    
    text_tree = str(tree).split('\n')
    count = 0
    for elem in text_tree:
        node = re.search(r1,elem).groups()
        dist = re.search(r2,elem).groups()
        cl_dist.append(float(dist[0]))
        
        for index in node :
            i = int(index)
            if i >= 0:
                reordered_names.append(repeatnames[i])
                nodes[index] = []
                nodes[index].append(20+count*w_scale)
                nodes[index].append(pic_h-100)
                draw.text((10+count*w_scale,pic_h-100),repeatnames[i],fill=(255,0,0))
                count += 1
                
    h_scale = (pic_h - 100)/max(cl_dist)
    count = -1
    for elem in text_tree :
        node = re.search(r1,elem).groups()
        dist = re.search(r2,elem).groups()
        d = float(dist[0])
        n1 = node[0]
        n2 = node[1]
        draw_line(draw,nodes[n1],nodes[n2],d,h_scale)
        nodes[str(count)] = []
        nodes[str(count)].append(0.5*(nodes[n1][0]+nodes[n2][0]))
        nodes[str(count)].append(pic_h-d*h_scale-100)
        count -= 1
    img.save(filename)
