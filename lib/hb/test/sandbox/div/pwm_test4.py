


# cd /usit/invitro/data/hyperbrowser/hb_core_developer/trunk   
# python test/sandbox/div/pwm_test4.py
# time  python /usit/invitro/data/hyperbrowser/hb_core_developer/trunk/test/sandbox/div/pwm_test4.py


print "inne i pwmtest4"

import MOODS
import Bio.Seq
import Bio.SeqIO
import Bio.Motif
#from numpy  import *
from datetime import datetime
import numpy as np
import os
import subprocess
#import gc

NO_SCORE_VALUE = -100
#MOODS_PATH = ['/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/MOODS/src/find_pssm_dna', '1', '--algorithm=0']
MOODS_PATH = ['/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/MOODS/src/find_pssm_dna', '1']


# 
# seq, string eller Bio.Seq
# mat, pwm matrise
# return, array med score per basepar, -100 som score der MOODS ikke gir noe.
def getMOODSscore_old(seq, mat):
    results = MOODS.search(seq, [mat], thresholds=1, absolute_threshold=False)
    resarray = np.zeros( (1, len(seq)), dtype=np.dtype('Float32'))
    resarray[:,:] = -100
    for (position, score) in results[0]:
        resarray[0, position] = score
    return(resarray)
    

# seqfile, path to seq fasta file, passed to MOODS
# matfile, path to pwm matrise file, passes to MOODS
# return, array with score per basepair, NO_SCORE_VALUE as score where MOODS does not give a score.
def getMOODSscore(seqfile, matfile, seqlen):
    #resarray = np.zeros( (1, len(seq)), dtype=np.dtype('Float32'))
    resarray = np.zeros( (1, seqlen), dtype=np.dtype('Float32'))
    resarray[:,:] = NO_SCORE_VALUE
    #process = subprocess.Popen(['cat', '20linjer.txt'], shell=False, stdout=subprocess.PIPE)
    #process = subprocess.Popen([MOODS_PATH, '1', seqfile, matfile], shell=False, stdout=subprocess.PIPE)
    process = subprocess.Popen(MOODS_PATH + [seqfile, matfile], shell=False, stdout=subprocess.PIPE)
    for line in process.stdout:
        if len(line) > 1:
            elm = line.split('\t')
            if len(elm)==2: # running with algo=0 gives an extra header due to sloppy testing of MOODS.
                resarray[0, int(elm[0])] = float(elm[1])
    return(resarray)


# Findinw max value for a sliding window of the pwm length, using numpy.max of arrays.
# bpscores, array score per basepair, can have to rows (for other strand)
# windowlength, distance in front of bp that will be searched for maxvalue 
# returns, array with max value found for each bp.
def getMaxPWMScore(bpscores, windowlength):
    ret = bpscores.copy()
    for n in range(1,windowlength):
        #print n
        ret = np.concatenate((ret,bpscores),)
        startx=n*len(bpscores)
        stopx=startx+len(bpscores)
        ret[startx:stopx, n:] = bpscores[:,:len(bpscores[0,:])-n]
    return np.max(ret, axis=0)
#return(ret)        

# Short helper function to make a wiggle file for the pwm scores. Scores formated to 2 decimals.
# thisvector, list with values, one for each bp
# name, name of the track, put in wiggle header.
# chr, put in wiggle header and used as filename + .wig
# path, where file will be made
def vegardswritewiggle(thisvector, name, chr, destpath):
    thisdir = destpath 
    if not os.path.exists(thisdir):
        os.makedirs(thisdir)
    thispath=thisdir+'/'+chr+'.dat.wig' # need .dat.wig to be recognized by hb?
    outfile = open(thispath, 'w')
    outfile.write('track type=wiggle_0 name='+name+'\n')
    outfile.write('fixedStep\tchrom='+chr+'\tstart=1\tstep=1\n')
    for val in thisvector:
        #print val
        #outfile.write(str(val)+'\n')
        outfile.write('%0.2f\n' % val)
    outfile.close()
#"%0.2f" % i 


#
# fastafile, list of filename with sequences to be scored
# pmwfiles, list of filnames of the pwm files to be used on the sequences
# destdir, path to where the output will be writte, additional hierarchis beneath will be made.
# both_strands, should the pwm be matched on both strand (and best scored from both strand used in bp)
def makePWMscorefiles(fastafiles, pwmfiles, destdir, both_strands=True):
    for fastaf in fastafile:
        ### seqence only needed for length here. MOODS does this parsing again later but without reporting length.
        thisseqname = fastaf.split('/')[-1].split('.')[0]
        handle = open(fastaf, "r")
        records = list(Bio.SeqIO.parse(handle, "fasta"))
        handle.close()
        thisseq = records[0].seq
        print 'Doing sequence ', thisseqname, 'length=', len(thisseq)
        
        for pwmf in pwmfiles:
            thispwmname = pwmf.split('/')[-1]
            thispwm = MOODS.load_matrix(pwmf)
            print ' Doing MOODS both strands for pwm ', thispwmname, ', length=', len(thispwm[0]), datetime.now()
            onestrandsindexvector = getMOODSscore(fastaf, pwmf, len(thisseq))
            print '  bp with no score (given ', NO_SCORE_VALUE,  ') is ', (onestrandsindexvector == NO_SCORE_VALUE).sum(), ' expected ', (len(thispwm[0])-1)
            print '  finding best score per bp, ', datetime.now()
            bestscorevector = getMaxPWMScore( onestrandsindexvector, len(thispwm[0])), 
            
            print '  writing wiggle for score per start index.', datetime.now()
            vegardswritewiggle(onestrandsindexvector[0,], name=thispwmname, chr=thisseqname, destpath=destdir + '/' + 'start_index_score/'+ thispwmname)
            
            print '  writing wiggle for bestscore. ', datetime.now()
            vegardswritewiggle(bestscorevector[0], name=thispwmname, chr=thisseqname, destpath=destdir + '/' + 'best_score_in_window/'+thispwmname)



        




pwmpath = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/matrix/JASPAR_CORE_2008'
pwmfiles =[f for f in os.listdir(pwmpath) if f.endswith('.pfm')]
pwmfiles = [pwmpath+ '/' + s for s in pwmfiles]

'''
###### for hg19.
fastafilepath = '/usit/invitro/hyperbrowser/standardizedTracks/hg19/Sequence/DNA'
fastafile = [f for f in os.listdir(fastafilepath) if f.endswith('.fa')]
fastafile = [fastafilepath+ '/' + s for s in fastafile]

#outputdir = '/usit/invitro/hyperbrowser/standardizedTracks/spombe2007/Trashcan/pwmtest'
outputdir = '/usit/invitro/hyperbrowser/standardizedTracks/hg19/Private/vegard/pwmtest'

print  datetime.now()
makePWMscorefiles(fastafile, pwmfiles[0:1], outputdir)
print  datetime.now()
'''

######### for spombe2007

fastafilepath ='/usit/invitro/hyperbrowser/standardizedTracks/spombe2007/Sequence/DNA'
fastafile = [f for f in os.listdir(fastafilepath) if f.endswith('.fa')]
fastafile = [fastafilepath+ '/' + s for s in fastafile]

#outputdir = '/usit/invitro/hyperbrowser/standardizedTracks/spombe2007/Trashcan/pwmtest'
outputdir = '/usit/invitro/hyperbrowser/standardizedTracks/spombe2007/Private/vegard/pwmtest3'

print  datetime.now()
makePWMscorefiles(fastafile, pwmfiles[0:2], outputdir)
print  datetime.now()




##########testing .......
#calculate_both_strands=True
#outputdir = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/tempoutput'


#fastafile=['/usit/invitro/hyperbrowser/standardizedTracks/hg19/Sequence/DNA/chr1.fa']
#pwmfiles=['/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm']

#fastaf = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/sequence/dnaRAND.txt'
#pwmf = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm'
#destdir = outputdir


#pwmfiles=['/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm', '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest1.pfm']

#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/string_in_ex1_as_fasta.txt'
#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/dummychrom.fasta'
#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/sequence/dnaRAND.txt'
#fastafile='/usit/invitro/hyperbrowser/standardizedTracks/hg19/Sequence/DNA/chr21.fa'

#### test av biopythons motif pakke med scanPWM

#matrix = MOODS.load_matrix('/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest_virker.pfm') #9

from Bio import Motif
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
from datetime import datetime

# Let's create an instance of the E2F1 motif (downloaded from the 
# jaspar database):
testpwm= '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest_virker.pfm'
motif=Motif.read(open(testpwm), "jaspar-pfm")

# the format method displays the motif in a variety of formats:
print motif.format('transfac')

fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/sequence/dnaRAND.txt'
fastafile='/usit/invitro/hyperbrowser/standardizedTracks/hg19/Sequence/DNA/chr1.fa'
handle = open(fastafile, "r")
records = list(Bio.SeqIO.parse(handle, "fasta", alphabet=IUPAC.unambiguous_dna))
handle.close()
thisseq = records[0].seq

print  datetime.now()
hits = motif.scanPWM(thisseq)
print  datetime.now()


print "ferdig i pwmtest4"