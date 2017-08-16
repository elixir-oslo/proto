

print "inne i vegardtest2"

import rpy2
import rpy2.robjects as robjects



#loade library i R
x=robjects.r('''
library(hgu133plus2.db)
        ''')


probes = ['212017_at', '214253_s_at', '1556666_a_at', '1554469_at', '226145_s_at'] # eksempel prober
probes = robjects.StrVector(probes)
runlist = robjects.r['unlist']
rmget = robjects.r['mget']
syms = runlist(rmget(probes, robjects.r['hgu133plus2SYMBOL'])) # sikkert flere maater aa gjoere dette.



### skrive ut resultat
count=0
print "AffyID\tSymbol"
for affyid in probes:
    print affyid + "\t" + syms[count]
    count=count+1
    


"""
library(hgu133plus2.db)
probes = c('212017_at', '214253_s_at', '1556666_a_at', '1554469_at', '226145_s_at')
syms = unlist(mget(probes, hgu133plus2SYMBOL))

library(hgu133plus2.db)
probes = c('212017_at', 'tull')
syms = unlist(mget(probes, hgu133plus2SYMBOL, ifnotfound=NA))
syms[is.na(syms)]=names(syms[is.na(syms)])

syms = unlist(mget(c('236322_at'), hgu133plus2ENSEMBL, ifnotfound=NA))

dim(hgu133plus2SYMBOL)
multi <- toggleProbes(hgu133plus2SYMBOL, "all")
dim(multi)

mget(c('236322_at'), hgu133plus2ENSEMBL)

236322_at
"""
"""
#installere libraries. Vet ikk hvor de havnet.
x=robjects.r('''
source("http://www.bioconductor.org/biocLite.R")
biocLite(c("hgu133plus2.db", "AnnotationDbi", "Biobase", "org.Hs.eg.db", "DBI"))

        ''')

print x

"""
"""
from gold.description.TrackInfo import TrackInfo
genome="hg18"
tn = ['Private', 'Vegard', 'test', 'test1']

ti = TrackInfo(genome, tn)
print(ti.getUIRepr())
"""



print "ferdig"