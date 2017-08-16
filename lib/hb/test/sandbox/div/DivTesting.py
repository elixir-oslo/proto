#from gold.util.CommonFunctions import repackageException
#
#@repackageException(Exception,RuntimeError)
#def test():
#    raise OSError
#
#try:
#    test()
#except RuntimeError, e:
#    print e
#from quick.util.CommonFunctions import silenceRWarnings

#for i in range(500):
#    print i
#    silenceRWarnings()

#pvalFile = open('/Users/sandve/Desktop/pvals.txt')
#pvals = []
#
#for lineNum,line in enumerate(pvalFile):
#    if lineNum<6:
#        continue
#    pvals.extend(line.split()[4:])
#    #pvals.extend([float(x) for x in line.split()[4:] ])
#    
#print len(pvals)
#
##from proto.RSetup import r
#open('/Users/sandve/Desktop/pvalsToR.txt','w').write('\n'.join(pvals))
#r.hist(pvals,breaks=100)
for week in range(7,10):
    print '====== Uke %i ======' % week
    for stud in 'Eirik,Eivind,Hiep,Jonathan,Oyvind'.split(','):
        print '===== %s =====' % stud
        for x in ['Budsjett','Regnskap']:
            print '==== %s ====' %x
            for y in ['Synlig','Usynlig']:
                print '== %s: ==' %y
