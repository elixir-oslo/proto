

# cd /usit/invitro/data/hyperbrowser/hb_core_developer/trunk
# python test/sandbox/div/vegards_encodedcc2HB_parser.py  
# python test/sandbox/div/vegards_encodedcc2HB_parser.py > /cluster/home/vegardny/temp/encodeparser.out

print "inne i vegards_encodedcc2HB_parser"
import sys
import os
import shutil
from gold.description.TrackInfo import TrackInfo

# lese inn files.txt og for hver peak skrive ut noe.
# ta vare paa metainfo og skrive den i HB



# parsing the files.txt in every encodedcc folder, each line describing the datafile in the same folder with some attributes that are stored in a dict and used in tracknameing and metainfo
# returns the dict
# includeviews is a filter for which of the rows to be included in the dict (and later be parsed and moved)
# some more rows with an errorstatus is also not included.
def parseannotationfile(infile, includedviews):
    print "inne i parseannotationfile"
    f = open(infile, 'r')
    bigdict = {}
    errorobjstatus = ('revoked', 'replaced', 'renamed') # renamed is somewhat unclear whether they should be included or not.
    for line in f:
        line=line.strip()
        filename=line.split('\t')[0]
        #print 'parser line=', filename
        #for thiskeyword in keyword:
        #    if(filename.find(thiskeyword) > -1):
        elm = line.split('\t')[1].split('; ')
        thisdict={}
        #print filename
        for e in elm:
            pair=e.split("=")
            thisdict[pair[0]]=pair[1]
        if 'view' not in thisdict or thisdict['view'] not in includedviews:
            print 'Not allowed viewtype =', filename
            continue
        if 'objStatus' in thisdict:
            #if thisdict['objStatus']=='revoked' or thisdict['objStatus']=='replaced':
            skip = False
            for e in errorobjstatus:
                if thisdict['objStatus'].find(e)!=-1:
                    print filename, ' not used since it has an objStatus indicating it should not be used:' , thisdict['objStatus']
                    skip=True
            if skip:         # not including those with reported problems.
                continue
        # objStatus seems to be given only when something was wrong and never stated when ok,
        #print 'view=', thisdict['view'], 'included =', includedviews
        bigdict[filename]=thisdict
    f.close()
    return bigdict



# makes a sensible HB trackname, this is somewhat ad-hoc.
# in ucsc the tracks has many dimensions (treatment, protocol, replicate and so on. Messy as a hierarchy)
def gettrackname(onedict, startname, thisucscname):
    thisdict = onedict.copy()
    thistrack =  list(startname)
    #thistrack.append('Experimentally determined ('+thisdict['dataType']+' '+thisdict['view'] +')')
    thistrack.append(thisdict['cell'])
    if('antibody' in thisdict):
        thistrack.append(thisdict['antibody'])
    trackname = ''
    if 'lab' in thisdict:
        trackname = trackname + thisdict['lab']
    else:
         trackname = trackname + thisucscname
    #trackname = thisucscname
    if 'protocol' in thisdict:
        trackname = trackname + '-' + thisdict['protocol']
    if 'treatment' in thisdict:
        trackname = trackname + '-' + thisdict['treatment']
    if 'control' in thisdict:
        trackname = trackname + '-' + thisdict['control']
    if 'controlId' in thisdict:
        trackname = trackname + '-' + thisdict['controlId']
    if 'replicate' in thisdict:
        trackname = trackname + '-rep' + thisdict['replicate']
    thistrack.append(trackname)
    return thistrack



# Makes the folders according to tracknames in targetdir (standardizedtracks/hg19)
# startname and thisucsname are begining of trackname
# moves the (bed) files to their HB folder.
def createdirsandcpfile(bigdict, sourcedir, targetdir, startname, thisucscname, copyfiles):
    print "in createdirs"
    for key in bigdict:
        thisdict = bigdict[key]
        thisdir=targetdir + '/' + os.sep.join(gettrackname(thisdict, startname, thisucscname))
        #print thisdir
        # lage folder.
        
        if not os.path.exists(thisdir):
            os.makedirs(thisdir)
        else:
            print 'Dir exists: ' + thisdir + ' . Might be something wrong, two bedfiles in same folder?'
            
        #copy and rename file to bed ot directory
        source = sourcedir + '/'+ key.split( '.gz')[0]
        target = thisdir +'/'+ key[0:key.rindex('.')] + '.bed'   # must be bed for HB to recognize?
        #print 'target=' + target
        #print 'source='+ source
        if copyfiles:
            shutil.copyfile(source, target)


def writemetainfo(bigdict, genome, startname, thisucscname):
    print "in writemetainfo"
    for key in bigdict:
        thisdict = bigdict[key]
        thistrack = gettrackname(thisdict, startname, thisucscname)
        #print thistrack
        ti = TrackInfo(genome, thistrack)
        #ti.description = 'TF bindingsites as reported in Peak-files Fetched from UCSC Genome browser, se  http://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g='+ucscname
        ti.description = 'Tracks fetched from UCSC Genome browser, se  http://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g='+thisucscname
        ti.description = ti.description + '<BR/>' +'Use of data might be restricted, see dateUnrestricted below.<BR/> '
        for key in thisdict:
            ti.description = ti.description + '<BR/>' + key + '=' + thisdict[key]
        ti.description = ti.description + '<BR/>Annotation from the "files.txt"'
        ti.reference = 'Downloaded from UCSC hgdownload.cse.ucsc.edu, goldenPath/hg19/encodeDCC/. <BR/>The full data policy is available at http://genome.ucsc.edu/ENCODE/terms.html.'
        ti.hbContact = 'vegardny@radium.uio.no'
        if 'cell' in thisdict:
            ti.cellTypeSpecific = True
            ti.cellType = thisdict['cell']
        #ti.quality = x[3]
        #print 'thistrack:' + str(thistrack) + '\n'
        #print "\n\nti=", ti, '\n\n'
        #print 'cellType=' + ti.cellType + '=\n'
        ti.store()



# parse files.txt



#targerdir = '/xanadu/home/vegardny/prosjekter/hyperbrowser/CHIP-seq/HAIB_TFBS'
#ucscname= 'wgEncodeUchicagoTfbs'
#ucscname= 'wgEncodeSydhTfbs'
#ucscname= 'wgEncodeHaibTfbs'
#ucscname= 'wgEncodeOpenChromChip'
#ucscname= 'wgEncodeUwDgf'

#ucscnames = ['wgEncodeUchicagoTfbs', 'wgEncodeSydhTfbs', 'wgEncodeHaibTfbs', 'wgEncodeOpenChromChip']
ucscnames = ['wgEncodeUwDgf']
#ucscname = os.listdir('')
ucscnames = ['wgEncodeOpenChromDnase', 'wgEncodeOpenChromFaire', 'wgEncodeOpenChromSynth', 'wgEncodeUwDgf', 'wgEncodeUwDnase']
ucscnames = ['wgEncodeAwgTfbsUniform']

#targerdir = '/usit/invitro/hyperbrowser/standardizedTracks/hg19/Private/vegard/encodeDCCtest'
#targerdir = '/usit/invitro/hyperbrowser/standardizedTracks/hg19/Gene regulation/TFBS'



#toptrackname =  ['Gene regulation', 'TFBS']
genomename = 'hg19'
targerdir = '/usit/invitro/hyperbrowser/standardizedTracks/' + genomename
#toptrackname =  ['Chromatin']
#toptrackname =  ['Private','vegard', 'encodeDCCtest']
toptrackname =  ['Gene regulation', 'Transcription factor regulation', 'Experimentally determined (ChIP-seq peaks)', 'wgEncodeAwgTfbsUniform']
#sourcedir = '/cluster/home/vegardny/prosjekter/hyperbrowser/encodedcc/data/'
#sourcedir = '/usit/invitro/work/hyperbrowser/nosync/tempColl/hg19/Chromatin/DNaseI/'
sourcedir = '/usit/invitro/work/hyperbrowser/nosync/tempColl/hg19/Gene regulation/Transcription factor regulation/Experimentally determined (ChIP-seq peaks)/'
viewtypes = ['Peaks']

for thisucscname in ucscnames:
    print 'parsing ' + thisucscname
    thissourcedir = sourcedir + thisucscname
    # read annotationfile.
    bigdict = parseannotationfile(thissourcedir + '/files.txt', viewtypes)
    # make folders and hierarchy
    #createdirsandcpfile(bigdict, thissourcedir, targerdir, toptrackname, thisucscname, copyfiles=True)
    #smalldict = dict([ (k, bigdict.get(k)) for k in bigdict.keys()[0:3] ]) # debug
    #createdirsandcpfile(smalldict, thissourcedir, targerdir, toptrackname, copyfiles=False)
    # here a HB preprocess could be run.
    # make metainfo commands
    writemetainfo(bigdict, genomename, toptrackname, thisucscname)
    #writemetainfo(smalldict, genomename, toptrackname, thisucscname)

'''

wgEncodeHaibTfbs
wgEncodeSydhTfbs
wgEncodeUchicagoTfbs
wgEncodeUwTfbs
wgEncodeOpenChromChip
'''
            
       
    








print "ferdig i vegards_encodedcc2HB_parser"