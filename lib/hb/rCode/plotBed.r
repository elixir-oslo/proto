
#Get bed.file on required format:
plot.bed <- function(file,data.unit="bp"){
	bed.data <- read.table(file,header=F,na.strings="nan",skip=1)
	
	#Remove any rows with missing values:
	if(any(is.na(bed.data))){
		na.row <- which(is.na(bed.data),arr.ind=TRUE)[,1]
		bed.data <- bed.data[-na.row,,drop=FALSE]
	}
	
	nseg <- nrow(bed.data)

	#Extract numeric chrom.numbers and convert to arm numbers:
	chrom <- get.chromnumbers(chrom.names=bed.data[,1])
	arms <- getArms(position=bed.data[,3],chromosomes=chrom,unit=data.unit)

	sampleid <- rep("",nseg)
	npos <- rep("",nseg)
	
	segments <- as.data.frame(cbind(I(sampleid),arms,bed.data[2:3],I(npos),bed.data[,4]),stringsAsFactors=FALSE)
	
	colnames(segments) <- c("SampleID","Arm","Start.pos","End.pos","nPos","Mean")

	return(segments)
}

get.chromnumbers <- function(chrom.names){
	chrom.names <- as.character(chrom.names)
	chrom.numbers <- sub("chr","",chrom.names)   #Remove "chr"

	#Replace X and Y by numbers 23 and 24:
	ind.X <- which(chrom.numbers=="X")
	ind.Y <- which(chrom.numbers=="Y")
	chrom.numbers[ind.X] <- 23
	chrom.numbers[ind.Y] <- 24

	chrom.numbers <- as.numeric(chrom.numbers)
	
	return(chrom.numbers)

}


getArms <- function(position,chromosomes,unit){
	#Vector that give the stop position of p-arms:
	armStop <- c(124300000,93300000,91700000,50700000,47700000,60500000,59100000,45200000,
		51800000,40300000,52900000,35400000,16000000,15600000,17000000,38200000,22200000,
		16100000,28500000,27100000,12300000,11800000,59500000,11300000)
	#Vector that gives the stop position of each chromosome (and hence also the stop of the q-arm):
	chromStop <- c(247249719, 242951149, 199501827,191273063,180857866,170899992,158821424,146274826,
		140273252,135374737,134452384,132349534,114142980,106368585,100338915,88827254,
		78774742,76117153,63811651,62435964,46944323,49691432,154913754,57772954)

	#nArm <- length(armStop)
	units <- c("bp","kbp","mbp")
	if(all(units!=unit)){
		stop(paste("unit must match one of",deparse(units[1]),",",deparse(units[2]),"or",deparse(units[3]),sep=" "))
	}else{
		if(unit=="kbp"){
			position <- position*1000
		}else{
			if(unit=="mbp"){
				position <- position*1000000
			}
		}
	}

	chrom.list <- unique(chromosomes)
	nChrom <- length(chrom.list)
		
	arms <- rep(NA,length(chromosomes))
	for(k in 1:nChrom){
		ind.k <- which(chromosomes==chrom.list[k])
		pos.k <- position[ind.k] 
		arms[ind.k] <- chrom.list[k]*2  #all arms in chrom. k	
		ind.p <- ind.k[pos.k <= armStop[chrom.list[k]]]  #indeces of probes in p-arm
		arms[ind.p] <- chrom.list[k]*2-1   #p-arm 			
	}#endfor

	return(arms)
}