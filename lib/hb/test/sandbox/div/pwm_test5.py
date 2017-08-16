


# cd /usit/invitro/data/hyperbrowser/hb_core_developer/trunk   
# python test/sandbox/div/pwm_test4.py
# time  python /usit/invitro/data/hyperbrowser/hb_core_developer/trunk/test/sandbox/div/pwm_test4.py


print "inne i pwmtest5"
from datetime import datetime
import numpy as np
import os
import subprocess
from Bio import Motif
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
import Bio.Seq
import Bio.SeqIO
import Bio.Motif

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
    return np.nanmax(ret, axis=0)
       

# Short helper function to make a wiggle file for the pwm scores. Scores formated to 2 decimals.
# thisvector, list with values, one for each bp
# name, name of the track, put in wiggle header.
# chr, put in wiggle header and used as filename + .wig
# path, where file will be made
def vegardswritewiggle(thisvector, name, chr, destpath):
    thisdir = destpath 
    if not os.path.exists(thisdir):
        os.makedirs(thisdir)
    # need .dat.wig to be recognized by hb?
    thispath=thisdir+'/'+chr+'.dat.wig' #
    outfile = open(thispath, 'w')
    outfile.write('track type=wiggle_0 name='+name+'\n')
    outfile.write('fixedStep\tchrom='+chr+'\tstart=1\tstep=1\n')
    for val in thisvector:
        outfile.write('%0.2f\n' % val)
    outfile.close()



#
# fastafile, list of filename with sequences to be scored
# pmwfiles, list of filnames of the pwm files to be used on the sequences
# destdir, path to where the output will be writte, additional hierarchis beneath will be made.
# both_strands, should the pwm be matched on both strand (and best scored from both strand used in bp)
def makePWMscorefiles(fastafiles, pwmfiles, destdir, both_strands=True):
    for fastaf in fastafile:
        ### seqence only needed for length here. MOODS does this parsing again later but without reporting length.
        thisseqname = fastaf.split('/')[-1].split('.')[0]
        thisseq = Bio.SeqIO.read(fastaf, "fasta", alphabet=IUPAC.unambiguous_dna)
        #thisseq = Bio.SeqIO.parse(thisseqname, "fasta", alphabet=IUPAC.unambiguous_dna)
        print 'Doing sequence ', thisseqname, 'length=', len(thisseq)
        
        for pwmf in pwmfiles:
            thispwmname = pwmf.split('/')[-1]
            thispwm = Motif.read(open(pwmf), "jaspar-pfm")
            print ' Doing scanPWM one strands for pwm ', thispwmname, ', length=', len(thispwm[0]), datetime.now()
            onestrandsindexvector = thispwm.scanPWM(thisseq.seq)
            x = onestrandsindexvector[0:len(thispwm)-1].copy() # adding missing bp-values on the end to get the same length as seq.
            x[:]=np.NAN
            onestrandsindexvector=np.append(onestrandsindexvector, x)
            onestrandsindexvector = np.array([onestrandsindexvector]) # takes long time.
            print '  bp with nan score  is ', np.isnan(onestrandsindexvector).sum(), ' expected ', (len(thispwm)-1)
            print '  finding best score per bp, ', datetime.now()
            bestscorevector = getMaxPWMScore( onestrandsindexvector, len(thispwm)) 
            
            print '  writing wiggle for score per start index.', datetime.now()
            vegardswritewiggle(onestrandsindexvector[0,], name=thispwmname, chr=thisseqname, destpath=destdir + '/' + 'start_index_score/'+ thispwmname)
            
            print '  writing wiggle for bestscore. ', datetime.now()
            vegardswritewiggle(bestscorevector, name=thispwmname, chr=thisseqname, destpath=destdir + '/' + 'best_score_in_window/'+thispwmname)



        




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
outputdir = '/usit/invitro/hyperbrowser/standardizedTracks/spombe2007/Private/vegard/pwmtest4'

print  datetime.now()
makePWMscorefiles(fastafile[0:1], pwmfiles[0:1], outputdir)
print  datetime.now()




##########testing .......
#calculate_both_strands=True
#outputdir = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/tempoutput'


#fastafile=['/usit/invitro/hyperbrowser/standardizedTracks/hg19/Sequence/DNA/chr1.fa']
#pwmfiles=['/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm']

#fastaf = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/sequence/dnaRAND.txt'

fastaf = '/usit/invitro/hyperbrowser/standardizedTracks/spombe2007/Sequence/DNA/chr1.fa'
#fastaf = ''
#pwmf = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm'
pwmf = '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/matrix/JASPAR_CORE_2008/MA0086.pwf' 
destdir = outputdir



jaspar_file='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/JASPAR/all_data/matrix_only/matrix_only.txt'
thispwm = Motif.read(open(jaspar_file), "jaspar-pfm")

#pwmfiles=['/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm', '/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest1.pfm']

#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/string_in_ex1_as_fasta.txt'
#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/dummychrom.fasta'
#fastafile='/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/data/sequence/dnaRAND.txt'
#fastafile='/usit/invitro/hyperbrowser/standardizedTracks/hg19/Sequence/DNA/chr21.fa'

#### test av biopythons motif pakke med scanPWM



print "ferdig i pwmtest4"