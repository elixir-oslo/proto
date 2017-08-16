
#Function to plot observed copy number estimates and/or segmentation result for one given sample with a separate figure for each chromosome

#Version: 08.10.2009

#Author: Gro Nilsen

plot.chrom <- function(data=NULL,segments=NULL,winsoutliers=NULL,sampleID=NULL, chrom=NULL,xaxis="pos",unit=NULL,layout=c(1,1),dir.print=NULL,plot.ideo=FALSE,cytoband=NULL,segments2=NULL,...){

	#Check that data and/or segments is specified by user
	if(!is.null(data)||!is.null(segments)){
	
		#First extract relevant information from input data:
		if(!is.null(data)){
			
			#Check data, sampleid, and extract data:
			ext.data <- extractFromData(data,chrom,sampleID,winsoutliers,type="chrom")
			arm <- ext.data$arm
			position <- ext.data$position
			y <- ext.data$y
			winsoutliers <- ext.data$winsoutliers
			sampleID <- ext.data$sampleID
		}#endif
		
		
		
		#Then extract relevant information from input segments:
		if(!is.null(segments)){
			#Check segments, sampleID and extract
			ext.seg <- extractFromSegments(segments,chrom=chrom,sampleID=sampleID,type="chrom")
			segments <- ext.seg$segments
	
			#If data was not specified, we need to use arms and possibly sampleid from segments:
			if(is.null(data)){
				arm <- ext.seg$arm
				sampleID <- ext.seg$sampleID
			}
			
			#If a second segmentation has been given as input; need to extract info from this as well:
			if(!is.null(segments2)){
				ext.seg2 <- extractFromSegments(segments=segments2,chrom=chrom,sampleID=sampleID,type="chrom")
				segments2 <- ext.seg2$segments
			}
					
		}
		
		#Plot layout (number of columns and rows in plot grid) specified by user:	
		nr <- layout[1]
		nc <- layout[2]	
		
		
		#Set default plot parameters and change these if user has specified other choices via ... :
		arg <- getPlotParameters(type="chrom",nc=nc,sampleID=sampleID,...)
		
		#Margins used for the plot window:
		if(arg$title==""){
			oma <- c(0,0,0,0)
		}else{
			oma <- c(0,0,1,0)
		}
		
		mar=c(0.2,0.2,0.3,0.2)
		
		
		
		#Either print to file, or plot on screen
		if(!is.null(dir.print)){
			pdf(file=paste(dir.print,"/",arg$title,".pdf",sep=""),width=11.6,height=8.2, onefile=TRUE,paper="a4r")  #a4-paper 
		}else{
			windows(width=11.8,height=8.2,record=TRUE)
		}

		
		#Retrieve chromosome number from arm numbers:
		if(is.null(chrom)){
			chrom <- getChrom(unique(arm))
			chrom.list <- unique(chrom)
		}else{
			chrom.list <- chrom
		}
		nChrom <- length(chrom.list)
		
		#Initialize row and column index:
		row=1
		clm=1
		new = FALSE
		
		#Divide the plotting window by the function "framedim":
		frames <- framedim(nr,nc)
		
		#Make separate plots for each chromosome:
		
		for(c in 1:nChrom){ 
		
			#Select relevant chromosome number
			k <- chrom.list[c] 			
			
			#Print chromosome number to screen:
			#cat("chrom:",k,"\n")
			
			#Frame dimensions for plot c:
			fig.c <- c(frames$left[clm],frames$right[clm],frames$bot[row],frames$top[row])
			par(fig=fig.c,new=new,oma=oma,mar=mar)
			frame.c <- list(left=frames$left[clm],right=frames$right[clm],bot=frames$bot[row],top=frames$top[row])
	
			#Plotting			
			if(is.null(segments)){
				#Only plot observed data:
				
				#Get index for probes within the chromosome:
				index.k <- getChromIndex(k=k,arm=arm)
				plotObs(y,k=k,index=index.k,winsoutliers,xaxis,position,type="chrom",plot.ideo=plot.ideo,cytoband=cytoband,frame=frame.c,new=new,pos.unit=unit,op=arg)
					

			}else{
				if(is.null(data)){
					#Only plot segments
					
					#Get y-limits for segments2 to insure that these are included in plot:
					seg2.lim <- NULL
					if(!is.null(segments2)){
						seg2.lim <- get.seglim(segments2,arg$equalRange,k=k)
					}#endif

					#Plot segments:
					plotSegments(segments,type="chrom",k=k,xaxis=xaxis,plot.ideo=plot.ideo,cytoband=cytoband,add=FALSE,col=arg$seg.col[1],lty=arg$seg.lty[1],lwd=arg$seg.lwd[1],
						frame=frame.c,new=new,pos.unit=unit,seg2.lim=seg2.lim,op=arg)
						
					if(!is.null(segments2)){
						#Plot segments2 on top (e.g. results from Multipcf)
						plotSegments(segments2,type="chrom",k=k,xaxis=xaxis,add=TRUE,col=arg$seg.col[2],lty=arg$seg.lty[2],lwd=arg$seg.lwd[2],pos.unit=unit,op=arg)
					}#endif

				}else{
					#Plot both data and segments
					seg.lim <- get.seglim(segments,arg$equalRange,k=k)
					if(!is.null(segments2)){
						seg2.lim <- get.seglim(segments2,arg$equalRange,k=k)
						seg.lim[1] <- min(seg.lim[1],seg2.lim[1])
						seg.lim[2] <- max(seg.lim[2],seg2.lim[2])
					}
					
					
					#Get the index of probes within chromosome k:
					index.k <- getChromIndex(k=k,arm=arm)
					plotObs(y,k=k,index=index.k,winsoutliers,xaxis,position,type="chrom",plot.ideo=plot.ideo,cytoband=cytoband,frame=frame.c,new=new,pos.unit=unit,seg.lim=seg.lim,op=arg)

					
					plotSegments(segments,type="chrom",k=k,xaxis=xaxis,add=TRUE,col=arg$seg.col[1],lty=arg$seg.lty[1],lwd=arg$seg.lwd[1],pos.unit=unit,op=arg)

					if(!is.null(segments2)){
						#Plot segments2 on top (e.g. results from Multipcf)
						plotSegments(segments2,type="chrom",k=k,xaxis=xaxis,add=TRUE,col=arg$seg.col[2],lty=arg$seg.lty[2],lwd=arg$seg.lwd[2],pos.unit=unit,op=arg)
					}

				}#endif

			}#endif

			
			#If page is full; plot on new page
			if(c%%(nr*nc)==0){
				#Add main title to page:
				title(arg$title,outer=TRUE)
				
				#Start new page when prompted by user:
				if(is.null(dir.print)){
					devAskNewPage(ask = TRUE)   #Does not work in R 2.5.1..
				}
				
				#Reset columns and row in layout:
				clm = 1
				row = 1
				new=FALSE
				
			}else{
				#Update column and row index:
				if(clm<nc){
					clm <- clm+1
				}else{
					clm <- 1
					row <- row+1
				}#endif
				new=TRUE
			}#endif
				
			
		}#endfor

		#Plot sampleid as title
		title(arg$title,outer=TRUE)
		
		#Close plot	
		if(!is.null(dir.print)){
			graphics.off()
		}
		
	}else{
		stop(paste("One of the arguments",deparse(quote("data")),"and",deparse(quote("segments")),"must be specified!",sep=" "))
	}
}#endfunction



#Help functions:

#Function that plots estimated copy numbers for one sample:

plotObs <- function(y,k=NULL,index,winsoutliers,xaxis,position,type,chromosomes=NULL,plot.ideo=FALSE,cytoband=NULL,frame=NULL,new=FALSE,pos.unit,print.xwarn=TRUE,seg.lim=NULL,op){

	#Pick out relevant data:
	if(type=="genome"){
		#Get data for sample i
		use.y <- y[,index]
		sampleID <- colnames(y)[index]
		if(is.null(op$main)){
			op$main <- sampleID
		}
	}
	if(type=="sample"){
		#Get data for sample i
		use.y <- y[,index]
		sampleID <- colnames(y)[index]
		if(is.null(op$main)){
			op$main <- sampleID
		}
	}
	if(type=="chrom"){
		#Pick out data for probes in chromosome k:
		use.y <- y[index]
		if(is.null(op$main)){
			op$main=paste("Chromosome",k,sep=" ")
		}
	}#endif
		
			
	n.k <- length(use.y)
	
	#Pick out what should be plotted on x-axis (position or index)
	if(xaxis=="pos"){
		if(type=="genome"){
			#Convert to global position:
			#global.position <- convertToGlobalPos(position,chrom=chromosomes) 
			global.position <- getGlobPos(position,chromosomes,unit=pos.unit)
			x <- global.position
		}
		if(type=="sample"){
			x <- position
		}
		if(type=="chrom"){
			x <- position[index]
		}
		
	}else{
		if(xaxis=="index"){
			if(type=="genome"||type=="sample"){
				x <- 1:length(position)
				
			}
			if(type=="chrom"){
				x <- 1:length(position[index])
			}
		}else{
			stop(paste("Invalid xaxis option:",xaxis,sep=" "),call.=FALSE)
		}
	}
	

	
	#x-axis parameters:
	if(xaxis=="pos"){
		#Want to scale the x-axis to fit the desired unit given in plot.unit (default is mega base pairs)
		if(!is.null(pos.unit)){
			scale.fac <- convert.unit(unit1=op$plot.unit,unit2=pos.unit)
			x <- x*scale.fac
			xmax <- max(x)
			
		}else{
			stop(paste("Argument",deparse(quote("unit")),"is missing, with no default.",sep=" "))
		}
	}
	
	#Plot ideogram at bottom of plot (not if xaxis=index):
	
	
	
	if(plot.ideo && xaxis=="pos"){
		#Ideogram-plot dimensions:
		if(is.na(op$ideo.frac)){
			#ideo.frac has not been defined by user:
			op$ideo.frac <- (1/25)*1/op$f
			if(op$cyto.text){
				#Need larger margins for ideogram:
				op$ideo.frac <- (1.5+ncol*0.5)*op$ideo.frac  
			}
		}
		#Ideogram frame:
		ileft <- frame$left
		iright <- frame$right
		ibot <- frame$bot
		itop <- frame$bot + (frame$top-frame$bot)*op$ideo.frac						
		figi <- c(ileft,iright,ibot,itop)

		mar.i <- c(0.2*op$f,4*op$f,0,1*op$f)
		if(op$cyto.text){
			#Need to increase bottom margin:
			mar.i <- mar.i + c(2,0,0,0)
		}	
		
		#Plot ideogram and get maximum probe position in ideogram:
		par(fig=figi,new=new,mar=mar.i)
		#xmaxI <- plotIdeogram(chrom=k,op$cyto.text,cytoband=cytoband,cex=op$cex.cytotext,data.unit=pos.unit)
		xmaxI <- plotIdeogram(chrom=k,op$cyto.text,cytoband=cytoband,cex=op$cex.cytotext,unit=op$plot.unit)
		
		
		#Ideogram max will be used as xlim-max in plot:
		xmax <- xmaxI

		#Parameters for data plot:
		new <- TRUE
		mar <- c(2*op$f,4*op$f,3*op$f,1*op$f)


	}else{
		#Parameters for data plot:
		op$ideo.frac <- 0
		xside=1
		mar=c(2*op$f,4*op$f,3*op$f,1*op$f)
	}
	
	#Plot data (above ideogram if this was plotted)	
	
	#Plot-dimensions:
	aleft <- frame$left
	aright <- frame$right
	abot <- frame$bot + (frame$top-frame$bot)*op$ideo.frac
	atop <- frame$top
	figa <- c(aleft,aright,abot,atop)


	#Y-range; leave out the q/2 % most extreme observations in both directions (either based on entire genome or within chromosome):
	if(is.na(op$q)){
		op$q=0.01
	}
	if(op$equalRange){
		#Use entire genome
		quant <- quantile(y,probs=c(op$q/2,(1-op$q/2)),names=FALSE,type=4,na.rm=TRUE)
	}else{
		#Use only observations within chromosome k
		quant <- quantile(use.y,probs=c(op$q,(1-op$q)),names=FALSE,type=4,na.rm=TRUE)
	}
	if(!is.null(op$h)){ 
		#Make sure that y=h will be plotted:
		botlim <- min(c(op$h,quant[1]))
		toplim <- max(c(op$h,quant[2]))
	}else{
		botlim <- quant[1]
		toplim <- quant[2]
	}
	
	if(is.null(op$ylim)){
		#y-lim will be set such that all segments are shown in plot, as well as (1-q)% of observations:
		if(!is.null(seg.lim)){
			botlim <- min(seg.lim[1],botlim)
			toplim <- max(seg.lim[2],toplim)
		}
		op$ylim <- c(botlim,toplim)
	}
	
	
	#X-axis parameters:
	
	if(is.null(op$xlim)){
		op$xlim <- c(0,xmax)
	}
	
	#Separate colors for wins.obs and non-wins.obs:
	colobs <- rep(op$col,n.k)
	pch.obs <- rep(op$pch,n.k)
	cex.obs <- rep(op$cex,n.k)
	#Winsorized obs are marked by different color, and possibly different symbol:
	if(!is.null(winsoutliers)){
		if(type=="chrom"){
			outliers <- which(winsoutliers[index]!=0)
		}else{if(type=="sample"||type=="genome"){
			outliers <- which(winsoutliers[,index]!=0)
		}}
		colobs[outliers] <- op$wins.col
		pch.obs[outliers] <- op$wins.pch
		cex.obs[outliers] <- op$cex*op$wins.cex
		
	}
	
	#Plot observations that fall outside y-range or x-range on the borders of the plot and mark as yellow:
	colobs[use.y<op$ylim[1]] <- "gold"
	colobs[use.y>op$ylim[2]] <- "gold"
	use.y[use.y<op$ylim[1]] <- op$ylim[1] #+1/100
	use.y[use.y>op$ylim[2]] <- op$ylim[2] #-1/100
	
	#Check if maximum probe position in data is larger than max in ideogram; if this is the case
	#a warning is printed
	out.pos <- x[x>xmax]		
	if(length(out.pos)>0 && print.xwarn){
		#Print warning:
		warning(paste("Chromosome",k,"ranges from position 0 to",paste(xmax,".",sep=""),length(out.pos),"probe positions are outside this range.",sep=" "),call.=FALSE,immediate.=TRUE)
	}
	
	#Plot observations that fall outside x-range on the borders of the plot and mark as yellow:
	colobs[x>xmax] <- "gold"
	x[x>xmax] <- xmax


	
	#Further plot parameters; tick marks on x and y axis:
	if(is.null(op$at.x)){
		if(type=="genome"){
			n.ticks <- 10
		}
		else{
			n.ticks <- 6
		}
		if(xaxis=="pos"){
			op$at.x <- get.xticks(op$xlim[1],op$xlim[2],unit=op$plot.unit,ideal.n=n.ticks)
		}else{
			#xaxis = index:
			op$at.x <- get.xticks(op$xlim[1],op$xlim[2],unit="mbp",ideal.n=n.ticks)
		}
	}
	if(is.null(op$at.y)){
		op$at.y <- get.yticks(op$ylim[1],op$ylim[2])
	}
	
	#placement of labels and axis annotation:
	if(is.null(op$mgp)){
		op$mgp <- c(1.3,0.05,0)*op$f
		mgp.y <- c(2.5,0.5,0)*op$f
	}else{
		mgp.y <- op$mgp
	}
	
	#Default is no xlab, if specified by user the bottom margin must be increased:
	if(op$xlab!=""){
		mar[1] <- mar[1] + 1 
	}
	
	
	#Plot:
	par(fig=figa,new=new,mar=mar)
	
	plot(x,use.y,ylab="",xlab="",main="",pch=pch.obs,cex=cex.obs,col=colobs,ylim=op$ylim,xlim=op$xlim,xaxt="n",yaxt="n",xaxs="i",yaxs="r")
	axis(side=1,cex.axis=op$cex.axis,at=op$at.x,labels=as.integer(op$at.x),mgp=op$mgp,tcl=op$tcl)
	axis(side=2,cex.axis=op$cex.axis,at=op$at.y,mgp=mgp.y,las=op$las,tcl=op$tcl)
	
	mtext(text=op$xlab,side=1,line=op$mgp[1],cex=op$cex.lab)
	mtext(text=op$ylab,side=2,line=mgp.y[1],cex=op$cex.lab)
	
		
	title(main=op$main,line=op$main.line,cex.main=op$cex.main)
	
	
	if(op$sepChrom){		
		#Separate chromosomes by vertical lines (only done for type=="genome")
		nChrom <- length(unique(chromosomes))
		chrom.mark <- separateChrom(chromosomes)
		if(xaxis=="pos"){
			nProbe <- length(x)
			chrom.mark <- c(x[chrom.mark[-length(chrom.mark)]],x[nProbe]+1)
		}
		addChromlines(chromosomes,chrom.mark,op$cex.chrom,op=op)	
	}
	#Add reference line at y=h; h=NULL suppresses plotting of ref.line:
	if(!is.null(op$h)){
		abline(h=op$h,lty=op$h.lty,lwd=op$h.lwd,col=op$h.col)	
	}#endif

	
}#endplotObs



#Function that plots segmentation results for one sample:

plotSegments <- function(segments,type,k=NULL,index=NULL,xaxis,chromosomes=NULL,plot.ideo=FALSE,cytoband=NULL,add=FALSE,col,lty,lwd,frame=NULL,new=FALSE,pos.unit,print.xwarn=TRUE,seg2.lim=NULL,op){
	
	#Pick out relevant data:
	if(type=="genome"||type=="sample"){
	
		#index is a vector indicating the rows representing a given sample:
		use.segments <- segments[index,]
			
		all.segments <- segments[,6]
		
		sampleID <- unique(use.segments[,1])
		if(is.null(op$main)){
			op$main <- sampleID
		}
		
	}
	
	if(type=="chrom"){
		p.arm <- k*2-1
		q.arm <- k*2
		
		use.segments <- segments[segments[,2]==p.arm | segments[,2]==q.arm,]
		all.segments <- segments[,6]
		
		if(is.null(op$main)){
			op$main <- paste("Chromosome",k,sep=" ")	
		}
	}#endif


	#Retrieve segmentinfo
	nSeg <- nrow(use.segments)
	arms <- use.segments[,2]
	seg.mean <- use.segments[,6]
	#seg.mean <- c(seg.mean,seg.mean[nSeg])  #Add last seg.mean twice because of stop
	start <- use.segments[,3]
	stop <- use.segments[,4]
	nPos <- use.segments[,5]

	
	#Separate between arms (for chrom- and sample-plot):
	n.arm <- length(arms)
	if(n.arm>1&&type!="genome"){
		#Locate where the segments in the second arm starts (if two arms):
		sep.arm <- which(use.segments[1:(nSeg-1),2]!=use.segments[2:nSeg,2])+1
	}else{
		sep.arm <- NULL
	}


	if(xaxis=="pos"){
		#Plot against probe position on x-axis
		
		if(type=="genome"){
			#Use global position
			chrom <- getChrom(arms)
			globalseg <- findGlobalSeg(start,stop,chrom=chrom,unit=pos.unit)
			start <- globalseg$glob.start
			stop <- globalseg$glob.stop
			
		}
			
		use.start <- start
		use.stop <- stop
		
	
		if(nSeg>1){
			#The segments should start and end halfway between two probes:
			#half <- (use.start[2:nSeg]-use.stop[1:(nSeg-1)])/2
			#use.start[2:nSeg] <- use.start[2:nSeg] - half
			#use.stop[1:(nSeg-1)] <- use.stop[1:(nSeg-1)]+half
                  			
			if(!is.null(sep.arm)){
				#No connection of segments across arms:
				use.start[sep.arm] <- start[sep.arm]
				use.stop[sep.arm-1] <- stop[sep.arm-1]
				#use.stop <- c(stop[(sep.arm-1)],use.stop)
				
			}		
		}#endif
		
		
		
	}else{
		if(xaxis=="index"){
			#Plot against probe index on x-axis:
					
			use.start <- rep(NA,nSeg) 
			use.start[1] <- 1
			use.stop <- rep(NA,nSeg)
			use.stop[nSeg] <- sum(nPos)
		
		
			if(nSeg>1){
				for(i in 2:nSeg){
					use.start[i] <- use.start[i-1] + nPos[i-1] 
				}
				use.stop[1:(nSeg-1)] <- use.start[2:nSeg]-1
				
				#The segments should start and end halfway between two probes:
				use.start[2:nSeg] <- use.start[2:nSeg]-0.5
				use.stop[1:(nSeg-1)] <- use.stop[1:(nSeg-1)]+0.5
			
				if(!is.null(sep.arm)){
					
					#Start of first segment in second arm should not be halfway between probes
					use.start[sep.arm] <- use.start[sep.arm]+0.5
					use.stop[sep.arm-1] <- use.stop[sep.arm-1]-0.5
				
				
				}#endif
			}
		}else{
			stop(paste("Invalid xaxis option:",quote('xaxis'),sep=" "))
		}
	}#endif
	
	xmax <- max(use.stop)

	
	
	#Plot:
		
	
	#Want to scale the x-axis to fit the desired unit given in plot.unit (default is mega base pairs)
	
	
	if(xaxis=="pos"){
		scale.fac <- convert.unit(unit1=op$plot.unit,unit2=pos.unit)
		use.start <- use.start*scale.fac
		use.stop <- use.stop*scale.fac
		xmax <- xmax*scale.fac
	
	}
	


	#Plotting:
	if(add){
		#add segments to existing plot:
		segments(x0=use.start,y0=seg.mean,x1=use.stop,y1=seg.mean,col=col,lwd=lwd,lty=lty)
		
		#Connect segments; except across arms:
		if(!is.null(sep.arm)&&nSeg>2){
			segments(x0=use.stop[-c((sep.arm-1),nSeg)],y0=seg.mean[-c((sep.arm-1),nSeg)],x1=use.stop[-c((sep.arm-1),nSeg)],
			y1=seg.mean[-c(1,sep.arm)],col=col,lwd=lwd,lty=lty)
		}else{if(is.null(sep.arm)&&nSeg>1){
			segments(x0=use.stop[1:(nSeg-1)],y0=seg.mean[1:(nSeg-1)],x1=use.stop[1:(nSeg-1)],y1=seg.mean[2:nSeg],col=col,lwd=lwd,lty=lty)
		}}
		
	}else{
		#Plot only segments:

		#Plot ideogram at bottom of plot (not if xaxis=index):
		if(plot.ideo && xaxis=="pos"){
			
			if(is.na(op$ideo.frac)){
				#ideo.frac has not been defined by user:
				op$ideo.frac <- (1/25)*1/op$f
				if(op$cyto.text){
					#Need larger space for ideogram:
					op$ideo.frac <- (1.5+ncol*0.5)*op$ideo.frac  
				}
			}

			#Ideogram-plot dimensions:
			ileft <- frame$left
			iright <- frame$right
			ibot <- frame$bot
			itop <- frame$bot + (frame$top-frame$bot)*op$ideo.frac						
			figi <- c(ileft,iright,ibot,itop)

			#Margins:
			mar.i <- c(0.2*op$f,4*op$f,0,1*op$f)
			if(op$cyto.text){
				#Need to increase bottom margin:
				mar.i <- mar.i + c(2,0,0,0)
			}	
	
		
			#Plot ideogram:
			par(fig=figi,new=new,mar=mar.i)
			xmaxI <- plotIdeogram(chrom=k,op$cyto.text,cytoband=cytoband,cex=op$cex.cytotext,unit=op$plot.unit)
			#Make sure that segment positions fall within ideogram:
			
			xmax <- xmaxI

			#Parameters for segments plot:
			new=TRUE
			xside=1
			mar=c(2*op$f,4*op$f,3*op$f,1*op$f)
		}else{
			#Parameters for segments plot:
			op$ideo.frac <- 0
			xside=1
			mar=c(2*op$f,4*op$f,3*op$f,1*op$f)
		}
	
		#Segment-plot dimensions:
		aleft <- frame$left
		aright <- frame$right
		abot <- frame$bot + (frame$top-frame$bot)*op$ideo.frac
		atop <- frame$top
		figa <- c(aleft,aright,abot,atop)


		#Y-range; leave out the (q/2) % most extreme observations in both directions (either based on entire genome or within chromosome):
		if(is.na(op$q)){
			op$q=0
		}
		if(op$equalRange){
			#Use entire genome
			quant <- quantile(all.segments,probs=c(op$q/2,(1-op$q/2)),names=FALSE)
		}else{
			#Use only observations within chosen segments
			quant <- quantile(use.segments[,6],probs=c(op$q,(1-op$q)),names=FALSE)
		}
		
		if(!is.null(op$h)){
			botlim <- min(c(op$h,quant[1]))
			toplim <- max(c(op$h,quant[2]))
		}else{
			botlim <- quant[1]
			toplim <- quant[2]
		}

		if(is.null(op$ylim)){
			#Make sure that segments2 are included in range as well:
			if(!is.null(seg2.lim)){
				botlim <- min(seg2.lim[1],botlim)
				toplim <- max(seg2.lim[2],toplim)
			}
			op$ylim <- c(botlim,toplim)
		}


		#x-axis parameters:
		if(is.null(op$xlim)){
			op$xlim <- c(0,xmax)
		}

		#Check if end of any segments is larger than max in ideogram; if this is the case
		#a warning is printed
		out.seg <- use.stop[use.stop>xmax]		
		if(length(out.seg)>0 && print.xwarn){
			#Print warning:
			warning(paste("Chromosome",k,"ranges from position 0 to",paste(xmax,".",sep=""),length(out.seg),"segments are outside this range.",sep=" "),call.=FALSE,immediate.=TRUE)
		}


		#Further plot parameters; tick marks on x and y axis:		
		if(is.null(op$at.x)){
			if(type=="genome"){
				n.ticks <- 10
			}
			else{
				n.ticks <- 6
			}
			if(xaxis=="pos"){
				op$at.x <- get.xticks(op$xlim[1],op$xlim[2],unit=op$plot.unit,ideal.n=n.ticks)
			}else{if(xaxis=="index"){
				op$at.x <- get.xticks(op$xlim[1],op$xlim[2],unit="mbp",ideal.n=n.ticks)
			}}
			
		}
		if(is.null(op$at.y)){
			op$at.y <- get.yticks(op$ylim[1],op$ylim[2])
			
		}
		
		#placement of labels and axis annotation:
		if(is.null(op$mgp)){
			op$mgp <- c(1.3,0.05,0)*op$f
			mgp.y <- c(2,0.5,0)*op$f
		}else{
			mgp.y <- op$mgp
		}

		#Default is no xlab, if specified by user the bottom margin must be increased:
		if(op$xlab!=""){
			mar[1] <- mar[1] + 1 
		}

		#Plot
		par(fig=figa,new=new,mar=mar)
		
		#Empty plot with desired dimensions:
		plot(start,seg.mean,type="n",col=col,lwd=lwd,lty=lty,main="",xlab="",
			xlim=op$xlim,las=op$las,ylab="",ylim=op$ylim,xaxt="n",yaxt="n",xaxs="i")
		
		#Plot segments
		segments(x0=use.start,y0=seg.mean,x1=use.stop,y1=seg.mean,col=col,lwd=lwd,lty=lty)
		
		#Connect segments except across arms:
		if(!is.null(sep.arm)&&nSeg>2){
			segments(x0=use.stop[-c((sep.arm-1),nSeg)],y0=seg.mean[-c((sep.arm-1),nSeg)],x1=use.stop[-c((sep.arm-1),nSeg)],
			y1=seg.mean[-c(1,sep.arm)],col=col,lwd=lwd,lty=lty)
		}else{if(is.null(sep.arm)&&nSeg>1){
			segments(x0=use.stop[1:(nSeg-1)],y0=seg.mean[1:(nSeg-1)],x1=use.stop[1:(nSeg-1)],y1=seg.mean[2:nSeg],col=col,lwd=lwd,lty=lty)
                }}
		
								
		axis(side=1,cex.axis=op$cex.axis,at=op$at.x,labels=as.integer(op$at.x),mgp=op$mgp,tcl=op$tcl)
		axis(side=2,cex.axis=op$cex.axis,at=op$at.y,mgp=mgp.y,las=op$las,tcl=op$tcl)
		mtext(text=op$xlab,side=1,line=op$mgp[1],cex=op$cex.lab)
		mtext(text=op$ylab,side=2,line=mgp.y[1],cex=op$cex.lab)
		
		title(main=op$main,line=op$main.line,cex.main=op$cex.main)
		
		if(op$sepChrom){
			#Separate chromosomes by vertical lines (only done for type=="genome")
			chromosomes <- chromosomes[index]
			nChrom <- length(unique(chromosomes))
			chrom.mark <- separateChrom(chromosomes)
			
			if(xaxis=="pos"){
				chrom.mark <- c(start[chrom.mark[-length(chrom.mark)]],stop[nSeg])*scale.fac
			}
			#Separate chromosomes by vertical lines:
			addChromlines(chromosomes,chrom.mark,op$cex.chrom,op=op)	
		}
		#Add reference line at y=h; h=NULL suppresses plotting of ref.line:
		if(!is.null(op$h)){
			#Add reference line
			abline(h=op$h,lty=op$h.lty,lwd=op$h.lwd,col=op$h.col)
		}#endif
		
	}#endif
		
}#endplotSegments

#Help-functions:

#Function to find frame dimensions when a window is to be sectioned into nrow rows and ncol columns:
framedim <- function(nrow,ncol){
	cl <- 0:(ncol-1)
	cr <- 1:ncol
	left <- rep(1/ncol,ncol)*cl
	right <- rep(1/ncol,ncol)*cr

	rt <- nrow:1
	rb <- (nrow-1):0
	top <- rep(1/nrow,nrow)*rt
	bot <- rep(1/nrow,nrow)*rb

	return(list(left=left,right=right,bot=bot,top=top))
}#endframedim


#Function to check if segments come from pcf-routine or multipcf-routine:
is.multiseg <- function(segments){
	#If multisegment, the first column will give arm numbers (numeric), whereas if unisegment the first column will give sampleid (character):
	multi <- ifelse(is.numeric(segments[1,1]),TRUE,FALSE)
	
	return(multi)
}#end is.multiseg



#Function to extract relevant information from input data:
extractFromData <- function(data,chrom,sampleID,winsoutliers,type){
	#data must be a matrix with arm in first column, position in second, and copy numbers in remaining column(s).
	#Check that data has at least 3 columns:
	stopifnot(ncol(data)>=3)
	org.data <- data
	
	if(type=="chrom"){
		#Check that maximum one sampleID has been specified:
		if(length(sampleID)>1){
			warning(paste("Only one sampleID should be specified, the first sampleID (",sampleID[1],") is used.",sep=" "),immediate.=TRUE,call.=FALSE)
			sampleID <- sampleID[1]
			
			#Check that specified sampleID is found in data:
			if(!any(colnames(data)==sampleID)){
				stop(paste("No data is found for sampleID",sampleID,sep=" "))
			}
		}else{
			#If sampleID is missing, data should ideally only represent one sample. If more than one sample is represented in data, only the first sample will be chosen; either way column 3 will be chosen
			if(ncol(data)>3){
				warning(paste("More than one sample is represented in data and sampleID is missing. Only ",colnames(data)[3]," is used.",sep=" "),immediate.=TRUE,call.=FALSE)
			}
			data <- data[,1:3,drop=FALSE]
		}
		
	}#endif
		
	if(type=="sample"){
		#Check that maximum one chromosome has been specified:
		if(length(chrom)>1){
			warning(paste("Only one chromosome should be specified, only the first chromosome (",chrom[1],") is used.",sep=" "),immediate.=TRUE,call.=FALSE)
			chrom <- chrom[1]
			
			p.arm <- chrom*2-1
			q.arm <- chrom*2
			arms <- c(p.arm,q.arm)
			#Check that specified chrom is found in data:
			if(!any(data[,1]%in%arms)){
				stop(paste("No data is found for chromosome",chrom,sep=" "))
			}
		}else{
			#If chrom is missing, data should ideally only represent just one chromosome. If more than one chrom is represented in data, only the first chrom will be chosen:
			all.chrom <- unique(getChrom(data[,2]))
			if(length(all.chrom)==1){
				warning(paste("More than one chromosome is represented in data and chrom is missing. Only chromosome",all.chrom[1]," is used.",sep=" "),immediate.=TRUE,call.=FALSE)
				chrom <- unique(all.chrom)[1]   #choose first chromosome
			}
		}
			
	}#endif
	
	#Extract relevant data:
	if(is.null(chrom) && is.null(sampleID)){
		#Should just keep data as they are:
		sel.data <- data[,-2,drop=FALSE]
	}else{
		sel.data <- getSubset(data=data[,-2,drop=FALSE],chrom=chrom,sampleid=sampleID)
	}
	arm <- sel.data[,1]
	y <- sel.data[,-1]
	sampleID <- colnames(sel.data)[-1]
	
	if(!is.null(chrom)){
		#also get subset of positions:
		position <- getSubset(position=data[,c(1:2)],chrom=chrom)
	}else{
		position <- data[,2]
	}
	
	#Extract relevant winsoutliers as well:
	if(!is.null(winsoutliers)){
		#Check that winsoutliers has 2 columns less than data (wins.outliers does not have columns with arms and positions):
		winsoutliers <- as.matrix(winsoutliers)
		
		if(ncol(winsoutliers)!=(ncol(org.data)-2)){
			stop("number of samples in winsoutliers must be the same as in data",call.=FALSE)
		}
		
		#Get winsoutliers for indicated sample:
		if(!is.null(chrom) || !is.null(sampleID)){
			sel.outliers <- getSubset(data=cbind(data[,1],winsoutliers),chrom=chrom,sampleid=sampleID)
			winsoutliers <- sel.outliers[,-1,drop=FALSE]
		}
	}

	return(list(y=y,arm=arm,position=position,winsoutliers=winsoutliers,sampleID=sampleID,chrom=chrom))
}#end extractFromData


#Function to extract relevant information from segments:
extractFromSegments <- function(segments,chrom,sampleID,type){

	#Check segements form:
	multi <- is.multiseg(segments)
	if(multi){
		stopifnot(ncol(segments)>=5)
		#Convert to uniseg format:
		segments <- getUnisegFormat(segments)
	}else{
		stopifnot(ncol(segments)>=6)
	}
	
	if(type=="chrom"){
		#Check that maximum one sampleID has been specified:
		if(length(sampleID)>1){
			warning(paste("Only one sampleID should be specified, the first sampleID (",sampleID[1],") is used.",sep=" "),immediate.=TRUE,call.=FALSE)
			sampleID <- sampleID[1]
				
			#Check that specified sampleID is found in data:
			
			seg.samples <- unique(segments[,1])
				
			if(!any(seg.samples==sampleID)){
				stop(paste("No segments found for sampleID",sampleID,sep=" "))
			}
		}
		if(is.null(sampleID)){
			#If sampleID is missing, segments should only represent one sample. If more than one sample is represented in segments, only the first sample will be chosen:
			
			all.samples <- unique(segments[,1])
			if(length(all.samples)>1){
				sampleID <- unique(segments[,1])[1]
				warning(paste("More than one sample is represented in segments and sampleID is missing. Only ",sampleID," is used.",sep=" "),immediate.=TRUE,call.=FALSE)
			}
			
		}
		
	}#endif
		
	if(type=="sample"){
		#Check that maximum one chromosome has been specified:
		if(length(chrom)>1){
			warning(paste("Only one chromosome should be specified, only the first chromosome (",chrom[1],") is used.",sep=" "),immediate.=TRUE,call.=FALSE)
			chrom <- chrom[1]
		
			p.arm <- chrom*2-1
			q.arm <- chrom*2
			arms <- c(p.arm,q.arm)
			#Check that specified chrom is found in data:
			seg.arms <- segments[,2]
			
			if(!any(seg.arms%in%arms)){
				stop(paste("No segments found for chromosome",chrom,sep=" "))
			}
		}else{
			#If chrom is missing, segments should ideally only represent just one chromosome. If more than one chrom is represented in data, only the first chrom will be chosen:
			
			all.chrom <- unique(getChrom(segments[,2]))
			
			if(length(all.chrom)==1){
				warning(paste("More than one chromosome is represented in segments and chrom is missing. Only chromosome",all.chrom[1]," is used.",sep=" "),immediate.=TRUE,call.=FALSE)
				chrom <- unique(all.chrom)[1]   #choose first chromosome
			}	
		}
			
	}#endif
	
	#Extract relevant segments:
	if(is.null(chrom) && is.null(sampleID)){
		#keep segments as they are:
		sel.segments <- segments
	}else{
		sel.segments <- getSubset(segments=segments,chrom=chrom,sampleid=sampleID)
	}
	
	arm <- sel.segments[,2]
	sampleID <- unique(sel.segments[,1])
	
	return(list(segments=sel.segments,arm=arm,sampleID=sampleID))
}#end extractFromSegments





#Function to get multisegment results on a unisegmentformat:
getUnisegFormat <- function(segments){

	#Check that the segments are really on a multiseg format first:
	stopifnot(is.multiseg(segments))
	
	nSample <- ncol(segments)-4
	nSeg <- nrow(segments)
	uni.segments <- as.data.frame(matrix(NA,ncol=6,nrow=0))
	colnames(uni.segments) <- c("SampleID",colnames(segments)[1:4],"Mean")
	for(i in 1:nSample){
		sampleID <- colnames(segments)[4+i]
		sample.segments <- cbind(rep(sampleID,nSeg),segments[,c(1:4,(4+i))])
		colnames(sample.segments) <- colnames(uni.segments)
		uni.segments <- rbind(uni.segments,sample.segments,deparse.level=0)
	}

	return(uni.segments)
	
}



#Function to set default plotting parameteres, and modify these according to user specifications:
getPlotParameters <- function(type,nc,sampleID=NULL,chrom=NULL,...){

	#Default parameters:
	
	#Apply a scaling factor according to number of columns in grid
	ff <- c(1,0.9,0.81,0.73,0.65)   
	if(nc>5){
		ff[6:nc] <- ff[5]
	}
	
	f <- ff[nc]
	
	
	#List with default plotting parameters:
	arg <- list(title="",col="dodgerblue",wins.col="magenta",pch=".",wins.pch="*", ylab=expression(log[2]~"-ratio"),
		xlab="",main=NULL,xlim=NULL,ylim=NULL,f=ff[nc],cex=2*f,wins.cex=0.4,cex.lab=1*f,cex.main=1.2*f,
		cex.axis=0.9*f,las=1,at.x=NULL,at.y=NULL, main.line=0.6*f,mgp=NULL,tcl=-0.3*f,equalRange=TRUE,
		q=NA,h=0,h.lty=5,h.lwd=f,h.col="darkgrey",ideo.frac=NA,cyto.text=FALSE,cex.cytotext=0.6,sepChrom=FALSE,
		cex.chrom=0.7*f,plot.unit="mbp",seg.col=c("red","green"),seg.lty=c(1,1),seg.lwd=c(4*f,3*f),equalRange=TRUE)


	if(type=="genome"){
		#By default: plot lines to separate the chromosomes:
		arg$sepChrom=TRUE
		arg$main.line=1.5*f
		arg$title=ifelse(length(sampleID)==1,sampleID,"Genomeplot")
	}
	if(type=="chrom"){
		arg$title <- sampleID
	}
	if(type=="sample"){
		arg$title <- paste("Chromosome",chrom,sep=" ")
	}
	
	#Check for user modifications
	arg <- modifyList(arg,list(...))
	
	return(arg)
	
}#endgetPlotParameters


#Function get segments y-limits:
get.seglim <- function(segments,equalRange,index=NULL,k=NULL){
	
	if(equalRange){
		#Use all segments to determine limits:
		use.segments <- segments
	}else{
		#Use only segments indicated by index or k to calculate limits:
		if(!is.null(k)){
			p.arm <- k*2-1
			q.arm <- k*2		
			use.segments <- segments[segments[,2]==p.arm | segments[,2]==q.arm,]
		}else{if(!is.null(index)){
			use.segments <- segments[index,]
		}}
	}				
	
	seg.lim <- c(min(use.segments[,6]),max(use.segments[,6]))
	
	return(seg.lim)
	
}#end get.seglim


#Use arm numbers to find corresponding chromosomenumbers
getChrom <- function(arm){
	chrom <- rep(0,0)
	for(i in 1:length(arm)){
		if(arm[i]%%2==0){
			#"even" arm
			chrom <- append(chrom,arm[i]/2)
		}else{
			#"odd" arm
			chrom <- append(chrom,(arm[i]+1)/2)
		}
	}#endfor
	return(chrom)
}#endgetChrom


#Given a vector of arm numbers for all probes; find the index of probes within a given chromosome:
getChromIndex <- function(k,arm){
	p.arm <- (k*2)-1
	q.arm <- k*2
	use.arms <- c(p.arm,q.arm)
	ind <- which(arm%in%use.arms)
	
	return(ind)

}

#Function to determine where each chromosome starts (and the last chromosome ends):
separateChrom <- function(chromosomes){
	#Determine start-index of the different chromosomes:
	nChrom <- length(unique(chromosomes))
	chrom.sep <- which(chromosomes[1:(length(chromosomes)-1)]!=chromosomes[2:length(chromosomes)])+1
	#Include the first and last(+1) index (to include the start of first chrom,and the stop of last chrom)
	chrom.sep <- c(1,chrom.sep,(length(chromosomes)+1))

	return(chrom.sep)
}#end separateChrom


#Function to get a scaling factor such that unit2 may be converted to unit1:
convert.unit <- function(unit1,unit2){
	
	factor <- NA
	#Allowed units:
	units <- c("bp","kbp","mbp")
	
	if(identical(unit1,unit2)){
		factor <- 1
	}else{
		if(identical(unit1,units[3])){
			if(identical(unit2,units[2])){
				factor <- 1/(10^3)
			}else{if(identical(unit2,units[1])){
				factor <- 1/(10^6)
			}}
		}else{
			if(identical(unit1,units[2])){
				if(identical(unit2,units[3])){
					factor <- 10^3
				}else{if(identical(unit2,units[1])){
					factor <- 1/(10^3)
				}}
			}else{
				if(identical(unit1,units[1])){
					if(identical(unit2,units[3])){
						factor <- 10^6
					}else{if(identical(unit2,units[2])){
						factor <- 10^3
					}}
				}
			}
		}
	}
	
	if(is.na(factor)){
		if(all(units!=unit2)){
			stop(paste("unit2 must match one of",deparse(units[1]),",",deparse(units[2]),"or",deparse(units[3]),sep=" "))
		}
		if(all(units!=unit1)){
			stop(paste("unit1 must match one of",deparse(units[1]),",",deparse(units[2]),"or",deparse(units[3]),sep=" "))
		}
		
	}
	
	return(factor)
}#end convert.unit

#convert.unit("bp","kbp")

#Function that converts local positions to cumulative(!) global positions
convertToGlobalPos <- function(localPos,chrom){
	nloc <- length(localPos)
	globalPos <- rep(NA, nloc)

	#sep <- which(localPos[2:nloc]<localPos[1:(nloc-1)])+1
	#sep <- c(sep,(nloc+1))
	#Global position is the same as local pos. for the first chromosome:
	sep <- separateChrom(chrom)[-1]
	globalPos[1:(sep[1]-1)] <- localPos[1:(sep[1]-1)]
	for(j in 1:(length(sep)-1)){
		globalPos[sep[j]:(sep[j+1]-1)] <- localPos[sep[j]:(sep[j+1]-1)]+globalPos[sep[j]-1]
		#If all chromosomes start with position 0, need to add 1 to global pos to avoid equal glob.pos at end of chrom j and start of chrom j+1
		if(localPos[sep[j]]==0){
			globalPos[sep[j]:(sep[j+1]-1)] <- globalPos[sep[j]:(sep[j+1]-1)] +1
		}
	}

	return(globalPos)
}


#Function to covert local posistions to global positions based on a defined set of local stop positions of p.arms and chromosomes
getGlobPos <- function(position,chrom,unit){

	f <- switch(unit,
		bp = 1,
		kbp = 10^(-3),
		mbp = 10^(-6))
			
	loc.pStop <- c(124300000,93300000,91700000,50700000,47700000,60500000,59100000,45200000,
		51800000,40300000,52900000,35400000,16000000,15600000,17000000,38200000,22200000,
		16100000,28500000,27100000,12300000,11800000,59500000,11300000)*f
		
	chromStop <- c(247249719, 242951149, 199501827,191273063,180857866,170899992,158821424,146274826,
		140273252,135374737,134452384,132349534,114142980,106368585,100338915,88827254,
		78774742,76117153,63811651,62435964,46944323,49691432,154913754,57772954)*f
	
	
	
	totChromStart <- chromStop[-length(chromStop)]+1
	for(j in 2:length(totChromStart)){
		totChromStart[j] <- totChromStart[j] + totChromStart[j-1]
	}
	totChromStart <- c(0,totChromStart)   #add as first chromosome start
	
	pStop <- loc.pStop
	
	glob.pos <- rep(NA,length(position))	
	chrom.list <- unique(chrom)
	nChrom <- length(chrom.list)
	for(i in 1:nChrom){
		c <- chrom.list[i]
		ind.c <- which(chrom==c)
		
		#Get global position
		glob.pos[ind.c] <- position[ind.c] + totChromStart[c]
		
	}
	
	return(glob.pos)
}#end getGlobPos


#Function that converts local segment start and stop positions to global start and stop positions (using getGlobPos):
findGlobalSeg <- function(seg.start,seg.stop,chrom,unit){
	nSeg <- length(seg.start)

	#Append start and stop positions for the segments
	pos <- rep(0,0)
	for(i in 1:nSeg){
		pos <- append(pos,c(seg.start[i],seg.stop[i]))
	}#endfor

	#Get global positions for the combined vector of start and stop:
	use.chrom <- rep(chrom,each=2)
	
	#global.pos <-  convertToGlobalPos(pos,use.chrom)
	global.pos <- getGlobPos(pos,use.chrom,unit=unit)

	#Divide the vector into global start and global stop:
	glob.start <- rep(0,0)
	glob.stop <- rep(0,0)
	for(j in 1:length(global.pos)){
		if(j%%2!=0){
			glob.start <- append(glob.start,global.pos[j])
		}else{
			glob.stop <- append(glob.stop,global.pos[j])
		}
	}#endfor

	return(list(glob.start=glob.start,glob.stop=glob.stop))

}#endfindGlobalSeg

#Function to calculate ticks along x-axis in plot:
get.xticks <- function(min,max,unit,ideal.n){
	
	
	if(identical(unit,"mbp")){
		#if(is.null(ideal.n)){
		#	ideal.n <- 8
		#}
		by <- c(1,2,5,10,20,40,60,80,100,200,500,1000,2000,5000)
	}else{if(identical(unit,"kbp")){
		ideal.n <- ideal.n-1
		by <- c(1,2,5,10,20,40,60,80,100,200,500,1000,2000,5000)*1000
	}}
	
	use.min <- rep(NA,length(by))
	use.max <- rep(NA,length(by))
	n.tick <- rep(NA,length(by))

	for(i in 1:length(by)){
		use.max[i] <- max
		if(max%%by[i]!=0){
			use.max[i] <- max + (by[i]-max%%by[i]) 
		}
		use.min[i] <- min
		if(min%%by[i]!=0){
			use.min[i] <- min - min%%by[i] 
		}
		seq <- seq(use.min[i],use.max[i],by=by[i])
		n.tick[i] <- length(seq)
				
	}#endfor	
	
	diff <- sapply(n.tick,"-",ideal.n)
	best <- which.min(abs(diff))
	#Eventuelt den som minimerer positiv diff?	
	ticks <- seq(use.min[best],use.max[best],by=by[best])
	
	return(ticks)

}#endfunction

#Function to calculate ticks along y-axis in plot:
get.yticks <- function(min,max){
	
	ideal.n <- 5
	by <- c(1e6,2e6,5e6,1e5,2e5,5e5,1e4,2e4,5e4,1e3,2e3,5e3,0.01,0.02,0.05,0.1,0.2,0.5,1,2,5,10,50,100,500,1000,2000,5000,10000,20000,50000,100000,200000,500000,10000000,20000000,50000000,100000000,200000000,500000000,1000000000)
	use.min <- rep(NA,length(by))
	use.max <- rep(NA,length(by))
	n.tick <- rep(NA,length(by))

	for(i in 1:length(by)){
		use.max[i] <- max
		if(max%%by[i]!=0){
			use.max[i] <- max + (by[i]-max%%by[i]) 
		}
		use.min[i] <- min
		if(min%%by[i]!=0){
			use.min[i] <- min - min%%by[i] 
		}
#		seq <- seq(use.min[i],use.max[i],by=by[i])
		n.tick[i] <- (use.max[i]-use.min[i])/by[i]
				
	}#endfor	
		
	diff <- sapply(n.tick,"-",ideal.n)
	best <- which.min(abs(diff))
		
	ticks <- seq(use.min[best],use.max[best],by=by[best])
	return(ticks)

}#endfunction


#get.yticks(-2.36,0)

#Function used to separate chromosomes by stapled lines in genome plot:
addChromlines <- function(chromosome,chrom.mark,cex,op){
	#Separate chromosomes by vertical lines in existing plot:
	nChrom <- length(unique(chromosome))
	arg <- list(chrom.lwd=1, chrom.lty=2, chrom.col="darkgrey",chrom.side=3, chrom.cex=cex,chrom.line=0)
	
	arg <- modifyList(arg,op)
	
	abline(v=chrom.mark-0.5,col=arg$chrom.col,lwd=arg$chrom.lwd,lty=arg$chrom.lty)
	mtext(unique(chromosome),side=arg$chrom.side,line=arg$chrom.line,at=(chrom.mark[1:nChrom]-1)+(chrom.mark[2:(nChrom+1)]-chrom.mark[1:nChrom])/2,cex=arg$chrom.cex)
	#mtext("Chrom.",side=arg$chrom.side,line=arg$chrom.line,at=-1,cex=arg$chrom.cex)
}#endaddChromlines




getSubset <- function(data=NULL,segments=NULL,data.files=NULL,segment.files=NULL,position=NULL,chrom=NULL,sampleid=NULL){
	
	#Data subset
	if(!is.null(data)){
		data.subset <- selectData(data=data,chrom=chrom,sampleid=sampleid)
	}else{
		if(!is.null(data.files)){
			data.subset <- selectData(files=data.files,chrom=chrom,sampleid=sampleid)
		}else{
			data.subset <- NULL
		}
	}
	
	#Segments subset
	if(!is.null(segments)){
		segments.subset <- selectSegments(segments=segments,chrom=chrom,sampleid=sampleid)
	}else{
		if(!is.null(segment.files)){
			segments.subset <- selectSegments(files=segment.files,chrom=chrom,sampleid=sampleid)
		}else{
			segments.subset <- NULL
		}
	}
	
	#Position subset:
	if(!is.null(position)){
		if(ncol(position)!=2){
			warning("position must have two columns!")
			position.subset <- NULL
		}else{
			position.subset <- getChromPos(position=position[,2],arms=position[,1],chrom=chrom)
		}
	}else{
		position.subset <- NULL
	}
	
	#Only return non-null results:
	notnull <- c(!is.null(data.subset),!is.null(segments.subset),!is.null(position.subset))
	keep <- which(notnull==TRUE)
	if(length(keep)>1){
		res.list <- list(dataSubset=data.subset,segmentSubset=segments.subset,positionSubset= position.subset)
		res.list <- res.list[keep]
		return(res.list)
	}else{
		if(keep==1){
			return(data.subset)
		}else{
			if(keep==2){
				return(segments.subset)
			}else{
				return(position.subset)
			}
		}
	}#endif
	
}#endgetSubset


selectSegments <- function(segments=NULL,files=NULL,chrom=NULL,sampleid=NULL){
	
	if(!is.null(chrom)){
		p.arm <- chrom*2-1
		q.arm <- chrom*2
		arms <- c(p.arm,q.arm)
	}

	if(!is.null(segments)){
		keepchrom <- 1:nrow(segments)
		multi <- is.multiseg(segments)
		if(!multi){
			if(!is.null(chrom)){
				keepchrom <- which(segments[,2]%in%arms)
			}
			sel.segments <- segments[keepchrom,,drop=FALSE]
			keepsample <- 1:nrow(sel.segments)
			
			if(!is.null(sampleid)){
				keepsample <- which(sel.segments[,1]%in%sampleid)
			}
			
			sel.segments <- sel.segments[keepsample,,drop=FALSE]
		}else{
			if(!is.null(chrom)){
				keepchrom <- which(segments[,1]%in%arms)
			}
			sel.segments <- segments[keepchrom,,drop=FALSE]
			keepsample <- 5:ncol(sel.segments)
			if(!is.null(sampleid)){
				keepsample <- which(colnames(sel.segments)%in%sampleid)
			}
			sel.segments <- sel.segments[,c(1:4,keepsample),drop=FALSE]
		}
		
	}else{
		
		for(f in 1:length(files)){
			segments <- read.table(files[f],header=TRUE)
			keepchrom <- 1:nrow(segments)
			multi <- is.multiseg(segments)
			if(!multi){
				if(!is.null(chrom)){
					keepchrom <- which(segments[,2]%in%arms)
				}
				use.segments <- segments[keepchrom,,drop=FALSE]
				keepsample <- 1:nrow(use.segments)
				if(!is.null(sampleid)){
					keepsample <- which(use.segments[,1]%in%sampleid)
				}
				use.segments <- use.segments[keepsample,,drop=FALSE]
	
				if(f==1){
					sel.segments <- matrix(0,nrow=0,ncol=ncol(use.segments))
				}
				sel.segments <- rbind(sel.segments,use.segments)
			}else{
				if(!is.null(chrom)){
					keepchrom <- which(segments[,1]%in%arms)
				}
				use.segments <- segments[keepchrom,,drop=FALSE]
				keepsample <- 5:ncol(use.segments)
				if(!is.null(sampleid)){
					keepsample <- which(colnames(use.segments)%in%sampleid)
				}
				use.segments <- use.segments[,c(1:4,keepsample),drop=FALSE]
	
				if(f==1){
					sel.segments <- matrix(0,nrow=0,ncol=ncol(use.segments))
				}
				sel.segments <- rbind(sel.segments,use.segments)
			}
		}#endfor
	}
	#Sort by sampleid if uniseg and by chrom.number if multiseg
	sort.by <- sel.segments[,1]
	if(is.factor(sort.by)){
		sort.by <- as.character(sort.by)
	}
	sel.segments <- sel.segments[order(sort.by),]
	rownames(sel.segments) <- 1:nrow(sel.segments)


	return(sel.segments)

}





selectData <- function(data=NULL,files=NULL,chrom=NULL,sampleid=NULL){

	if(!is.null(chrom)){
		p.arm <- chrom*2-1
		q.arm <- chrom*2
		arms <- c(p.arm,q.arm)
	}

	if(!is.null(data)){
		if(is.null(chrom)){
			arms <- unique(data[,1])
		}
		keepchrom <- which(data[,1]%in%arms)
		keepsample <- 2:ncol(data)
		if(!is.null(sampleid)){
			keepsample <- which(colnames(data)%in%sampleid)
			#data <- data[,c(1,keep)]
		}
		
		data <- data[keepchrom,c(1,keepsample),drop=FALSE]

	}else{

		for(f in 1:length(files)){
			use.data <- read.table(files[f],header=TRUE)
			
			if(f==1){
				data <- use.data[,1,drop=FALSE]
				if(is.null(chrom)){
					arms <- unique(data[,1])
				}
				keepchrom <- which(data[,1]%in%arms)
				data <- data[keepchrom,,drop=FALSE]
			}
			y <- use.data[keepchrom,2,drop=FALSE]

			keepsample <- TRUE
			if(!is.null(sampleid)){
				id <- colnames(y)
				keepsample <- id%in%sampleid
			}
			if(keepsample){
				data <- cbind(data,y)
			}
			
			
		}#endfor
	}

	#Order columns by samplenames:
	if(ncol(data)>2){
		samplenames <- colnames(data[,-1])
		data <- data[,c(1,order(samplenames)+1)]
	}
	
	return(data)
}

getChromPos <- function(position,arms,chrom){
	if(is.null(chrom)){
		chrom.pos <- position   #return all positions
	}else{
		p.arm <- chrom*2-1
		q.arm <- chrom*2
		use.arms <- c(p.arm,q.arm)
		chrom.pos <- position[arms%in%use.arms]
	}
	return(chrom.pos)
}#endgetChromPos



plotIdeogram <- function(chrom,cyto.text=FALSE,cex=0.6,cytoband,cyto.unit="bp",unit){
	
	if(chrom==23){
		chrom.cytoband <- cytoband[cytoband[,1]=="chrX",]
	}else{
		if(chrom==24){
			chrom.cytoband <- cytoband[cytoband[,1]=="chrY",]
		}else{
			chrom.cytoband <- cytoband[cytoband[,1]==paste("chr",chrom,sep=""),]
		}
	}
	
	cyto.start <- chrom.cytoband[,2]
	cyto.end <- chrom.cytoband[,3]
	scale <- convert.unit(unit1=unit,unit2=cyto.unit)
	
	xleft <- cyto.start*scale
	xright <- cyto.end*scale
	n <- length(xleft)
	stain <- chrom.cytoband[,5]
	sep.stain <- c("gpos","gneg","acen","gvar","stalk")

	g <- sapply(sep.stain,grep,x=stain,fixed=TRUE)

	centromere <- g$acen
	stalk <- g$stalk
	col <- rep("",n)
	col[stain=="gneg"] <- "white"
	col[stain=="gpos100"] <- "black"
	col[stain=="gpos75"] <- "gray25"
        col[stain=="gpos66"] <- "gray33"
	col[stain=="gpos50"] <- "gray50"
        col[stain=="gpos33"] <- "gray66"
	col[stain=="gpos25"] <- "gray75"
	col[stain=="stalk"] <- "gray90"
	col[stain=="gvar"] <- "grey"
	col[stain=="acen"] <- "black"
	density <- rep(NA,n)
	angle <- rep(45,n)
	density[stain=="gvar"] <- 15
	angle[stain=="gvar"] <- -60
	density[stain=="acen"] <- 25
	angle[stain=="acen"] <- 60
	
	

	ylow <- 0
	yhigh <- 1
	

	plot(x=c(0,max(xright)),y=c(ylow,yhigh),type="n",axes=FALSE,xlab="",ylab="",xlim=c(0,max(xright)),ylim=c(0,1),xaxs="i")
	#rect(xleft[-centromere],rep(ylow,n-length(centromere)),xright[-centromere],rep(yhigh,n-length(centromere)),col=col[-centromere],density=density,border="black")
	#polygon(x=c(xleft[centromere[1]],xright[centromere[1]],xleft[centromere[1]]),y=c(ylow,yhigh/2,yhigh),col=col[centromere[1]])
	#polygon(x=c(xleft[centromere[2]],xright[centromere[2]],xright[centromere[2]]),y=c(yhigh/2,ylow,yhigh),col=col[centromere[2]])
	
	#Rectangles:
	skip.rect <- c(1,centromere,n,stalk)
	rect(xleft[-skip.rect],rep(ylow,n-length(skip.rect)),xright[-skip.rect],rep(yhigh,n-length(skip.rect)),
		col=col[-skip.rect],border="black",density=density[-skip.rect],angle=angle[-skip.rect])
	
	#Round edges at ideogram start, stop and at centromere:
	draw.roundEdge(start=xleft[1],stop=xright[1],y0=ylow,y1=yhigh,col=col[1],bow="left",density=density[1],angle=angle[1],unit=unit)
	draw.roundEdge(start=xleft[centromere[1]],stop=xright[centromere[1]],y0=ylow,y1=yhigh,col=col[centromere[1]],bow="right",density=density[centromere[1]],
		angle=angle[centromere[1]],lwd=1,unit=unit)
	draw.roundEdge(start=xleft[centromere[2]],stop=xright[centromere[2]],y0=ylow,y1=yhigh,col=col[centromere[2]],bow="left",density=density[centromere[2]],
		angle=angle[centromere[2]],lwd=1,unit=unit)
	draw.roundEdge(start=xleft[n],stop=xright[n],y0=ylow,y1=yhigh,col=col[n],bow="right",density=density[n],angle=angle[n],unit=unit)

	#Draw stalk-segment:
	if(length(stalk)>0){
		for(i in 1:length(stalk)){
			drawStalk(xleft[stalk[i]],xright[stalk[i]],ylow,yhigh,col=col[stalk[i]])
		}
	}
	if(cyto.text){
		mtext(text=paste(chrom.cytoband$name,"-",sep=" "),side=1,at=(xleft + (xright-xleft)/2),cex=cex,las=2,adj=1,xpd=NA)
	}
	
	return(max(xright))
}

#Test buet ende og centromere:


draw.roundEdge <- function(start,stop,y0,y1,col,bow,density=NA,angle=45,lwd=1,unit){
	#Y points in roundedge:
	f <- rep(0,0)
	f[1] <- 0.001
	i=1
	half <- y0+(y1-y0)/2
	while(f[i]<half){
		f[i+1] <- f[i]*2
		i <- i+1
		#print(f[i])
	}
	f <- f[-length(f)]
	
	Y <- c(y1,y1,y1-f,half,y0+rev(f),y0,y0)
	
	#X points in roundedge
	cyto.length <- stop-start
        print(cyto.length)
        if(is.na(cyto.length)){
          print('hello')
          return()
        }
	
	if(unit=="bp"){
		u <- 1.5*10^6
	}else{
		if(unit=="kbp"){
			u <- 1500
		}
		else{
			u <- 1.5
		}
	}
	
	if(bow=="left"){
		if(cyto.length > u){
			round.start <- start+u
		}else{
			round.start <- stop
		}
		x <- seq(round.start,start,length.out=(length(f)+2))
		revx <- rev(x[-length(x)])
		x <- c(x,revx)
		X <- c(stop,x,stop)
	}else{
		if(bow=="right"){
			
			if(cyto.length > u){
				round.start <- stop - u
			}else{
				round.start <- start
			}
			x <- seq(round.start,stop,length.out=(length(f)+2))
			revx <- rev(x[-length(x)])
			x <- c(x,revx)
			X <- c(start,x,start)

		}
	}
	
	polygon(x=X,y=Y,col=col,border="black",density=density,angle=angle,lwd=lwd)

}

drawStalk <- function(start,stop,y0,y1,col){
	size <- stop-start
	x1 <- c(start,start+size/3,stop-size/3,stop)
	x2 <- rev(x1)
	x <- c(x1,x2)
	y_1 <- c(y0,y0+0.25,y0+0.25,y0)
	y_2 <- c(y1,y1-0.25,y1-0.25,y1)
	y <- c(y_1,y_2)
	polygon(x=x,y=y,col=col)

}
