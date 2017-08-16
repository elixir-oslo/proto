import os
from quick.util.GenomeInfo import GenomeInfo

class OrigFormatConverter:
    @staticmethod
    def wigVariableStepWithSpanToBedGraph(myFile, outFile):
        fileIn = open(myFile)
        fileOut = open(outFile, 'w')
        
        for i,line in enumerate(fileIn):
            
            if i == 0:
                fileOut.write( line.replace('wiggle_0', 'bedGraph'))
            
            if i > 0:
                
                cols = line.split()
            
                if len(cols) == 3:
                    chrom = cols[1].split("=")[1]
                    span = int(cols[2].split("=")[1])
                
                    #chrom, span = [cols[i].split("=")[1] for i in [1,2]]
                
                if len(cols) == 2:
                    chromStart = int(cols[0]) - 1
                    dataVal = cols[1]
                    chromEnd = chromStart + span
            
                    fileOut.write( '\t'.join([chrom, str(chromStart), str(chromEnd), dataVal]) + '\n' )
        
    @staticmethod            
    def convertBedGraphToWigVStepFillingGaps(fn, outFn, gapValue):
        lastChr = "chr0"        #initiate variable "lastChr"
        newWigList = [["track type=wiggle_0"]]        #create list of lists to hold new gap filled wig variable step format
       # oldStop = 1         # needed to fill the first gap
              
        for line in open(fn):
            cols = line.split()
            if cols[0] != "track":
                newStartCoord = int(cols[1]) + 1
                newStopCoord = int(cols[2]) + 1
                if cols[0] == lastChr:          #if same chromosome as last time
                    if cols[1] != oldStop: #if gap 
                        zeroSeg=[str(int(oldStop)+1),gapValue]
                        newWigList.append(zeroSeg)
                        newWigList.append([str(newStartCoord),str(cols[3])])
                        oldStop = cols[2]
                    else:     #if no gap          
                        newWigList.append([str(newStartCoord),str(cols[3])])
                        oldStop = cols[2]
                    lastChr = cols[0]
                else:       #if new chromosome
                    oldStop = 0 
                    newWigList.append(["variableStep chrom="+str(cols[0])])# add header
                    if cols[1] != oldStop: #if gap 
                        zeroSeg=[str(int(oldStop)+1),gapValue]
                        newWigList.append(zeroSeg)
                        newWigList.append([str(newStartCoord),str(cols[3])])
                        oldStop = cols[2]
                    else:     #if no gap          
                        newWigList.append([str(newStartCoord),str(cols[3])])
                        oldStop = cols[2]
                    lastChr = cols[0]
        #print newWigList
        ut = open(outFn,"w")
        for index in range(len(newWigList)):
            ut.write("\t".join(newWigList[index])+"\n")
        ut.close()


    @staticmethod
    def filterMarkedSegments(inputfile, outputfile, criterionfunction, genomebuild="hg18"):        
        import sys
        f = open(inputfile, 'r') 
        header = f.readline()
        a=f.readline().split()
        if(len(a)==4):
            OrigFormatConverter.filterMarkedSegmentsBED(inputfile, outputfile, criterionfunction)
        elif(len(a)==2):
            OrigFormatConverter.filterMarkedSegmentsVariableStep(inputfile, outputfile, criterionfunction, genomebuild)
        else:
            sys.stderr.write("Not able to parse format, must be BED as 'Chr'\t'start'\t'stop'\t'value'\nor variablestepFormat, 'start'\t'value'")
        return    
    
    @staticmethod    
    def filterMarkedSegmentsBED(inputfile, outputfile, criterionfunction):
        import os
        import sys    
        f = open(inputfile, 'r')    
        out = open(outputfile, 'w')    
        header = f.readline()
        if header.find("type") == -1: #no header.
            f = open(inputfile, 'r')    
        else:
            out.write(header)    
        for line in f:                
            value = line.split()[3]
            if criterionfunction(float(value)):
                    out.write(line)
        return


        
    @staticmethod
    def filterMarkedSegmentsVariableStep(inputfile, outputfile, criterionfunction, genomebuild="hg18"):        
        #import os
        #print( os.getcwd())
        f = open(inputfile, 'r')    
        out = open(outputfile, 'w')
        chrom="notset"
        lastchrom="notset"
        laststart="notset"
        lastvalue=0
        value = -1
        header = f.readline()
        
        for line in f:
            if line.find("chrom=") != -1: # a chrom def line.
                chrom = line.partition("chrom=")[2].strip()
                if(lastchrom != "notset"):
                    #stop = str(GenomeInfo.getChrLen(GenomeInfo.getChrList(genomebuild), genomebuild, lastchrom))#feil
                    stop=str(OrigFormatConverter.dummygetChromosomlength(genomebuild, lastchrom))
                start = "notset"
                #print "fant chrom!" + chrom
            else:
                start=line.partition("\t")[0]
                value=line.partition("\t")[2].strip()
                stop = start
            if laststart != "notset":
                try:
                    lastvalue = float(lastvalue)
                    if criterionfunction(int(lastvalue)):
                        out.write(lastchrom+"\t"+laststart+"\t"+stop+"\t"+str(lastvalue)+"\n")                    
                except ValueError:
                    #print("Segment excluded, not a number:"+str(lastvalue))
                    tull=0 # do nothing
            laststart=start
            lastvalue=value
            lastchrom=chrom
        
        #last variable step in chromsome, no stop is in the file. Get from genomeinfo.    
        try:
            if laststart != "notset":
                lastvalue = float(lastvalue)    
                if criterionfunction(int(lastvalue)):
                    #stop=str(GenomeInfo.getChrLen(GenomeInfo.getChrList(genomebuild), genomebuild, lastchrom))#feil
                    stop=str(OrigFormatConverter.dummygetChromosomlength(genomebuild, lastchrom))
                    out.write(lastchrom+"\t"+laststart+"\t"+str(stop)+"\t"+str(lastvalue)+"\n")
        except ValueError:
            #print("Segment excluded, not a number:"+str(lastvalue))
            tull=0 # do nothing
            return

    #dummy function. Skal vaere den ekte funksjonen for aa faa chromlength
    @staticmethod
    def dummygetChromosomlength(a,b):
        return GenomeInfo.getChrLen(a,b)

    
    @staticmethod
    def filterSegmentsByLength(inFn, outFn, criteria):
        outF = open(outFn,'w')
        for line in open(inFn):
            cols = line.split()
            length = int(cols[2]) - int(cols[1])
            if criteria(length):
                outF.write(line)


    @staticmethod
    def segments2points(inputfile, outputfile, point_to_use):
        import os
        import sys
        print( os.getcwd())
        f = open(inputfile, 'r')    
        out = open(outputfile, 'w')    
        header = f.readline()
        if header.find("type") == -1: #no header.
            f = open(inputfile, 'r')
        else:
            out.write(header)
        pointfunc=lambda x,y:(0)
        if point_to_use=="start":
            pointfunc=lambda x,y: (x)
        elif  point_to_use=="stop":
            pointfunc=lambda x,y: (y)
        elif  point_to_use=="mid":
            pointfunc=lambda x,y: ((x+y)/2)
        else:
            sys.stderr.write("point_to_use must be {'start', 'stop', 'mid'}")
            return
    
        for line in f:
            chrom = line.split()[0]
            start = int(line.split()[1])
            stop = int(line.split()[2])
            value = line.split()[3]
            newstart = pointfunc(start,stop)
            newstop = newstart +1 
            out.write(chrom+"\t"+str(newstart)+"\t"+str(newstop)+"\t"+value+"\n")
    
    #print("ferdig")
        return
    
    
    
    
