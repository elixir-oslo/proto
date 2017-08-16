#!/usr/bin/env python
"""
Adapted from bx/scripts/axt_to_fasta.py
"""
import rpy2.robjects as robjects
import sys


def main():
	
	# check the command line
	numObs = int(sys.argv[1])
	fileName = sys.argv[2]
	outFile = open(fileName, 'w')
	vector, dimensions, trueclust = GenerateDataset(numObs)
	numRowElems = int(dimensions[-1])
	tmpTab = []
	trueclust = [int(v) for v in trueclust]
	for index,val in enumerate(vector):
		if index>0 and index%numRowElems == 0:	
			print>>outFile, '\t'.join(tmpTab)
			tmpTab = []
		tmpTab.append(str(val))
		
		
	print>>outFile, dimensions
	outFile.write('Executing....')
	outFile.close()
	cFn = runCProgram(fileName)
	fileStr = evaluateResults(cFn, trueclust)
	outFile = open(fileName, 'a')
	print>>outFile, '\n\n'
	print>>outFile, fileStr
	
	#open(fileName, 'w').write(result)
	
# $$$ this should be moved to a bx.align.fasta module

def GenerateDataset(nObs):
	
	robjects.r('''generateDataset<-function(mu=6,s=1,s_s=1,s_n=0.1,lambda=10,d=50,nclust=5){
	require(MASS)
	n<-4*rpois(nclust,lambda)
	XX<-NULL
	trueclust<-rep(1:nclust,times=n)
	for (k in 1:nclust){
		sample.clust<-sample(1:4,d,replace=TRUE)
		m<-table(sample.clust)
		log.mu<-rnorm(4,mu,s)
		log.t<-NULL
		for (i in 1:4) log.t<-c(log.t,rnorm(m[i],log.mu[i],s_s))
		S_n<-diag(rep(s_n,length=d))
		X<-mvrnorm(n[k],log.t,S_n)
		XX<-rbind(X,XX)
	}
	return(list(x=as.numeric(XX),dimensions=c(nrow(XX),ncol(XX)), trueclust=trueclust))
}

res<-generateDataset()
x<-res$x
dimensions<-res$dimensions
trueclust<-res$trueclust''')
	
	vector = robjects.r("x")
	dimensions = robjects.r("dimensions")
	trueclust = robjects.r("trueclust")
	return vector, dimensions, trueclust #robjects.r("XX")

def runCProgram(vectorFn, prioFn=None, param1=1000, param2=2000, param3=100, param4=8, param5=100):
	#'/Users/trengere/Documents/jobb/Staale/resfile6.txt'
	return '/usit/invitro/data/hyperbrowser/hb_core_developer/trunk/galaxy_hb/tools/hyperbrowser/resfile6.txt'

	#from subprocess import call
	#call('testprog %s %s %i %i %i %i %i' %  (vectorFn, prioFn, param1, param2, param3, param4, param5))

def evaluateResults(cFileName, facitList):
	dim1, dim2 = 0, 0
	resultTab =[]
	clustRes = []
	for line in open(cFileName):
		linetab = [int(v) for v in line.strip().split()]
		resultTab+= linetab
		clustRes = linetab
		dim1+=1
		dim2 = len(linetab)
	#install.packages("mclust")\nlibrary(mclust)
	robjects.r('''require("mclust")\nlibrary(mclust)''')
	adjRandIndex = robjects.r('adjustedRandIndex')
	#res = adjRandIndex(robjects.IntVector(clustRes), robjects.IntVector(facitList))
	
	return repr(clustRes)
	
	#fileStr = open(cFileName).read()
	#return	fileStr

if __name__ == "__main__": main()

