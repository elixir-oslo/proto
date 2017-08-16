

print "inne i adhoc repair"
#python test/sandbox/div/adhoc_repair.py > /xanadu/home/vegardny/prosjekter/hyperbrowser/div/adhoc_out.txt
import datetime
import sys
import third_party.safeshelve as safeshelve
from gold.description.TrackInfo import TrackInfo
from gold.description.TrackInfo import SHELVE_FN
from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
from gold.util.CommonFunctions import createOrigPath
import re
#print "SHELVE_FN=", SHELVE_FN
trackInfoShelve = safeshelve.open(SHELVE_FN, 'w')
allkeys=trackInfoShelve.keys()
trackInfoShelve.close()

count = 0
for key in allkeys:
    #print key, count
    try: 
        ti = TrackInfo.createInstanceFromKey(key)
        if ti.timeOfPreProcessing > datetime.datetime(2011, 11, 8, 23,0,0) and ti.timeOfPreProcessing < datetime.datetime(2011, 11, 25, 23,0,0):
            if re.search('Nmers|Trashcan|external|Restriction', createOrigPath(ti.genome, ti.trackName))==None:
            # Nmers, external
                print 'trying to repair track ', ti.genome, ti.trackName, ti.timeOfPreProcessing
                count = count +1
                
            ### Sette ID til None og preprocesse.
                #ti.id = None
                #ti.store()
                #PreProcessAllTracksJob(ti.genome, ti.trackName).process()
                
                
                #### printe ut kommandoer for batch job, virket ikke.
                #print 'key =\''+key+'\''
                #print 'ti = TrackInfo.createInstanceFromKey(key)'
                #print 'ti.id = None'
                #print 'ti.store()'
                #print 'PreProcessAllTracksJob(ti.genome, ti.trackName).process()'
    except Exception, e: # fikk assert-feil paa track med : i navnet.
        #do nothing
        sys.stderr.write(str(e)+ "\n")
        #count=count
    #count = count +1
    #if count > 5:
    #   break


print "ferdig", str(count)
