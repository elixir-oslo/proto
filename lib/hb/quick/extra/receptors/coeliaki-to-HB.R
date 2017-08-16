#################################################################
#
#  Estimation of distribution of number of Tcells for each clonotypes
#
#  Several samples for each patient. 
#  Want to fint out whether these samples are from same distribution. 
#  Use a statistical urn model with many clonotypes
# 
#  External function calls:
#  EstimateClonotypesParameters
#  FindPosteriorClonatypesDistribution
#
#  CPU time is proportional with sim x function evaluations, about 100.000 per min.
#   assume about 100 clonotypes, 500 clonotypes increases time with 50% 
#  EstimateClonotypesParameters
#  sim=100   2-5 min. 
#  sim=5000, Model 1 often 100 function evaluations  30 min=0.5 hours 
#  sim=5000, Model 2 often 250 function evaluations  100 min= 1-2hours    
#  sim=5000, Model 3 often 400 function evaluations  400 min= 2-3 hours
#  FindPosteriorClonatypesDistribution
#  sim=200, simMCMC=10.000 = function evaluations    400 min=2-3 hours

#################################################################


##################################################################
#
#  Estimate distribution for clonotypes 
#  Find that parameters that most likely gives the dataset in CD1
####################################################################

EstimateClonotypesParameters<-function(CD1,sim,param,Model,ClonoFunc,LL)  {
  
#  CD1 data fra pasient # CD114 <- read.table("TcellDatasets/CD114.txt", header=T, sep="\t")
#  sim number of simulations when evaluating result  # sim<-5000 gives good approximation. Negative value for simulation
#  param parameters in model that may start give starting point of optimization, else default values
#  Model  1: same frequency   2: same ordrer   3: correlated order
#  ClonoFunc, function for number of clonotypes,  1: Fraction  2 Exponential 3 and 4 linear combination
#  LL list similar to L, specifices model for generating synthetic data ( specified by sim<0)
#
#  Output. List with
#  par  parameters
#  value optimal value
#  counts function calls
#  pvalH, and pvalN approximation to p-value, comparing by simulating from estimated parameter histogram/normal
#  mostProb the probabilities to the most probable clonotypes for each sample
#  h    help variables compares with simulation from estimated parameters
#  hh   help variables probabilities for most likely clonotypes


   L<-MakeList(CD1,sim,param,Model,ClonoFunc,LL) 
   k1<-L$k1
   N1<-L$N1
   X1<-L$X1
   XT<-L$XT
   XS<-L$XS
   MetN<-L$MetN
   X1v<-L$X1v
   Nklon<-L$Nklon
   Fklon<-L$Fklon
   Cklon<-L$Cklon
   P<-L$P
   PS<-L$PS

   if (Model==1) {   # S Same frequency
       xx<-c(Nklon,Fklon[1])
       hres<-optim(xx,fnS,L=L) #, lower=lower, upper=upper)fnS(xx,L)
       Fklon<-rep(hres$par[2],k1)
    } 
    if (Model==2) {   # O Same order
        xx<-c(Nklon,Fklon) 
  #      hres<-optim(xx,fnO,L=L,method="L-BFGS-B",lower=c(10,0,0,0), upper=c(500,1,1,1)) # for MetN=4 
        hres<-optim(xx,fnO,L=L) #, lower=lower, upper=upper)  #s  fnO(xx,L)
        Fklon<-hres$par[2:(1+k1)]
   } 
   if (Model==3) {   # C corrlated order
       xx<-c(Nklon,Fklon,Cklon)
       hres<-optim(xx,fnC,L=L) #, lower=lower, upper=upper)   #
       Fklon<-hres$par[2:(1+k1)]
       Cklon<-hres$par[(2+k1):(2*k1+1)]
  }
   Nklon<-floor(hres$par[1])   # must be integer
   L$Nklon<-Nklon
   L$Fklon<-Fklon
   L$Cklon<-Cklon
   
   hh<-matrix(0,k1,9)                  # finds probabilities for each clonotype for optimal parameters
   P<-Nford(k1,Nklon,Fklon,XT,MetN)
   PS<-rep(0,k1)
   for (i in 1:k1) PS[i]<-sum(P[i,])
   for ( i in 1:k1) {
        hh[i,]<-c(sum(P[i,]>0),P[i,1]/XT[i],P[i,5]/XT[i],P[i,10]/XT[i],P[i,25]/XT[i],P[i,50]/XT[i],Fklon[i],XT[i],P[i,1])
   }
  #  hh
   L$P<-P
   L$PS<-PS
   h<- sammenlignAndreRel(L)  # finds p-value by comparing with simulation from parametres

   list(par=hres$par,value=hres$value,counts=hres$counts,pvalH=h[length(h)-1],pvalN=h[length(h)],mostProb=hh[,2],h=h,hh=hh)
}  # end    EstimateClonotypesParameters


##################################################################
#
#  Find posterior distribution for clonotypes 
#   uses data and find uncertainty in parameters
####################################################################


FindPosteriorClonotypesDistribution<-function(CD1,sim,simMCMC,param,Model,ClonoFunc,LL)  {
  
#  CD1 data fra pasient # CD114 <- read.table("TcellDatasets/CD114.txt", header=T, sep="\t")
#  sim number of simulations when evaluating result  # sim<-5000, negative for synthetic
#  simMCMC number of iterations in MCMC loop   # simMCMC<-10000
# param is estimated parameters or parameters within distribution.
#  Model  1: same frequency   2: same ordrer   3: correlated order
#  ClonoFunc, function for number of clonotypes,  1: Fraction  2: Exponential 3 and 4:Linear combination
#  LL is list similar to L that is used in case for synthetic simulation
#
#  output. List with
#  acc  accept rate
#  XXM  matrix with MCMC chain
#  XXM[,1:2 or 1:(1+k) or 1:(1+2k)] parameters in model, k is number of samples in dataset
#  XXM[,(2+k):(5+k)]  distance from mean, p-value, acc. ratio (new pval/old pval),  (assuming model 2 with 1+k parameter)
#  XXM[,(6+k):(5+2k)] probability most likely clonotype in each sample,             (assuming model 2 with 1+k parameter)

   L<-MakeList(CD1,sim,param,Model,ClonoFunc,LL) 
   k1<-L$k1
   
   npar<-1+k1
   if(Model==3) npar<- 1+2*k1
   XXM<-matrix(0, simMCMC,npar+k1+3) # dataene 1:npar  parametrene, npar+1: T, npar+2: P(TY<TX), npar+3 ratio npar+4:npar+3+k1 sh clonotype 
   u<-runif(simMCMC)  # velge parameter
   u1<-runif(simMCMC)  # endre parameter
   u2<-runif(simMCMC)  # aksept
   acc<-0

   h<- sammenlignAndreRel(L)  #   (sim,param[1],param[2:(1+k1)],param[(2+k1):(2*k1+1)],MetN)
   c(h[1:3],sum(h[1:3]*c(1,0.33,0.05)),h[4:length(h)]) 
   XXM[1,]<-c(param,sum(h[1:3]*c(1,0.33,0.05)),max(h[length(h)-1],0.001),0,L$P[,1]/L$XT)     # startverdier

###############   MCMC

for ( i in 2:simMCMC) {  # i<-2  # i<-i+1
    XXM[i,]<-XXM[i-1,]   # lik forrige verdi
# random walk increasing/decreasing values, changing one value. u determines parameter and u1 determines value
   if (u[i]<0.5) XXM[i,floor(2*npar*u[i]+1)]<-XXM[i,floor(2*npar*u[i]+1)]*(1+u1[i]/2)   # 
   if (u[i]>0.5) XXM[i,floor(2*npar*(u[i]-0.5)+1)]<-XXM[i,floor(2*npar*(u[i]-0.5)+1)]/(1+u1[i]/2)
#
   c(i,XXM[i,1:4],floor(2*npar*u[i]+1),u[i])
   c(i,XXM[i-1,1:4],floor(2*npar*(u[i]-0.5)+1),u[i])

   L$Nklon<-floor(XXM[i,1])
   L$Fklon<-XXM[i,2:(1+k1)]
   if( Model==1) L$Fklon<-rep(XXM[i,2],k1)
   L$Cklon<-XXM[i,(2+k1):(2*k1+1)]
   if( Model<2.5) L$Cklon<-rep(0,k1)
   L$P<-Nford(L$k1,L$Nklon,L$Fklon,L$XT,L$MetN)   # beregne  antall av hver type
   L$PS<-rep(0,k1)
   for (ii in 1:k1) L$PS[ii]<-sum(L$P[ii,]) 
   XXM[i,(npar+4):(npar+3+k1)]<- L$P[,1]/L$XT
    h<- sammenlignAndreRel(L) #    sim,XXM[i,1],XXM[i,2:(1+k1)],MetN)
   c(i,h[1:5],L$Fklon,L$Cklon )
#   c(h[1:3],sum(h[1:3]*c(1,0.33,0.05)),h[4:length(h)]) 
   XXM[i,npar+1:3]<-c(sum(h[1:3]*c(1,0.33,0.05)),max(h[length(h)-1],0.001),max(h[length(h)-1],0.001)/XXM[i-1,npar+2])   # denne som ikke lages.
   XXM[i,npar+1:3]
   if (u2[i]<XXM[i,npar+3])     acc<-acc+1  # endre
   if (u2[i]>XXM[i,npar+3]) XXM[i,]<-XXM[i-1,]  # ikke endre
  c(u2[i]<XXM[i,npar+3],acc)
}  # end MCMC loop


list(acc=acc/simMCMC,XXM=XXM)

} # end FindPosteriorClonatypesDistribution

##########################################################
#  Make list
##############################################################

MakeList<-function(CD1,sim,param,Model,ClonoFunc,LL)  {
  
#  CD1 data fra pasient # CD114 <- read.table("TcellDatasets/CD114.txt", header=T, sep="\t")
#  sim number of simulations when evaluating result  # sim<-5000
#  param parameters in model that may start give starting point of optimization, else default values
#  Model  1: same frequency   2: same ordrer   3: correlated order
#  ClonoFunc, function for number of clonotypes,  1: Fraction  2 Exponential
#  LL is list similar to L, used for synthetic data

   strs <- CD1[,1]   ############# antar en av datasettene er lest inn i CD1
   pos1 <- regexpr("ID:", strs)
   pos2 <- regexpr(", Name", strs)
   MetN<-ClonoFunc

   N1<-nrow(CD1)-1   # kopy to data variable X
   k1<-ncol(CD1)-1
   X1<-matrix(0,k1,N1)
   for (i in 1:k1) X1[i,]<-CD1[1:N1,i+1]
   if (sim<0) X1<-simURelData(LL)                 # synthetic data when sim<0
   XT<-rep(0,k1)
   for (i in 1:k1) XT[i]<-CD1[N1+1,i+1] # totalt T-celler i organ
   XS<-rep(0,k1)
   for (i in 1:k1) XS[i]<-sum(X1[i,]) # totalt T-celler i test
   MetN<-ClonoFunc    # 1# 2# 1
   X1v<-Properties(X1,k1)   # finds property vector of data

   # initielle parametre når vi starter optimeringen
   if (min(param)>0) {   # have initial values of parameters
      Nklon<-param[1]
      Fklon<-rep(param[2],k1)
      if (Model>1) Fklon<-param[2:(1+k1)]   
      Cklon<-rep(0,k1)
      if (Model==3)  Cklon<-param[(2+k1):(2*k1+1)] 
   } else {            # default values of parameters
      Nklon<-100
      Fklon<-rep(1,k1)  
      if (MetN==4)  Fklon<-rep(0.5,k1)
      Cklon<-rep(0,k1)
      if (Model==3)  Cklon<-rep(2,k1)
   }
   
   P<-Nford(k1,Nklon,Fklon,XT,MetN)   # finds intital distribution of number of Tcells for each clonotype
   PS<-rep(0,k1)
   for (i in 1:k1) PS[i]<-sum(P[i,])
   
   list(sim=abs(sim),N1=N1,k1=k1,X1=X1,XT=XT,XS=XS,X1v=X1v,Nklon=Nklon,Fklon=Fklon,Cklon=Cklon,Model=Model,MetN=MetN,P=P,PS=PS) 
}

###############################################################
#
#  Simulerer en realisasjon
#####################################################################

simURelData<-function(L) { 
  k1<-L$k1
  sim<-L$sim

  if(L$Model==3) {         # change order of clonotypes based on Cklon
     rel<-matrix(0,k1+1,L$Nklon)   
     for ( i in 1:(k1+1)) rel[i,]<-rnorm(L$Nklon) 
     for (i in 1:k1) rel[i,]<-(1:L$Nklon)+L$Cklon[i]*rel[i,]
     for (i in 1:k1) L$P[i,]<-L$P[i,sort.list(rel[i,])] 
  }

  UN2<-0
  U<-matrix(0,k1,L$Nklon)
  for ( j in 1:L$Nklon) { # j<-1 # j<-j+1  # for each clonotype
    for ( i in 1:k1) {  # i<-1 # i>-i+1   # for each sample
       U[i,UN2+1]<-rbinom(1,L$P[i,j],L$XS[i]/L$PS[i])      # rbinom (NOF samples, n, prob)
    }
    if(sum(U[,UN2+1])>0) UN2<-UN2+1  # this clonotype present in at least one sample
  }

  U
}  # end simURelData<-function


###############################################################
#
#  Simulerer en realisasjon og analyserer data
#####################################################################

Properties<-function(U,k1){ 

  UR<-matrix(0,9+k1,k1)
  for (i in 1:k1) {
      UR[1,i]<-sum(U[i,]) # sum # Data: X1, dim: k1, N1, 1: sum, 2: KlonotypPS 3: max, 4: sum 5 største, 5: sum 10 største, 6 kropp, 7:6+k1 overlapp
      UR[2,i]<-sum(U[i,]>0) # ant klonotype
      UR[3,i]<-max(U[i,])
      UR[4,i]<-sum(-sort(-U[i,])[1:5]) # sum 5 largest
      UR[5,i]<-sum(-sort(-U[i,])[1:10]) 
      for (j in 1:k1) {
          hSortList<-sort.list(-U[i,])
          UR[6,i]<-UR[6,i]+U[j,hSortList[1]]
          UR[7,i]<-UR[7,i]+sum(U[j,hSortList[1:5]])
          UR[8,i]<-UR[8,i]+sum(U[j,hSortList[1:10]])
      }
      for (j in 3:5)  UR[j+3,i]<-UR[j+3,i]-UR[j,i]   # finner antall T-celler i andre tester.
#      UR[9,]<-L$PS # totalt T-celler i organ   brukes ikke
      for (j in 1:k1) UR[i+9,j]<-sum(U[i,]*U[j,]>0)   # overlapp av Klonotyper
   }
#   UR
   if (k1==2) hh<-c(UR[1,],UR[2,],UR[3,],UR[4,],UR[5,],UR[6,],UR[7,],UR[8,],UR[10,],UR[11,])
   if (k1==3) hh<-c(UR[1,],UR[2,],UR[3,],UR[4,],UR[5,],UR[6,],UR[7,],UR[8,],UR[10,],UR[11,],UR[12,])
   if (k1==4) hh<-c(UR[1,],UR[2,],UR[3,],UR[4,],UR[5,],UR[6,],UR[7,],UR[8,],UR[10,],UR[11,],UR[12,],UR[13,])

    hh
  }  # end Properties


###############################################################
#
#  Sammenligner simulerte data med virkelige data
#####################################################################

sammenlign<-function(L) { 
  set.seed(123)
  k1<-L$k1
  sim<-L$sim
  X1v<-L$X1v

  L$P<-Nford(L$k1,L$Nklon,L$Fklon,L$XT,L$MetN)   # beregne  antall av hver type
  L$PS<-rep(0,k1)
  for (i in 1:k1) L$PS[i]<-sum(L$P[i,])

  URM<-matrix(0,sim,(8+k1)*k1)
  for (i in 1:sim) {
     U<-simURelData(L)
     URM[i,]<-Properties(U,k1)    # finds properties of simulated realisation, comparable with X1v from data
  }
  URMstat<-matrix(0,4,(8+k1)*k1)
  for (i in 1:((8+k1)*k1)) URMstat[,i]<-c(X1v[i],mean(URM[,i]),sd(URM[,i]),-(X1v[i]-mean(URM[,i]))/(sd(URM[,i])+0.00001))
#  URMstat

   c(sum(abs(URMstat[4,])),sum(abs(URMstat[1,]-URMstat[2,])),sum((URMstat[1,]-URMstat[2,])**2))  
  } # end sammenlign

###############################################################
#
#  Sammenligner med andre realisasjoner
#####################################################################

sammenlignAndreRel<-function(L) {  # assumes P and PS are updated
  set.seed(123)
  k1<-L$k1
  sim<-L$sim
  X1v<-L$X1v

  URM<-matrix(0,sim,(8+k1)*k1)
  for (i in 1:sim) {    #simulate other realisations and finds properites
     U<-simURelData(L)
     URM[i,]<-Properties(U,k1)  # 
  }
  URMstat<-matrix(0,4,(8+k1)*k1)
#  URMstat  # 1-3: #T-cell, 4-6: # klonotyp, 7-9max 10-12: sum5 største, 13-15: sum 10 største, 16-24: andre tester i største 25: korr 
  for (i in 1:((8+k1)*k1)) URMstat[,i]<-c(X1v[i],mean(URM[,i]),sd(URM[,i]),-(X1v[i]-mean(URM[,i]))/(sd(URM[,i])+0.00001))
 URMstat
  resData<-rep(0,4)
  resData[1:3]<- c(sum(abs(URMstat[4,])),sum(abs(URMstat[1,]-URMstat[2,])),sum((URMstat[1,]-URMstat[2,])**2))  # avstand til data
  resData[4]<-sum(resData[1:3]*c(1,0.33,0.05))

  # snitt avvik
  URMmean<-rep(0,(8+k1)*k1)
  for (i in 1:((8+k1)*k1)) URMmean[i]<-mean(URM[,i])
  URMsd<-rep(0,(8+k1)*k1)
  for (i in 1:((8+k1)*k1)) URMsd[i]<-sd(URM[,i])

# gjennomsnittlig avvik for simulerte data
  DiffSimData<-matrix(0,sim,4)
  for  (i in 1:sim) DiffSimData[i,1:3]<-c(sum(abs(URM[i,]-URMmean)/(URMsd+0.00001)),sum(abs(URM[i,]-URMmean)),sum((URM[i,]-URMmean)**2))
  for  (i in 1:sim) DiffSimData[i,4]<-sum(DiffSimData[i,1:3]*c(1,0.33,0.05))
# hist(DiffSimData[,4],breaks=100)
  
  h3<-sum(resData[4]<DiffSimData[,4])/length(DiffSimData[,4])   # fasit ved opptelling
  res<-matrix(0,3,sim)
  for (i in 1:sim) {
     h<- abs(URM[i,]-URMmean)
     res[,i]<-c(sum(h/(URMsd+0.00001)), sum(h),sum(h**2))
  }

  c(mean(res[1,]),mean(res[2,]),mean(res[3,]),URMstat[4,],1-pnorm((resData[4]-mean(DiffSimData[,4]))/sd(DiffSimData[,4])),h3)

 } # end sammenlignAndreRel

############################################################  
# fordeling av Tceller for hver klonotype
############################################################

  Nford<-function(k1,Nklon,Fklon,XT,MetN) {
      P<-matrix(0,k1,Nklon) #  Uttrekk: U, dim: k1, UN1, mens >0 UN2 1: sum, 2: Klonotyp: 1, 3: max, 4: sum 5 største, 5: sum 10 største, 6 kropp, 7:6+k1 overlapp
       for ( i in 1:k1) {
           if(MetN==1)     FORD<- 1/(Fklon[i]-1+(1:Nklon))
           if(MetN==2)     FORD<-exp(-(1:Nklon)/Fklon[i])
           if(MetN==3)     FORD<-(exp(-Fklon[i]/10))*(0.18/(1:Nklon-0.2)-1/Nklon)+1/Nklon
           if(MetN==4)     FORD<- min(Fklon[i],1)*(0.18/(1:Nklon-0.2)-1/Nklon)+1/Nklon
          P[i,]<-floor(0.5+FORD*XT[i]/sum(FORD))  # P[1,1:10]
       }
     P
   }  # end Nford

#######################################################   Optimeringsfunksjon

fnS <-function(xx,L) {    # antar modell S: Same frequencies. parametre Nklon,Fklon[1]   2
                        
   hRes<-0                # NB foreløpig uten MetN==4 ###############################################
   hh<-c(100,1)
   xx<-xx[1:2]
   for (i in 1:length(xx)) {
       if (xx[i]<hh[i]*0.1) {
              hRes<- hRes+10*(0.1*hh[i]-xx[i])**2
              xx[i]<-0.1*hh[i]
    }}
   if (L$MetN==4) {
       for (i in 2:(L$k1+1)) {
         if (xx[i]>0.999) {
              hRes<- hRes+1000*(0.999-xx[i])**2
              xx[i]<-0.999
    }}}
    L$Nklon<-floor(xx[1])
    L$Fklon<-rep(xx[2],L$k1)
    output<-sammenlign(L)
#   print(c(L$Nklon,L$Fklon[1],sum(output*c(1,0.33,0.05))+hRes,L$PS,L$P[,1],L$N1))
    sum(output*c(1,0.33,0.05))+hRes
 }

fnO <-function(xx,L) {    # antar modell O: Ordered frequencies. parametre Nklon,Fklon   k1+1
                        
   hRes<-0
   hh<-c(100,rep(1,L$k1))
   for (i in 1:length(xx)) {
       if (xx[i]<hh[i]*0.1) {
              hRes<- hRes+1000*(0.1*hh[i]-xx[i])**2
              xx[i]<-0.1*hh[i]
   }}
   if (L$MetN==4) {
       for (i in 2:(L$k1+1)) {
         if (xx[i]>0.999) {
              hRes<- hRes+1000*(0.999-xx[i])**2
              xx[i]<-0.999
    }}}
    L$Nklon<-floor(xx[1])
    L$Fklon<-xx[2:(1+L$k1)]
   output<-sammenlign(L)# (sim,xx[1],xx[2:(1+k1)],X1R,k1,N1,P,PS,MetN)
# print(c(L$Nklon,L$Fklon,sum(output*c(1,0.33,0.05))+hRes,L$PS,L$P[,1],L$N1))
    sum(output*c(1,0.33,0.05))+hRes
 }

fnC <-function(xx,L) {    # antar modell C: correlated frequencies. parametre Nklon,Fklon,Cklon   2k1+1
                        
   hRes<-0
   hh<-c(100,rep(1,2*L$k1))
 for (i in 1:length(xx)) {
       if (xx[i]<hh[i]*0.1) {
              hRes<- hRes+10*(0.1*hh[i]-xx[i])**2
              xx[i]<-0.1*hh[i]
    }}
    if (L$MetN==4) {
       for (i in 2:(L$k1+1)) {
         if (xx[i]>0.999) {
              hRes<- hRes+1000*(0.999-xx[i])**2
              xx[i]<-0.999
    }}}
    L$Nklon<-floor(xx[1])
    L$Fklon<-xx[2:(1+L$k1)]
    L$Cklon<-xx[(2+L$k1):(1+2*L$k1)]
    output<-sammenlign(L)# (sim,xx[1],xx[2:(1+2*k1)],X1R,k1,N1,P,PS,MetN)
    sum(output*c(1,0.33,0.05))+hRes
 }




