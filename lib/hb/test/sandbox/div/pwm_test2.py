


# cd /usit/invitro/data/hyperbrowser/hb_core_developer/trunk    ##jeg klarer ikke kjoere herfra. Noe feil i oppsettet mitt som det var foer.
# python test/sandbox/div/pwm_test2.py
# python /usit/invitro/data/hyperbrowser/hb_core_developer/trunk/test/sandbox/div/pwm_test2.py


print "inne i pwmtest2"

import MOODS
import Bio.Seq
import Bio.SeqIO
#from numpy  import *
from datetime import datetime
import numpy as np
import os
#import gc


#funksjon som lager track med score for pwm match. Returnerer array med en verdi per basepar basert paa MOODS algo.
# input
# seqfile= path til fastafile med sekvens
# pwmfile=path til pwm fil


def getMOODSscore(seqfile, pwmfiles, both_strands=False):
    handle = open(seqfile, "r")
    records = list(Bio.SeqIO.parse(handle, "fasta"))
    handle.close()
    seq = records[0].seq
    print 'len(seq)=',len(seq)
    matrixlist=list()
    for f in pwmfiles:
        matrix = MOODS.load_matrix(f)
        print 'pwm ', f , 'windowlength=', len(matrix[0])
        matrixlist.append(matrix)
        if both_strands:
            matrixlist.append(MOODS.reverse_complement(matrix)) # both_strand option in MOODS returned a akward result.
    print 'starting MOODS.search', datetime.now()
    results = MOODS.search(seq, matrixlist, thresholds=1, absolute_threshold=False)
    print 'done MOODS.search', datetime.now()
    reslist=[]
    for n in range(len(pwmfiles)):
        thisind = n * (1 + both_strands)
        
        reslist.append(vegardparseMOODSres( results[thisind] , len(seq)))
        if both_strands:
            reslist[n] = np.append( reslist[n] , vegardparseMOODSres( results[thisind+1] , len(seq)), axis=0)
    return(reslist)



#m=results[thisind]
#l= len(seq)
def vegardparseMOODSres(m,l):
    resarray = np.zeros( (1, l), dtype=np.dtype('Float32'))
    resarray[:,:] = -100
    for (position, score) in m:
        resarray[0, position] = score
    return(resarray)
 

#bpscores a array with scores per basepairposition
#windowlength, length in downindex-direction to search for highest score.,
#returns a vector of same length with the max score per bp within windowlength
#
# Replicates array and shiftsvalues to the right, windowlengt times, and returns maxvalue per column.
def getMaxPWMScore(bpscores, windowlength):
    ret = bpscores.copy()
    for n in range(1,windowlength):
        #print n
        ret = np.concatenate((ret,bpscores),)
        startx=n*len(bpscores)
        stopx=startx+len(bpscores)
        ret[startx:stopx, n:] = bpscores[:,:len(bpscores[0,:])-n]
    #return(np.max(ret, axis=0))
    return(ret)        


def vegardswritewiggle(thisvector, name, chr, path):
    thisdir = path 
    if not os.path.exists(thisdir):
        os.makedirs(thisdir)
    thispath=thisdir+'/'+chr+'.wig'
    outfile = open(thispath, 'w')
    outfile.write('track type=wiggle_0 name='+name+'\n')
    outfile.write('fixedStep\tchrom='+chr+'\tstart=1\tstep=1\n')
    for val in thisvector:
        #print val
        #outfile.write(str(val)+'\n')
        outfile.write('%0.2f\n' % val)
    outfile.close()
#"%0.2f" % i 

#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/string_in_ex1_as_fasta.txt'
#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/dummychrom.fasta'
#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/sequence/dnaRAND.txt'
fastafile='/usit/invitro/hyperbrowser/standardizedTracks/hg19/Sequence/DNA/chr21.fa'

pwmpath = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/matrix/JASPAR_CORE_2008'
pwmfiles =[f for f in os.listdir(pwmpath) if f.endswith('.pfm')]
pwmfiles = [pwmpath+ '/' + s for s in pwmfiles]
pwmfiles = pwmfiles[0:1]


#pwmfiles=['/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm', '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest1.pfm']

seqname = fastafile.split('/')[-1].split('.')[0]
outputdir = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/tempoutput'
calculate_both_strands=True

####### running MOODS algorithm on sequence with all pwm files.
#datetime.now()
print 'running getMOODSscore', datetime.now()
indexscorematrix = getMOODSscore(fastafile, pwmfiles, both_strands=calculate_both_strands)
print 'finished getMOODSscore', datetime.now()
#datetime.now()

## for alle pwm.
## lage max array
## skrive ut 3 filer.
for n in range(len(pwmfiles)):
    thisname = pwmfiles[n].split('/')[-1]
    print 'making maxscpre for ',thisname, datetime.now()
    thisscorematrix = indexscorematrix[n] #
    thispwmlength = len(MOODS.load_matrix(pwmfiles[n])[0])
    thismaxvector = getMaxPWMScore(thisscorematrix, thispwmlength)
    
    print 'writing wiggle for ',thisname, datetime.now()
    ### best score file
    vegardswritewiggle(thismaxvector, name=thisname, chr=seqname, path=outputdir + '/' + 'best_score_in_window/'+thisname)
    for strandnbr in range(len(thisscorematrix)):
        vegardswritewiggle(thisscorematrix[strandnbr,:], name=thisname, chr=seqname, path=outputdir + '/' + 'start_index_score/'+ thisname+ '/strand_'+str(strandnbr))
    



temp1 = getMaxPWMScore(temp1, thispwmlength)

    





print "ferdig i pwmtest2"