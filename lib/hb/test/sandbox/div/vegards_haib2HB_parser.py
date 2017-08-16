

print "inne i vegards_haib2HB_parser"
import sys
import os
import shutil
from gold.description.TrackInfo import TrackInfo

# lese inn files.txt og for hver peak skrive ut noe.




def parseannotationfile(infile, keyword):
    print "inne i parseannotationfile"
    f = open(infile, 'r')
    bigdict = {}
    for line in f:
        line=line.strip()
        filename=line.split('\t')[0]
        
        if(filename.find(keyword) > -1):
            elm = line.split('\t')[1].split('; ')
            thisdict={}
            #print filename
            for e in elm:
                pair=e.split("=")
                thisdict[pair[0]]=pair[1]
            if('objStatus' in thisdict):
                if(thisdict['objStatus']=='revoked' or thisdict['objStatus']=='replaced'):
                 print filename, 'revoked, not included'
            else:
                bigdict[filename]=thisdict
    f.close()
    return bigdict
    
def createdirsandcpfile(bigdict, sourcedir, targetdir):
    print "inne i createdirs"
    for key in bigdict:
        thisdict = bigdict[key]
        cellname = thisdict['cell']
        if 'replicate' in thisdict:
            cellname = cellname +'_rep' +thisdict['replicate']
        thisdir = targetdir + '/'+ thisdict['antibody'] + '/' +cellname
        print thisdir
        # lage folder.
        if not os.path.exists(thisdir):
            os.makedirs(thisdir)
        #copy and rename file to bed ot directory
        source = sourcedir + '/'+ key.split( '.gz')[0]
        target = thisdir + '/'+ key[0:key.rindex('.')] + '.bed'
        #target = thisdir + '/'+ key + '.bed'
        print 'target=' + target
        print 'source='+ source
        shutil.copyfile(source, target)
        


def writemetainfo(bigdict, genome, startname, ucscname):
    print "inne i createdirs"
    for key in bigdict:
        thisdict = bigdict[key]
        thistrack = list(startname)
        thistrack.append(thisdict['antibody'])
        cellname = thisdict['cell']
        if 'replicate' in thisdict:
            cellname = cellname +'_rep' +thisdict['replicate']
        thistrack.append(cellname)
        print thistrack
           
           
        ti = TrackInfo(genome, thistrack)
        ti.description = 'TF bindingsites as reported in Peak-files Fetched from UCSC Genome browser, se  http://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g='+ucscname
        ti.description = ti.description + '<BR/>' +'Use of data might be restricted, see dateUnrestricted below.<BR/> '
        for key in thisdict:
            ti.description = ti.description + '<BR/>' + key + '=' + thisdict[key]
        ti.description = ti.description + '<BR/>Annotation from the "files.txt"'
        ti.reference = 'Downloaded from UCSC hgdownload.cse.ucsc.edu, goldenPath/hg19/encodeDCC/wgEncodeHaibTfbs, August 2012. <BR/>The full data policy is available at http://genome.ucsc.edu/ENCODE/terms.html.'
        ti.hbContact = 'vegardny@radium.uio.no'
        #ti.quality = x[3]
       

        print "ti=", ti
        ti.store()



# parse files.txt



#targerdir = '/xanadu/home/vegardny/prosjekter/hyperbrowser/CHIP-seq/HAIB_TFBS'
ucscname= 'wgEncodeUchicagoTfbs'
ucscname= 'wgEncodeSydhTfbs'
ucscname= 'wgEncodeHaibTfbs'
ucscname= 'wgEncodeOpenChromChip'


targerdir = '/usit/invitro/hyperbrowser/standardizedTracks/hg19/Private/vegard/encodeDCC/' + ucscname
sourcedir = '/xanadu/home/vegardny/prosjekter/hyperbrowser/CHIP-seq/encodeDCC/' + ucscname

# read annotationfile.
bigdict = parseannotationfile(sourcedir + '/files.txt', 'Peak')
 
# make folders and hierarchy
createdirsandcpfile(bigdict, sourcedir, targerdir)

# make metainfo commands
writemetainfo(bigdict, 'hg19', ['Private', 'vegard', 'encodeDCC', ucscname], ucscname)
      
      
'''

wgEncodeHaibTfbs
wgEncodeSydhTfbs
wgEncodeUchicagoTfbs
wgEncodeUwTfbs
wgEncodeOpenChromChip
'''
            
       
    



# for hver peak fil
# 1. finne TF (antibody), celle type, replikat.
# 2. lage folder for TF/celletype_repN
# 3. flytte fil dit, gjoere om hvis noedvendig.
# 4. lage linje for aa legge inn metainfo.






print "ferdig i vegards_haib2HB_parser"