import sys
import json
import base64
import os
import time
#import galaxy.tools.parameters

#from gold.application.GalaxyInterface import *
#from  quick.webtools.plot import CreateBpsVennDIagram
from quick.webtools.plot.CreateBpsVennDIagram import CreateBpsVennDIagram
#from collections import OrderedDict
#from config.Config import *

#http://hyperbrowser.uio.no/dev2/tool_runner?tool_id=vegards_tool&runtool_btn=yes&input=test&dbkey=hg19

def main():
    #print sys.argv
    debug = False
    if debug:
        starttime = time.clock()
        lasttime = starttime
    
    scriptName, datainput, dbkey, output = sys.argv
    data = base64.urlsafe_b64decode(datainput)
    #print 'Data=' + str(data)
    datadict = json.loads(data)
    outfile = open(output, 'w')
    
    catInfo = datadict['catInfo']
    trackNameStrings = [x['fullTrackName'] for x in catInfo.values()]
    trackNames=[x['fullTrackName'].split(':') for x in catInfo.values()]
    genome = dbkey
    
    if debug:
        print 'parsing input ' + str(time.clock()-lasttime)
        lasttime = time.clock()
    
    geSourceList, trackNamesWithoutPath = CreateBpsVennDIagram.getGeSourceList(genome, trackNames)
    
    if debug:
        print 'getGeSourceList ' + str(time.clock()-lasttime)
        lasttime = time.clock()
    
    selectedState = 1
    for thisCatInfo in catInfo.values():
        if thisCatInfo['selection']=='in':
            selectedState = selectedState *  int(thisCatInfo['prime'])
           
    print 'Regions covered by:'
    for key in [ key for key, value in catInfo.items() if value['selection']=='in']:
        print '\t' + key 
    print 'But not by:'
    for key in [ key for key, value in catInfo.items() if value['selection']=='out']:
        print '\t' + key
    
    if debug:    
        print 'Some output ' + str(time.clock()-lasttime)
        lasttime = time.clock()    
    
    # Make input similar, if it is many files or one category.bed file.
    # turn into a categoryBedLIst
    if len(set(trackNameStrings))==1: # assume input is one category.bed file
        categoryBedList, categoryNames = CreateBpsVennDIagram.getCategoryBedList(geSourceList[0])
    else:
        categoryBedList = CreateBpsVennDIagram.collapseToCategoryBedList(geSourceList, trackNamesWithoutPath)
        categoryNames =  trackNamesWithoutPath
        
    if debug:
        nregions = sum([len(onechr) for onechr in categoryBedList.values()])
        print 'getCategoryBedList '+ ' time' + str(time.clock()-lasttime) + ', regions '+ str(nregions)
        #print 'getCategoryBedList '+ ' time' + str(time.clock()-lasttime) + ', regions '+ str(nregions) + ' -'+str([len(chr) for chr in categoryBedList]) + '-'+str(categoryBedList)
        lasttime = time.clock()    
    
    # collapse to startorstop and state lists
    posDict, catDict = CreateBpsVennDIagram.getPosCatDictsFromCategoryBedList(categoryBedList, catInfo)
    
    if debug:
        print 'getPosCatDictsFromCategoryBedList time ' +str(time.clock()-lasttime) 
        lasttime = time.clock()
    
    # iterate list and get stateBPCounter and stateRegions
    stateBPCounter, stateRegions, thisdebugstring = CreateBpsVennDIagram.getStateCount(posDict, catDict)
    for thischr, val in stateRegions.items():
        for line in val:
            if line[2] == selectedState:
                outfile.write(thischr + '\t' + str(line[0]) + '\t'+ str(line[1])+os.linesep)
    if debug:
        nregions = sum([len(onechr) for onechr in stateRegions.values()])          
        print 'write regions len=' + str(nregions) +' time '+ str(time.clock()-lasttime)
        lasttime = time.clock()
    #outfile.write('\n\n\ndebug\n')            
    #outfile.write('thisdebugstring='+str(thisdebugstring)+ '=\n')
    #outfile.write('stateBPCounter='+str(stateBPCounter)+ '=\n')
    #outfile.write('stateRegions='+str(stateRegions)+ '=\n')
            
    outfile.close()
    if debug:
        print 'done ' + str(time.clock()-starttime)
        lasttime = time.clock()



if __name__ == "__main__":
    main()


