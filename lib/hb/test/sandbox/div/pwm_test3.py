


# cd /usit/invitro/data/hyperbrowser/hb_core_developer/trunk    ##jeg klarer ikke kjoere herfra. Noe feil i oppsettet mitt som det var foer.
# python test/sandbox/div/pwm_test2.py
# python /usit/invitro/data/hyperbrowser/hb_core_developer/trunk/test/sandbox/div/pwm_test3.py


print "inne i pwmtest3"

import MOODS
import Bio.Seq
import Bio.SeqIO
#from numpy  import *
from datetime import datetime
import numpy as np
import os
import subprocess
#import gc


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
    

# seq, string eller Bio.Seq
# mat, pwm matrise
# return, array med score per basepar, -100 som score der MOODS ikke gir noe.
def getMOODSscore(seqfile, matfile):
    process = subprocess.Popen(['cat', '20linjer.txt'], shell=False, stdout=subprocess.PIPE)
    process.communicate()
    #results = MOODS.search(seq, [mat], thresholds=1, absolute_threshold=False)
    resarray = np.zeros( (1, len(seq)), dtype=np.dtype('Float32'))
    resarray[:,:] = -100
    
    testf = open('20linjer.txt', 'r')
    for position in testf:
        print 'pos=', position, 'score='
   
    
    #resarray = np.zeros( (1, len(seq)), dtype=np.dtype('Float32'))
    resarray = np.zeros( (1, 20), dtype=np.dtype('Float32'))

    resarray[:,:] = -100
    process = subprocess.Popen(['cat', '20linjer.txt'], shell=False, stdout=subprocess.PIPE)     
    for line in process.stdout:
        if len(line) > 1:
            (position, score) = line.split()
            print 'pos=', position, 'score=',score
            resarray[0, position] = score
        
        
        resarray[0, position] = score
    return(resarray)


# bpscores a array with scores per basepairposition
# bpscores, array med score per basepar, lengde 1 eller 2 (for motsatt strand.)
# windowlength, avstand forand bp som skal searches for maxvalue 
# returns, array with max value found for each bp.
def getMaxPWMScore(bpscores, windowlength):
    ret = bpscores.copy()
    for n in range(1,windowlength):
        #print n
        ret = np.concatenate((ret,bpscores),)
        startx=n*len(bpscores)
        stopx=startx+len(bpscores)
        ret[startx:stopx, n:] = bpscores[:,:len(bpscores[0,:])-n]
    return(np.max(ret, axis=0))
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


#
# fastafile, list of filename with sequences to be scored
# pmwfiles, list of filnames of the pwm files to be used on the sequences
# destdir, path to where the output will be writte, additional hierarchis beneath will be made.
# both_strands, should the pwm be matched on both strand (and best scored from both strand used in bp)
def makePWMscorefiles(fastafiles, pwmfiles, destdir, both_strands=True):
    for fastaf in fastafile:
        thisseqname = fastaf.split('/')[-1].split('.')[0]
        handle = open(fastaf, "r")
        records = list(Bio.SeqIO.parse(handle, "fasta"))
        handle.close()
        thisseq = records[0].seq
        print 'Doing sequence ', thisseqname, 'length=', len(thisseq)
        for pwmf in pwmfiles:
            thispwmname = pwmf.split('/')[-1]
            print ' Doing pwm ', thispwmname
            thispwm = MOODS.load_matrix(pwmf)
            thispwmcomplement = MOODS.reverse_complement(thispwm)
            
            print '  strand 1'
            onestrandindexvector=getMOODSscore(thisseq, thispwm)
            print '  strand 2'
            otherstrandindexvecor=getMOODSscore(thisseq, thispwmcomplement)
            print '  finding best score per bp'
            bothstrandsindexvector = np.append( onestrandindexvector, otherstrandindexvecor, axis=0)
            bestscorevector = getMaxPWMScore( bothstrandsindexvector, len(thispwm[0]))
            
            for strandnbr in range(len(bothstrandsindexvector)):
                print '  writing wiggle for strand', str(strandnbr)
                vegardswritewiggle(bothstrandsindexvector[strandnbr,:], name=thispwmname, chr=thisseqname, destpath=destdir + '/' + 'start_index_score/'+ thispwmname+ '/strand_'+str(strandnbr))
            
            print '  writing wiggle for bestscore'
            vegardswritewiggle(bestscorevector, name=thispwmname, chr=thisseqname, destpath=destdir + '/' + 'best_score_in_window/'+thispwmname)



        
#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/string_in_ex1_as_fasta.txt'
#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/dummychrom.fasta'
#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/sequence/dnaRAND.txt'
#fastafile='/usit/invitro/hyperbrowser/standardizedTracks/hg19/Sequence/DNA/chr21.fa'

pwmpath = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/matrix/JASPAR_CORE_2008'
pwmfiles =[f for f in os.listdir(pwmpath) if f.endswith('.pfm')]
pwmfiles = [pwmpath+ '/' + s for s in pwmfiles]
pwmfiles = pwmfiles[0:4]

fastafilepath ='/usit/invitro/hyperbrowser/standardizedTracks/spombe2007/Sequence/DNA'
fastafile = [f for f in os.listdir(fastafilepath) if f.endswith('.fa')]
fastafile = [fastafilepath+ '/' + s for s in fastafile]

outputdir = '/usit/invitro/hyperbrowser/standardizedTracks/spombe2007/Trashcan/pwmtest'


fastafile=['/usit/invitro/hyperbrowser/standardizedTracks/hg19/Sequence/DNA/chr1.fa']
pwmfiles=['/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm']

makePWMscorefiles(fastafile, pwmfiles, outputdir)

#calculate_both_strands=True
#outputdir = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/tempoutput'

#fastaf = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/string_in_ex1_as_fasta.txt'
#pwmf = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm'
#destdir = outputdir


#pwmfiles=['/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm', '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest1.pfm']

#seqname = fastafile.split('/')[-1].split('.')[0]




print "ferdig i pwmtest3"