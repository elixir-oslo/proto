import numpy as np

from HyperBrowserControllerMixin import HyperBrowserControllerMixin
from gold.application.StatRunner import AnalysisDefJob
from gold.description.TrackInfo import TrackInfo
from proto.BaseToolController import BaseToolController
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.extra.clustering.ClusteringExecution import ClusteringExecution
from quick.extra.clustering.FeatureCatalog import (SplittedRegionsAsFeaturesCatalog,
                                                   DirectDistanceCatalog, FeatureCatalog,
                                                   LocalResultsAsFeaturesCatalog)


class ClusteringToolController(HyperBrowserControllerMixin, BaseToolController):
    def __init__(self, trans, job):
        BaseToolController.__init__(self, trans, job)
    
    def handlePairDistance(self, genome, tracks, track_names, clusterMethod, extra_option):
        if self.params.has_key("pair_feature") : # must use "" here because the '' does not work
            feature = self.params.get('pair_feature')
            extra_feature = self.params.get('pair_feature+') #must be different from the text --select--
            regSpec, binSpec = self.getRegAndBinSpec()
            
            #d_matrix = self.constructDistMatrix(genome, tracks, feature, extra_feature)
            #figure = GalaxyRunSpecificFile(['cluster_trakcs_result_figure.pdf'], self.jobFile) #this figure is runspecific and is put in the directory
            #
            #figurepath = figure.getDiskPath(True)
            #r.pdf(figurepath, 8, 8)
            #r.assign('track_names',track_names)
            #r.assign('d_matrix', d_matrix)
            #r('row.names(d_matrix) <- track_names')
            #
            #r('d <- as.dist(d_matrix)')
            #if clusterMethod == 'Hierarchical clustering' and extra_option != "--select--" :
            #   r.assign('extra_option',extra_option) 
            #   r('hr <- hclust(d, method=extra_option, members=NULL)')
            #   r('plot(hr, ylab="Distance", hang=-1)')
            #   
            #r('dev.off()')
            #print figure.getLink('clustering results figure<br>')
            
            ClusteringExecution.executePairDistance(genome, tracks, track_names, clusterMethod, extra_option, feature, extra_feature, self.jobFile, regSpec, binSpec)
            
        else :
            print 'A feature must be selected in order to compute the distance between tracks.'
    
    def handleReferenceTrack(self, genome, tracks, track_names, clusterMethod, extra_option ):
        reftrack_names = [] #for use in creating the heatmap (as the column names)
        refTracks = []
        options = [] #for the case using refTracks, options contains feature for every refTrack, chosen by user.
        print 'params'
        keys = sorted(self.params.keys())
        for key in keys:
            print key, self.params[key]
        numreferencetracks = self.params.get('numreferencetracks')
        refTracks = [self.params['reftrack' + str(i+1)] for i in range(int(numreferencetracks))] if numreferencetracks else None
        refFeatures = [self.params.get('ref'+str(i)+'feature') for i in range(int(numreferencetracks))] if numreferencetracks else None
        yesNo = [self.params.get('yes_no'+str(i)) for i in range(int(numreferencetracks))] if numreferencetracks else None
        howMany = [self.params.get('how_many'+str(i)) if self.params.get('how_many'+str(i)) else '0' for i in range(int(numreferencetracks))] if numreferencetracks else None
        upFlank = [ [self.params.get(str(i)+'_'+str(v)+'up')for v in range(int(howMany[i]))] for i in range(int(numreferencetracks))] if numreferencetracks else None 
        downFlank =[ [self.params.get(str(i)+'_'+str(v)+'down') for v in range(int(howMany[i]))] for i in range(int(numreferencetracks))] if numreferencetracks else None 
        distanceType = self.params.get("distanceType") #from distanceType select tag 
        kmeans_alg = self.params.get("kmeans_alg")
        regSpec, binSpec = self.getRegAndBinSpec()
        
        ClusteringExecution.executeReferenceTrack(genome, tracks, track_names, clusterMethod, extra_option, distanceType, kmeans_alg, self.jobFile, regSpec, binSpec, numreferencetracks, refTracks, refFeatures, yesNo, howMany, upFlank, downFlank)
        
        #if self.params.has_key('numreferencetracks') :
        #    for i in range(int(self.params['numreferencetracks'])):
        #        ref_i = self.params['reftrack' + str(i+1)].split(":") #name of refTrack is being used to construct the name of expanded refTrack
        #        refTracks.append(ref_i) #put the refTrack into refTracks list
        #        reftrack_names.append(ref_i[-1])
        #        temp_opt1 = 'ref'+str(i)+'feature'
        #        options+= [] if self.params.get(temp_opt1) == None else [self.params.get(temp_opt1)]
        #        if self.params.get('yes_no'+str(i)) == "Yes" and self.params.get('how_many'+str(i)) != "--select--":
        #            for expan in range(int(self.params.get('how_many'+str(i)))) :
        #                reftrack_names.append(ref_i[-1]+'_'+self.params.get(str(i)+'_'+str(expan)+'up'))
        #                upFlank = int(self.params.get(str(i)+'_'+str(expan)+'up'))
        #                downFlank = int(self.params.get(str(i)+'_'+str(expan)+'down'))
        #                withinRunId = str(i+1)+' expansion '+str(expan + 1)
        #                outTrackName = GalaxyInterface.expandBedSegmentsFromTrackNameUsingGalaxyFn(ref_i, genome, upFlank, downFlank, self.jobFile, withinRunId) #outTrackName is unique for run
        #                refTracks.append(outTrackName) #put the expanded track into refTracks list
        #                options.append(options[-1]) # use chosen feature for refTack as valid feature for the expanded
        #                
        #    for index, track in enumerate(refTracks) :
        #        print track, '<br>'
        #        if isinstance(track, basestring) :
        #            track = track.split(":")
        #        refTracks[index] = track[:-1] if track[-1] == "-- All subtypes --" else track
        #        
        #if len(refTracks) > 0 :
        #    
        #   distanceType = self.params.get("distanceType") #from distanceType select tag 
        #   
        #   kmeans_alg = self.params.get("kmeans_alg")
        #   
        #   f_matrix = self.construct_feature_matrix_using_reftracks(genome,tracks,reftracks,options, regSpec, binSpec)
        #   
        #   r.assign('track_names',track_names) #use as track names, will be shown in clustering figure
        #   r.assign('reftrack_names',reftrack_names)
        #   r.assign('f_matrix',f_matrix)
        #   r.assign('distanceType',distanceType)
        #   r('row.names(f_matrix) <- track_names')
        #   r('colnames(f_matrix) <- reftrack_names')
        #   
        #   if clusterMethod == 'Hierarchical clustering' and extra_option != "--select--":
        #       figure = GalaxyRunSpecificFile(['cluster_tracks_result_figure.png'], self.jobFile)
        #       figurepath = figure.getDiskPath(True) 
        #       r.png(figurepath)
        #       r('d <- dist(f_matrix, method=distanceType)')
        #       r.assign('extra_option',extra_option)
        #       r('hr <- hclust(d, method=extra_option, members=NULL)')
        #       r('plot(hr, ylab="Distance", hang=-1)')
        #       
        #       r('dev.off()')
        #       print figure.getLink('clustering results figure<br>')
        #   elif clusterMethod == 'K-means clustering' and extra_option != "--select--" and kmeans_alg != "--select--":
        #       textFile = GalaxyRunSpecificFile(['result_of_kmeans_clustering.txt'], self.jobFile)
        #       textFilePath = textFile.getDiskPath(True)
        #       extra_option = int(extra_option)
        #       r.assign('extra_option',extra_option)
        #       r.assign('kmeans_alg',kmeans_alg)
        #       r('hr <- kmeans(f_matrix,extra_option,algorithm=kmeans_alg)') #the number of cluster is gotten from clusterMethod+ tag, instead of 3 used here
        #       
        #       kmeans_output = open(textFilePath,'w')
        #       clusterSizes = r('hr$size') #size of every cluster
        #       
        #       withinSS = r('hr$withinss')
        #       clusters = array(r('hr$cluster')) #convert to array in order to handle the index more easily
        #       track_names = array(track_names) 
        #       for index1 in range(extra_option) : #extra_option actually the number of clusters
        #           trackInCluster = [k for k,val in clusters.items() if val == index1]
        #           
        #           print>>kmeans_output, 'Cluster %i(%s objects) : ' % (index1+1, str(clusterSizes[index1]))
        #           for name in trackInCluster :
        #               print>>kmeans_output, name
        #               
        #           print>>kmeans_output, 'Sum of square error for this cluster is : '+str(withinSS[index1])+'\n'
        #       kmeans_output.close()
        #       print textFile.getLink('Detailed result of kmeans clustering <br>') 
        #        
        #   
        #   heatmap = GalaxyRunSpecificFile(['heatmap_figure.png'], self.jobFile)
        #   heatmap_path = heatmap.getDiskPath(True)
        #   r.png(heatmap_path, width=700, height=500)
        #   r('heatmap(f_matrix, col=cm.colors(256), Colv=NA, scale="none", xlab="Features", ylab="cluster tracks")')
        #   r('dev.off()')
        #   
        #   print heatmap.getLink('heatmap figure <br>')
        #   print self.print_data(f_matrix)
        #   
        #else :
        #   print 'Have to specify a set of refTracks'
    
    def handleSelfFeature(self, genome, tracks, track_names, clusterMethod, extra_option):
        
        if self.params.has_key("self_feature") :
            feature = self.params.get("self_feature")
            distanceType = self.params.get("distanceType") #from distanceType select tag 
            kmeans_alg = self.params.get("kmeans_alg")
            jobFile = self.jobFile
            regSpec, binSpec = self.getRegAndBinSpec()
            
            return ClusteringExecution.executeSelfFeature(genome, tracks, track_names, clusterMethod, extra_option, feature, distanceType, kmeans_alg, jobFile, regSpec, binSpec)
        else :
            print 'A feature must be selected in order to build the feature vecotr for tracks.'
            
   
    def handleRegionClustering(self, genome, tracks, clusterMethod, extra_option):
        region_cluster_track = self.getHistoryTrackDef('track1')
        print region_cluster_track
        region_ref_track = self.params.get('reftrack1')
        if region_cluster_track[0] == 'galaxy' :
            file_type = region_cluster_track[1]
            track_path = region_cluster_track[2]
            userBinSource = GalaxyInterface._getUserBinSource('bed', track_path, genome)
            validFeature = SplittedRegionsAsFeaturesCatalog.getValidAnalyses(genome,region_ref_track,[])
            analysisDef = validFeature[0]
            result = AnalysisDefJob(analysisDef, region_ref_track, [], userBinSource).run()
            print [result[localKey][validFeature[1]] for localKey in sorted(result.keys())]
    
    def execute(self):
        
        
        self.stdoutToHistory() # links stdout til self.jobFile
        
        genome = self.params.get('dbkey')
        clusterTracks = [self.params['track'+str(i)] for i in range(1,int(self.params['numclustertracks'])+1) ]
        tracks = self.trackPrepare(clusterTracks, genome)
        track_names = [track[-1] for track in tracks] #just take the last part in each track_path, used as name of the track
        
        clusterMethod = self.params.get("clusterMethod") # from clusterMethod select tag
        extra_option = self.params.get("clusterMethod+")
        
        if self.params.get('clusterCase') == 'use pair distance':
            self.handlePairDistance(genome, tracks, track_names, clusterMethod, extra_option)       
        elif self.params.get('clusterCase') == 'use refTracks':
            self.handleReferenceTrack(genome, tracks, track_names, clusterMethod, extra_option )
        elif self.params.get('clusterCase') == 'self feature': #self feature case.
            self.handleSelfFeature(genome, tracks, track_names, clusterMethod, extra_option)    
        else : # regions clustering case
            self.handleRegionClustering(genome, tracks, clusterMethod, extra_option)
            
        #self.collectParamsIntoFile()
    
    def collectParamsIntoFile(self):        
        parameters = GalaxyRunSpecificFile(['run_parameters.html'],self.jobFile) #just collect the parametes used into a file
        p_path = parameters.getDiskPath(True)
        p_output = open(p_path,'w')
        print>>p_output, '<html><body>'
        print>>p_output, '<ol>'
        for key in self.params.keys():
            print>>p_output, '<li>%s:%s </li>'%(key,self.params[key])
        print>>p_output, '</body></html>'
        p_output.close()
        print parameters.getLink('Parameters of this run')
    
        
        
    def trackPrepare(self, inputTracks, genome) : #just filter out the -- All subtypes -- tag if it exists
        output = []
        for track in inputTracks :
            if isinstance(track, basestring) :
                track = track.split(":")
            if track[-1] == "-- All subtypes --" :
                output.append(track[:-1])
            else :
                output.append(track)
        output = GalaxyInterface._cleanUpTracks(output, genome, realPreProc=True)        
        return output

    def computeDistance(self, genome, track1, track2, feature): #direct distance between track1, track2
        '''
        track1 and track2 are two lists like : ['Sequence','Repeating elements','LINE']
        feature specifies how the distance between track1 and track2 is defined 
        '''
        validFeature = DirectDistanceCatalog.getValidAnalyses(genome, track1, track2)[feature]
        analysisDef = validFeature[0] #'bla bla -> PropFreqOfTr1VsTr2Stat' #or any other statistic from the HB collection
        if self.params.get("compare_in") == "Chromosomes" :
            regSpec = "__chrs__"
            binSpec = self.params.get("Chromosomes")
        elif self.params.get("compare_in") == "Chromosome arms" :
            regSpec = "__chrArms__"
            binSpec = self.params.get("Chromosome_arms")
        elif self.params.get("compare_in") == "Cytobands" :
            regSpec = "__chrBands__"
            binSpec = self.params.get("Cytobands")
        else :
            regSpec = self.params.get("region")
            binSpec = self.params.get("binsize")
        #regSpec = 'chr1' #could also be e.g. 'chr1' for the whole chromosome or '*' for the whole genome
        #binSpec = '10m' #could also be e.g.'100', '1k' or '*' for whole regions/chromosomes as bins 
        #genome = 'hg18' # path /../../..../genome
        #allRepeats = GalaxyInterface.getSubTrackNames(genome,['Sequence','Repeating elements'],False)
        #GalaxyInterface.run(trackName1, trackName2, question, regSpec, binSpec, genome='hg18')
        userBinSource = GalaxyInterface._getUserBinSource(regSpec,binSpec,genome)
        
        result = AnalysisDefJob(analysisDef, track1, track2, userBinSource).run()
        #result er av klassen Results..
        #from gold.result.Results import Results

        mainResultDict = result.getGlobalResult()
        #from PropFreqOfTr1VsTr2Stat:...
        #self._result = {'Track1Prop':ratio,'CountTrack1':c1, 'CountTrack2':c2,'Variance':variance}

        #mainValueOfInterest = mainResultDict['Variance']
        return mainResultDict[validFeature[1]]

    def constructDistMatrix(self, genome, tracks, feature, extra_feature="default"): #construct the distance matrix used in pair_distance case
        '''
        Need the use of extra_feature because the intersect/union ratio cannot be used as the distance between tracks.
        But the (cov. por. intersection) over (cov. por1 * cov. por2) ratio can be directly used as the distance
        '''
        l = len(tracks)
        matrix = np.zeros((l,l))
        for i in range(l) :
            for j in range(l):
                if i < j :
                    if extra_feature == "1 minus the ratio" :
                        matrix[i,j] = 1 - self.computeDistance(genome, tracks[i], tracks[j], feature)
                        matrix[j,i] = matrix[i,j]
                    elif extra_feature == "1 over the ratio" :
                        matrix[i,j] = 1/self.computeDistance(genome, tracks[i], tracks[j], feature)
                        matrix[j,i] = matrix[i,j]
                    else :
                        matrix[i,j] = self.computeDistance(genome, tracks[i], tracks[j], feature)
                        matrix[j,i] = matrix[i,j] 
        return matrix

    def extract_feature(self, genome, track, ref, option) : 
        '''
        this function return the relation of clusterTrack to referenceTrack
        option is the statistical function used, should be named feature
        track, ref is clusterTrack and referenceTrack
        '''
        validFeature = FeatureCatalog.getFeaturesFromTracks(genome,track,ref)[option] #validFeature contains analysisDef and the key to get the needed number from the global result
        if option == 'Prop. of tr1-points falling inside segments of tr2' and self.getTrackFormat(genome, track) in ['Segments', 'Valued segments'] :
            analysisDef = 'dummy [tf1=SegmentToMidPointFormatConverter] -> DerivedPointCountsVsSegsStat'
        else :    
            analysisDef = validFeature[0] #or any other statistic from the HB collection
        if self.params.get("compare_in") == "Chromosomes" :
            regSpec = "__chrs__"
            binSpec = self.params.get("Chromosomes")
        elif self.params.get("compare_in") == "Chromosome arms" :
            regSpec = "__chrArms__"
            binSpec = self.params.get("Chromosome_arms")
        elif self.params.get("compare_in") == "Cytobands" :
            regSpec = "__chrBands__"
            binSpec = self.params.get("Cytobands")
        else :
            regSpec = self.params.get("region")
            binSpec = self.params.get("binsize")
        #regSpec = self.params.get("region")
        #binSpec = self.params.get("binsize")
        #regSpec = 'chr1' #could also be e.g. 'chr1' for the whole chromosome or '*' for the whole genome
        #binSpec = '10m' #could also be e.g.'100', '1k' or '*' for whole regions/chromosomes as bins 
        #genome = 'hg18'
        userBinSource = GalaxyInterface._getUserBinSource(regSpec,binSpec,genome)
        if option == 'Prop. of tr2 covered by tr1' : #because the confuse of refTrack and clusterTrack in this statistics
            result = AnalysisDefJob(analysisDef, ref, track, userBinSource).run()
        else :
            result = AnalysisDefJob(analysisDef, track, ref, userBinSource).run()
        mainResultDict = result.getGlobalResult()
        return mainResultDict[validFeature[1]]
        #return mainResultDict['1inside2']

    
    def construct_feature_matrix_using_reftracks(self, genome, cTracks, rTracks, options) : #rTracks and options has the same length 
        c = len(cTracks)
        r = len(rTracks)
        output = np.zeros((c, r))
        for i in range(c) :
            for j in range(r) :
                output[i,j] = self.extract_feature(genome,cTracks[i],rTracks[j],options[j])
        return output
    
    def getRegAndBinSpec(self):
        if self.params.get("compare_in") == "Chromosomes" :
            regSpec = "__chrs__"
            binSpec = self.params.get("Chromosomes")
        elif self.params.get("compare_in") == "Chromosome arms" :
            regSpec = "__chrArms__"
            binSpec = self.params.get("Chromosome_arms")
        elif self.params.get("compare_in") == "Cytobands" :
            regSpec = "__chrBands__"
            binSpec = self.params.get("Cytobands")
        else :
            regSpec = self.params.get("region")
            binSpec = self.params.get("binsize")
        return regSpec, binSpec
        

    def getTrackFormat(cls,genome,trackName) : #trackName here is a list of directories which is path of track
        #temp = trackName.split(":")
        temp = trackName
        if temp[-1] == "-- All subtypes --" :
            trackName = temp[:-1]
        else :
            trackName = temp
        #trackName = self.trackPrepare(trackName)
        return TrackInfo(genome,trackName).trackFormatName
                
        
    def getValidFeatures(self,genome,ctrack,rtrack): #valid feature for every pair ctrack, rtrack
        return FeatureCatalog.getFeaturesFromTracks(genome,ctrack,rtrack)
        
    def getDirectDistanceFeatures(self, genome, ctrack1, ctrack2) : #used in direct distance case
        return DirectDistanceCatalog.getValidAnalyses(genome, ctrack1, ctrack2)
    
    def getLocalResultsAsFeaturesCatalog(self,genome, ctrack):
        return LocalResultsAsFeaturesCatalog.getValidAnalyses(genome, ctrack, [])
    
    def getExpandedTrackNameFromInTrackName(self, inTrackName, outTrackName,uniqueStaticId, genome, upFlank, downFlank):
        GalaxyInterface.expandBedSegmentsFromTrackName(inTrackName, outTrackName, uniqueStaticId, genome, upFlank, downFlank)
        return outTrackName
    
def getController(transaction = None, job = None):
    return ClusteringToolController(transaction, job)
