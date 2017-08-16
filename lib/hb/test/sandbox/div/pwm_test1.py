


# cd /usit/invitro/data/hyperbrowser/hb_core_developer/trunk    ##jeg klarer ikke kjoere herfra. Noe feil i oppsettet mitt som det var foer.
# python test/sandbox/div/pwm_test1.py

print "inne i pwmtest1"

import MOODS
import Bio.Seq
import Bio.SeqIO

'''
matrix = [ [10,0,0],
           [0,10,0],
           [0,0,10],
           [10,10,10]]

teststring='actgtggcgtcaacgtaggccaacgtggacccgtacgtaaacgaagaggggtagtc'

#teststring = 'acgta'

matrix = [ [1,0,0,0],
           [0,1,1,0],
           [0,0,1,1],
           [1,1,0,1]]

matrix = [ [10,0,0,0],
           [0,10,10,0],
           [0,0,10,10],
           [10,10,0,10]]

matrix = [ [1,0,0,0],
           [0,1,0,0],
           [0,0,1,0],
           [0,0,0,1]]

teststring = 'acgtacgt'
'''

handle = open('/xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.fasta', "r")
records = list(Bio.SeqIO.parse(handle, "fasta"))
handle.close()
seq = records[0]
teststring=seq.seq




print('both strands')
results = MOODS.search(teststring, [matrix], thresholds=1, absolute_threshold=False, both_strands=True)

for i in results:
    for (position, score) in i:
        print("Position: " + str(position) + " Score: "+ str(score))
        
        
        
print('one way')
results = MOODS.search(teststring, [matrix], thresholds=1, absolute_threshold=False, both_strands=False)

for i in results:
    for (position, score) in i:
        print("Position: " + str(position) + " Score: "+ str(score))
        
        
print('other way')
results = MOODS.search(teststring, [  ,MOODS.reverse_complement(matrix)], thresholds=1, absolute_threshold=False, both_strands=False)

results = MOODS.search(teststring, [  matrix , matrix], thresholds=1, absolute_threshold=False, both_strands=False)

MOODS.search(teststring, [  matrix ], thresholds=1, absolute_threshold=False, both_strands=True)

for i in results:
    for (position, score) in i:
        print("Position: " + str(position) + " Score: "+ str(score))

       


        
#  /xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/MOODS/src/find_pssm_dna 1 -algorithm=naive /xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.fasta /xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm


#  /xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/MOODS/src/find_pssm_dna 1 /xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.fasta /xanadu/home/vegardny/prosjekter/hyperbrowser/pwm_vs_snp/vegard_debug_MOODS/examples/vegardtest2.pfm
   
   
   
       
        



















print "ferdig i pwmtest1"