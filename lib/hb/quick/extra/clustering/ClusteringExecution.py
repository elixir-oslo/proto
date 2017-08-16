import numpy as np

from gold.description.TrackInfo import TrackInfo
from gold.result.HeatmapPresenter import HeatmapFromNumpyPresenter
from gold.result.Results import Results
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.extra.clustering.FeatureCatalog import DirectDistanceCatalog, FeatureCatalog, \
    LocalResultsAsFeaturesCatalog
from quick.util.CommonFunctions import silenceRWarnings


#import rpy2.robjects.numpy2ri as rpyn

class ClusteringExecution(object):
    @classmethod
    def _clusterAndPlotDendrogram(cls, figurePath, method, distVar, matrixVar, rowNames):
        ##TEMP DEBUG..
        #DebugRObj = GalaxyRunSpecificFile(['debug.obj'], galaxyFn)
        #r('rsave <- function(f){save(d,file=f)}')
        #r.rsave(DebugRObj.getDiskPath(True))
        ##TEMP DEBUG END
        from proto.RSetup import r
        silenceRWarnings()

        r('library(flashClust)')

        # A device is needed to calculate the correct width and height
        r('pdf("%s", width=100, height=100)' % figurePath)

        r.assign('extra_option', method)
        r('hr <- hclust(%s, method=extra_option, members=NULL)' % distVar)
        r('hr$height <- hr$height/max(hr$height)*10')

        longestRowName = max(zip((len(_) for _ in rowNames), rowNames))[1]
        r('pdf_width=dim(%s)[1] * (strheight("%s", units="inches") + (0.4/2.54)) + par("mai")[2] + par("mai")[4]' % (matrixVar, longestRowName))
        r('pdf_height=max(hr$height)/2.54 + strwidth("%s", units="inches") + par("mai")[1] + par("mai")[3]' % longestRowName)

        r('dev.off()')

        r('pdf("%s" , width=pdf_width, height=pdf_height)' % figurePath)
        r('plot(hr, ylab="Distance", hang=-1)')
        r('dev.off()')

    @classmethod
    def executeSelfFeature(cls, genome, tracks, track_names, clusterMethod, extra_option, feature, distanceType, kmeans_alg, galaxyFn, regSpec, binSpec):
        
        from proto.RSetup import r
        #regSpec, binSpec = 'bed', '/usit/invitro/data/galaxy/galaxy-dist-hg-dev/./database/files/017/dataset_17084.dat'
        silenceRWarnings()

        jobFile = open(galaxyFn, 'w')
#         print>>jobFile, 'PARAMS: ', dict(zip('genome, tracks, track_names, clusterMethod, extra_option, feature, distanceType, kmeans_alg, regSpec, binSpec'.split(','), [repr(v)+'<br>'for v in [genome, tracks, track_names, clusterMethod, extra_option, feature, distanceType, kmeans_alg,regSpec, binSpec]])), '<br><br>'
        batchRun = GalaxyRunSpecificFile(['batch_run_job.txt'], galaxyFn)
        print>>jobFile, '<h3>Results for the "similarity of positional distribution along the genome" way of clustering<h3/><br/><br/>'
        with open(batchRun.getDiskPath(ensurePath=True),'w') as  batchFile:
            print>>batchFile, '$clusterBySelfFeature', (genome, '$'.join([':'.join(t) for t in tracks]), ':'.join(track_names)  , clusterMethod, extra_option, feature, distanceType, kmeans_alg, regSpec, binSpec)
        print>>jobFile, batchRun.getLink('View batch script line for this analysis<br/>')
        #print>>jobFile, 'Batch script syntax for this analysis:<br>$clusterBySelfFeature', (genome, '$'.join([':'.join(t) for t in tracks]), ':'.join(track_names)  , clusterMethod, extra_option, feature, distanceType, kmeans_alg, regSpec, binSpec), '<br><br>'
        #print>>jobFile, 'signature of method clusterBySelfFeature:<br>', 'clusterBySelfFeature(genome, tracksStr, track_namesStr, clusterMethod, extra_option, feature, distanceType, kmeans_alg, regSpec, binSpec):<br><br><br>'
        prettyTrackNames = [v[-1].replace('RoadMap_','').replace('.H3K4me1','') for v in tracks]
        #prettyTrackNames = [prettyPrintTrackName(v, shortVersion=True) for v in tracks]
        f_matrix = cls.construct_feature_matrix(genome, tracks, feature, regSpec, binSpec)
        #print>>jobFile, 'dir f_matrix: ', dir(f_matrix), regSpec, binSpec
        userBinSource = GalaxyInterface._getUserBinSource(regSpec,binSpec,genome)
        binNames = [str(bin)  for binIndex, bin in enumerate(sorted(list(userBinSource)))]
        if len(binNames) != f_matrix.shape[1]:
            binNames = ['Microbin'+str(i) for i in range(f_matrix.shape[1])]
        r.assign('bin_names',binNames)
        r.assign('track_names',prettyTrackNames) #use as track names, will be shown in clustering figure
        r.assign('f_matrix',f_matrix)
        r.assign('distanceType',distanceType)
        r('row.names(f_matrix) <- track_names')
        r('colnames(f_matrix) <- bin_names')

        if clusterMethod == 'Hierarchical clustering' and extra_option != "--select--" :
            #print 'galaxyFn: ', galaxyFn
            figure = GalaxyRunSpecificFile(['cluster_tracks_result_figure.pdf'], galaxyFn)
            figurepath = figure.getDiskPath(ensurePath=True)
            r('d <- dist(f_matrix, method=distanceType)')
            distTable = r('d')
            distMatrix = GalaxyRunSpecificFile(['distance_matrix_result.txt'], galaxyFn)
            distMatrixPath = distMatrix.getDiskPath(True)
            open(distMatrixPath,'w').write(str(distTable))
            print>>jobFile, distMatrix.getLink('View the distance matrix for this analysis <br>')
            #with open(distMatrixPath,'w') as distObj:
            #    #distTable = d_matrix.tolist()
            #    core = HtmlCore()
            #    core.tableHeader(['']+track_names,firstRow=True)
            #    rowSize = len(track_names)
            #    index=0
            #    while index<len(distTable):
            #        core.tableLine([track_names[index % rowSize]]+[str(v) for v in distTable[index:index+rowSize]])
            #    #for index, row in enumerate(distTable):
            #    #    core.tableLine([track_names[index]]+[str(v) for v in row])
            #    core.tableFooter()
            #    print>>distObj, str(core)
            #print>>jobFile, distMatrix.getLink('View the distance matrix for this analysis <br>')

            if True:#f_matrix.shape[1] <= 100:
                r_f_matrixFile = GalaxyRunSpecificFile(['f-matrix.robj'], galaxyFn)
                #', '.join([str(v) for v in row])
                r.assign('f_matrix_fn', r_f_matrixFile.getDiskPath(True))
                r('dput(f_matrix, f_matrix_fn)')
                #r_f_matrixFile.writeTextToFile(', '.join(cls.getFlattenedMatrix(f_matrix)) + '\n\nTrack names: '+', '.join(prettyTrackNames)+'\n\nNumber of tracks: '+str(len(prettyTrackNames))+'\n\nbins: +)
                #r_f_matrixFile.writeTextToFile()
                #r_f_matrixFile.writeTextToFile(str(f_matrix)+'\n\n'+str(r.d))
                print>>jobFile, r_f_matrixFile.getLink('Access the R-representation of the Feature_matrix (text-file)'), '<br/>'

            cls._clusterAndPlotDendrogram(figurepath, extra_option, 'd', 'f_matrix', prettyTrackNames)
            print>>jobFile, figure.getLink('View the clustering tree (dendrogram) for this analysis<br>')

            if True:#f_matrix.shape[1] <= 100:
                #heatmap = GalaxyRunSpecificFile(['heatmap_figure.pdf'], galaxyFn)
                #baseDir = os.path.dirname(heatmap.getDiskPath(True))

                resDict = Results([],[],'')
                resDict.setGlobalResult({'result':{'Matrix':f_matrix, 'Rows':np.array(track_names), 'Cols':np.array(binNames), 'Significance':None, 'RowClust':r('hr'), 'ColClust':None}})
                header = 'View the resulting heatmap plot <br>'

                baseDir = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()
                heatPresenter = HeatmapFromNumpyPresenter(resDict, baseDir, header, printDimensions=False)
                print>>jobFile, heatPresenter.getReference('result')

                #heatmap = GalaxyRunSpecificFile(['heatmap_figure.pdf'], galaxyFn)
                #heatmap_path = heatmap.getDiskPath(True)
                #r.pdf(heatmap_path)
                ##cm.colors(256)
                #r.library("gplots")
                #r('heatmap(f_matrix, col=redgreen(75), distfun=function(c) dist(c, method=distanceType), hclustfun=function(c) hclust(c, method=extra_option, members=NULL),Colv=NA, scale="none", xlab="", ylab="", cexRow=0.5, cexCol=0.5, margin=c(8,10))')#Features cluster tracks
                #r('dev.off()')
                ##print>>jobFile, r('dimnames(f_matrix)')
                #print>>jobFile, heatmap.getLink('View the resulting heatmap plot <br>')
            else:
                print>>jobFile, 'Heatmap not generated due to large size ', f_matrix.shape
        elif clusterMethod == 'K-means clustering' and extra_option != "--select--" and kmeans_alg != "--select--":
            textFile = GalaxyRunSpecificFile(['result_of_kmeans_clustering.txt'], galaxyFn)
            textFilePath = textFile.getDiskPath(True)
            extra_option = int(extra_option)
            r.assign('kmeans_alg',kmeans_alg)
            r.assign('extra_option',extra_option)

            r('hr <- kmeans(f_matrix,extra_option,algorithm=kmeans_alg)') #the number of cluster is gotten from clusterMethod+ tag, instead of 3 used here
            r('hr$height <- hr$height/max(hr$height)*10')
            kmeans_output = open(textFilePath,'w')
            clusterSizes = r('hr$size') #size of every cluster
            withinSS = r('hr$withinss')
            clusters = r('hr$cluster')
            for index1 in range(extra_option) : #extra_option actually the number of clusters
               #trackInCluster = [k for k,val in clusters.items() if val == index1]
               trackInCluster = [k+1 for k,val in enumerate(clusters) if val == index1+1] #IS THIS CORRECT, I.E. SAME AS ABOVE??

               print>>kmeans_output, 'Cluster %i(%s objects) : ' % (index1+1, str(clusterSizes[index1]))
               for name in trackInCluster :
                   print>>kmeans_output, name, '(This result may be a bit shaky afters some changes in rpy access)'

               print>>kmeans_output, 'Sum of square error for this cluster is : '+str(withinSS[index1])+'\n'

            kmeans_output.close()
            print>>jobFile, textFile.getLink('Detailed result of kmeans clustering <br>')

        #cls.print_data(f_matrix, jobFile)
        '''
        feature = self.params.get("self_feature")
        results = self.build_feature_vector(genome, tracks[0], feature)
        vektor = [results[localKey]['Result'] for localKey in sorted(results.keys())]
        print vektor
        '''

    @classmethod
    def construct_feature_matrix(cls, genome, cTracks, option, regSpec, binSpec):
        '''
        option mean how the feature vector is created for every track in cTracks
        this matrix is for the self feature case
        '''

        f_matrix = cls.build_feature_vector(genome, cTracks[0], option, regSpec, binSpec)
        for i in range(1,len(cTracks)) :
            f_matrix = np.vstack((f_matrix,cls.build_feature_vector(genome, cTracks[i], option, regSpec, binSpec)))

        return f_matrix

    @classmethod
    def executePairDistance(cls, genome, tracks, track_names, clusterMethod, extra_option, feature, extra_feature, galaxyFn, regSpec, binSpec):
        from proto.RSetup import r
        silenceRWarnings()
        #jobFile = galaxyFn

        if feature is not None: # must use "" here because the '' does not work

            l = len(tracks)
            d_matrix = np.zeros((l,l))
            for i in range(l) :
                for j in range(l):
                    if i < j :
                        if extra_feature == "1 minus the ratio" :
                            d_matrix[i,j] = 1 - ClusteringExecution.computeDistance(genome, tracks[i], tracks[j], feature, regSpec, binSpec, galaxyFn)
                            d_matrix[j,i] = d_matrix[i,j]
                        elif extra_feature == "1 over the ratio" :
                            d_matrix[i,j] = 1/ClusteringExecution.computeDistance(genome, tracks[i], tracks[j], feature, regSpec, binSpec, galaxyFn)
                            d_matrix[j,i] = d_matrix[i,j]
                        else :
                            d_matrix[i,j] = ClusteringExecution.computeDistance(genome, tracks[i], tracks[j], feature, regSpec, binSpec, galaxyFn)
                            d_matrix[j,i] = d_matrix[i,j]

            jobFile = open(galaxyFn, 'w')
            print>>jobFile, '<h3>Results for the "direct sequence-level similarity" way of clustering<h3/><br/><br/>'
            figure = GalaxyRunSpecificFile(['cluster_tracks_result_figure.pdf'], galaxyFn) #this figure is runspecific and is put in the directory
            distMatrix = GalaxyRunSpecificFile(['distance_matrix_result.html'], galaxyFn)
            distMatrixPath = distMatrix.getDiskPath(True)
            with open(distMatrixPath,'w') as distObj:
                distTable = d_matrix.tolist()
                core = HtmlCore()
                core.tableHeader(['']+track_names,firstRow=True)
                for index, row in enumerate(distTable):
                    core.tableLine([track_names[index]]+[str(v) for v in row])
                core.tableFooter()
                print>>distObj, str(core)


            figurepath = figure.getDiskPath(True)
            #r.pdf(figurepath, 8, 8)
            r.assign('track_names',track_names)
            r.assign('d_matrix', d_matrix)
            r('row.names(d_matrix) <- track_names')

            r('d <- as.dist(d_matrix)')
            if clusterMethod == 'Hierarchical clustering' and extra_option != "--select--" :
                cls._clusterAndPlotDendrogram(figurepath, extra_option, 'd', 'd_matrix', track_names)
                #r.assign('extra_option',extra_option)
                #r('hr <- hclust(d, method=extra_option, members=NULL)')
                #r('hr$height <- hr$height/max(hr$height)*10')
                #r('plot(hr, ylab="Distance", hang=-1)')

            #r('dev.off()')
            batchRun = GalaxyRunSpecificFile(['batch_run_job.txt'], galaxyFn)
            with open(batchRun.getDiskPath(ensurePath=True),'w') as  batchFile:
                print>>batchFile, '$clusterByPairDistance', (genome, '$'.join([':'.join(t) for t in tracks]), ':'.join(track_names)  , clusterMethod, extra_option, feature, extra_feature, regSpec, binSpec)
            print>>jobFile, batchRun.getLink('View batch script line for this analysis <br/>')
            #print>>jobFile, 'Batch script syntax for this analysis:<br>$clusterByPairDistance', (genome, '$'.join([':'.join(t) for t in tracks]), ':'.join(track_names)  , clusterMethod, extra_option, feature, extra_feature, regSpec, binSpec), '<br><br>'
            print>>jobFile, figure.getLink('View the clustering tree (dendrogram) for this analysis <br>')
            print>>jobFile, distMatrix.getLink('View the distance matrix for this analysis <br>')


    @classmethod
    def computeDistance(cls, genome, track1, track2, feature, regSpec, binSpec, galaxyFn=None): #direct distance between track1, track2
        '''
        track1 and track2 are two lists like : ['Sequence','Repeating elements','LINE']
        feature specifies how the distance between track1 and track2 is defined
        '''
        validFeature = DirectDistanceCatalog.getValidAnalyses(genome, track1, track2)[feature]
        analysisDef = validFeature[0] #'bla bla -> PropFreqOfTr1VsTr2Stat' #or any other statistic from the HB collection
        #userBinSource = GalaxyInterface._getUserBinSource(regSpec,binSpec,genome)

        result = GalaxyInterface.runManual([track1, track2], analysisDef, regSpec, binSpec, genome, galaxyFn=galaxyFn)
        #result = AnalysisDefJob(analysisDef, track1, track2, userBinSource).run()
        mainResultDict = result.getGlobalResult()
        return mainResultDict[validFeature[1]]


    @classmethod
    def executeReferenceTrack(cls, genome, tracks, track_names, clusterMethod, extra_option, distanceType, kmeans_alg, galaxyFn, regSpec, binSpec, numreferencetracks=None, refTracks=None, refFeatures=None, yesNo=None, howMany=None, upFlank=None, downFlank=None):
        from proto.RSetup import r
        silenceRWarnings()
        jobFile = open(galaxyFn, 'w')
        print>>jobFile, '<h3>Results for the "similarity of relations to other sets of genomic features" way of clustering<h3/><br/><br/>'
#         print>>jobFile, 'PARAMS: ', dict(zip('genome, tracks, track_names, clusterMethod, extra_option, distanceType, kmeans_alg, regSpec, binSpec'.split(','), [repr(v)+'<br>'for v in [genome, tracks, track_names, clusterMethod, extra_option, distanceType, kmeans_alg, regSpec, binSpec]])), '<br><br>'
        batchRun = GalaxyRunSpecificFile(['batch_run_job.txt'], galaxyFn)
        with open(batchRun.getDiskPath(ensurePath=True),'w') as  batchFile:
            print>>batchFile, '$clusterByReference', (genome, '$'.join([':'.join(t) for t in tracks]), ':'.join(track_names)  , clusterMethod, extra_option, distanceType, kmeans_alg, regSpec, binSpec,numreferencetracks, refTracks, refFeatures, yesNo, howMany, upFlank, downFlank)
        print>>jobFile, batchRun.getLink('View batch script line for this analysis<br/>')

        #print>>jobFile, 'Batch script syntax for this analysis:<br>', '$clusterByReference', (genome, '$'.join([':'.join(t) for t in tracks]), ':'.join(track_names)  , clusterMethod, extra_option, distanceType, kmeans_alg, regSpec, binSpec,numreferencetracks, refTracks, refFeatures, yesNo, howMany, upFlank, downFlank), '<br><br>'
        #print>>jobFile, 'signature of method clusterByReference:<br>', 'clusterByReference(genome, tracksStr, track_namesStr, clusterMethod, extra_option, distanceType, kmeans_alg, regSpec, binSpec, numreferencetracks=None, refTracks=None, refFeatures=None, yesNo=None, howMany=None, upFlank=None, downFlank=None)<br><br><br>'
        prettyTrackNames = [v[-1].replace("RoadMap_","").replace('.H3K4me1','') for v in tracks]

        #prettyTrackNames = [prettyPrintTrackName(v) for v in tracks]
        #paramNames = ['numreferencetracks', 'refTracks', 'refFeatures', 'yesNo', 'howMany', 'upFlank', 'downFlank']
        #for index, value in enumerate([numreferencetracks, refTracks, refFeatures, yesNo, howMany, upFlank, downFlank]):
        #    if value != None:
        #        print paramNames[index]+'='+ str(value),
        #print ''

        reftrack_names = [] #for use in creating the heatmap (as the column names)

        options = [] #for the case using refTracks, options contains feature for every refTrack, chosen by user.

        if numreferencetracks :
            for i in range(int(numreferencetracks)):
                ref_i = refTracks[i].split(":") #name of refTrack is being used to construct the name of expanded refTrack
                #refTracks.append(ref_i) #put the refTrack into refTracks list
                reftrack_names.append(ref_i[-1])
                temp_opt1 = 'ref'+str(i)+'feature'
                options+= [] if refFeatures[i] == None else [refFeatures[i]]
                if  yesNo[i] == "Yes" and howMany[i] != '--select--':
                    for expan in range(int(howMany[i])) :
                        reftrack_names.append(ref_i[-1]+'_'+ upFlank[i][expan])
                        upFlank = int(upFlank[i][expan])
                        downFlank = int(downFlank[i][expan])
                        withinRunId = str(i+1)+' expansion '+str(expan + 1)
                        outTrackName = GalaxyInterface.expandBedSegmentsFromTrackNameUsingGalaxyFn(ref_i, genome, upFlank, downFlank, galaxyFn, withinRunId) #outTrackName is unique for run
                        refTracks.append(outTrackName) #put the expanded track into refTracks list
                        options.append(options[-1]) # use chosen feature for refTack as valid feature for the expanded

            for index, track in enumerate(refTracks) :
                #print track, '<br>'
                if isinstance(track, basestring) :
                    track = track.split(":")
                refTracks[index] = track[:-1] if track[-1] == "-- All subtypes --" else track

        if len(refTracks) > 0:

            trackFormats = [TrackInfo(genome,track).trackFormatName for track in tracks]

            trackLen = len(tracks)
            refLen = len(refTracks)
            f_matrix = np.zeros((trackLen, refLen))
            for i in range(trackLen):
                for j in range(refLen):
                    #print 'len(options), refLen, len(tracks), trackLen, len(trackFormats):', len(options), refLen, len(tracks), trackLen, len(trackFormats)
                    f_matrix[i,j] = cls.extract_feature(genome,tracks[i],refTracks[j],options[j], regSpec, binSpec, trackFormats[i])
            r.assign('track_names',prettyTrackNames) #use as track names, will be shown in clustering figure
            r.assign('reftrack_names',reftrack_names)
            r.assign('f_matrix',f_matrix)
            r.assign('distanceType',distanceType)
            r('row.names(f_matrix) <- track_names')
            r('colnames(f_matrix) <- reftrack_names')

            if clusterMethod == 'Hierarchical clustering' and extra_option != "--select--":
                figure = GalaxyRunSpecificFile(['cluster_tracks_result_figure.pdf'], galaxyFn)
                figurepath = figure.getDiskPath(True)
                #r.pdf(figurepath, 8,8)
                r('d <- dist(f_matrix, method=distanceType)')
                distTable = r('d')
                distMatrix = GalaxyRunSpecificFile(['distance_matrix_result.txt'], galaxyFn)
                distMatrixPath = distMatrix.getDiskPath(True)
                open(distMatrixPath,'w').write(str(distTable))
                print>>jobFile, distMatrix.getLink('View the distance matrix for this analysis <br>')

                #with open(distMatrixPath,'w') as distObj:
                #    #distTable = d_matrix.tolist()
                #    core = HtmlCore()
                #    core.tableHeader(['']+track_names,firstRow=True)
                #    rowSize = len(track_names)
                #    index=0
                #    while index<len(distTable):
                #        core.tableLine([track_names[index % rowSize]]+[str(v) for v in distTable[index:index+rowSize]])
                #    core.tableFooter()
                #    print>>distObj, str(core)
                #print>>jobFile, distMatrix.getLink('View the distance matrix for this analysis <br>')
                #print r.f_matrix
                #print r.d

                r_f_matrixFile = GalaxyRunSpecificFile(['f-matrix.robj'], galaxyFn)
                r.assign('f_matrix_fn', r_f_matrixFile.getDiskPath(True))
                r('dput(f_matrix, f_matrix_fn)')
                print>>jobFile, r_f_matrixFile.getLink('Access the R-representation of the Feature_matrix (text-file) <br>'),

                #r_f_matrixFile = GalaxyRunSpecificFile(['f-matrix.txt'], galaxyFn)
                #r_f_matrixFile.writeTextToFile(str(f_matrix)+'\n\n'+str(r.d))
                #print>>jobFile, r_f_matrixFile.getLink('r.f_matrix & r.d <br>')

                cls._clusterAndPlotDendrogram(figurepath, extra_option, 'd', 'f_matrix', prettyTrackNames)
                #r.assign('extra_option',extra_option)
                #r('hr <- hclust(d, method=extra_option, members=NULL)')
                #r('hr$height <- hr$height/max(hr$height)*10')
                #r('plot(hr, ylab="Distance", hang=-1)')
                #
                #r('dev.off()')
                print>>jobFile, figure.getLink('View the clustering tree (dendrogram) for this analysis<br>')
            elif clusterMethod == 'K-means clustering' and extra_option != "--select--" and kmeans_alg != "--select--":
                textFile = GalaxyRunSpecificFile(['result_of_kmeans_clustering.txt'], galaxyFn)
                textFilePath = textFile.getDiskPath(True)
                extra_option = int(extra_option)
                r.assign('extra_option',extra_option)
                r.assign('kmeans_alg',kmeans_alg)
                r('hr <- kmeans(f_matrix,extra_option,algorithm=kmeans_alg)') #the number of cluster is gotten from clusterMethod+ tag, instead of 3 used here
                r('hr$height <- hr$height/max(hr$height)*10')
                kmeans_output = open(textFilePath,'w')
                clusterSizes = r('hr$size') #size of every cluster

                withinSS = r('hr$withinss')
                clusters = np.array(r('hr$cluster')) #convert to array in order to handle the index more easily
                track_names = np.array(track_names)
                for index1 in range(extra_option) : #extra_option actually the number of clusters
                    trackInCluster = [k for k,val in clusters.items() if val == index1]

                    print>>kmeans_output, 'Cluster %i(%s objects) : ' % (index1+1, str(clusterSizes[index1]))
                    for name in trackInCluster :
                        print>>kmeans_output, name

                    print>>kmeans_output, 'Sum of square error for this cluster is : '+str(withinSS[index1])+'\n'
                kmeans_output.close()
                print>>jobFile, textFile.getLink('Detailed result of kmeans clustering <br>')

            #heatmap = GalaxyRunSpecificFile(['heatmap_figure.pdf'], galaxyFn)
            #baseDir = os.path.dirname(heatmap.getDiskPath(True))
            ##r.png(heatmap_path, width=800, height=700)

            resDict = Results([],[],'ClusTrack')
            resDict.setGlobalResult({'result':{'Matrix':f_matrix, 'Rows':np.array(track_names), 'Cols':np.array(reftrack_names), 'Significance':None, 'RowClust':r('hr'), 'ColClust':None}})
            header = 'Heatmap of Feature matrix for "similarity of positional distribution along the genome" '

            baseDir = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()
            heatPresenter = HeatmapFromNumpyPresenter(resDict, baseDir, header, printDimensions=False)

            print>>jobFile, heatPresenter.getReference('result')
            #r.pdf(heatmap_path)
            #r.library("gplots")
            #r('heatmap(f_matrix, col=redgreen(75), Colv=NA, scale="none", xlab="", ylab="", margins=c(10,10))')#Features cluster tracks
            #r('dev.off()')

            #print>>jobFile, heatmap.getLink('View the resulting heatmap plot <br>')
            #cls.print_data(f_matrix, jobFile)

        else :
            print 'Have to specify a set of refTracks'

    @classmethod
    def extract_feature(cls, genome, track, ref, option, regSpec, binSpec, trackFormat) :
        #print 'genome, track, ref, option, regSpec, binSpec, trackFormat: ', genome, track, ref, option, regSpec, binSpec, trackFormat
        #featureKeys = FeatureCatalog.getFeaturesFromTracks(genome,track,ref).keys()
        #logMessage('ClusterExecution (extract_feature) track og refTrack = ('+ repr(track)+'  #####  '+repr(ref))
        #logMessage('ClusterExecution (extract_feature) featureKeys = '+ repr(featureKeys))
        validFeature = FeatureCatalog.getFeaturesFromTracks(genome,track,ref)[option] #validFeature contains analysisDef and the key to get the needed number from the global result
        if option == 'Prop. of tr1-points falling inside segments of tr2' and trackFormat in ['Segments', 'Valued segments'] :
            analysisDef = 'dummy [tf1=SegmentToMidPointFormatConverter] -> DerivedPointCountsVsSegsStat'
        else :
            analysisDef = validFeature[0] #or any other statistic from the HB collection

        #userBinSource = GalaxyInterface._getUserBinSource(regSpec,binSpec,genome)
        result = GalaxyInterface.runManual([ref, track], analysisDef, regSpec, binSpec, genome, printResults=False, printProgress=False, printHtmlWarningMsgs=False,  printRunDescription=False)
        #result = AnalysisDefJob(analysisDef, ref, track, userBinSource).run() if option == 'Prop. of tr2 covered by tr1' else AnalysisDefJob(analysisDef, track, ref, userBinSource).run()

        validAnalysisDef = validFeature[1]
        assert result.getGlobalResult() is not None, 'Did not get any global result for analysisDef: '+validAnalysisDef
        return result.getGlobalResult()[validAnalysisDef]

    @staticmethod
    def build_feature_vector(genome, ctrack, feature, regSpec, binSpec):
        '''
        this function create a feature vector for ctrack
        feature specifies how the vector is constructed
        '''
        #print 'TEMP1:', ctrack, '<br>', LocalResultsAsFeaturesCatalog.getValidAnalyses(genome, ctrack, []),'<br>'
        #validFeature = LocalResultsAsFeaturesCatalog.getValidAnalyses(genome, ctrack, [])[feature]
        validFeature = LocalResultsAsFeaturesCatalog.getAllFeatures()[feature]
        analysisDef = validFeature[0]
        #regSpec = self.params.get("region")
        #binSpec = self.params.get("binsize")
        #userBinSource = GalaxyInterface._getUserBinSource(regSpec,binSpec,genome)

        #result = GalaxyInterface.runManual([ctrack], analysisDef, regSpec, binSpec, genome, printResults=False, printProgress=False)
        #result = AnalysisDefJob(analysisDef, ctrack, [], userBinSource).run()
        if validFeature[1] == 'Microbins':
            microBinConfig = 'extraDummy [microBin=%i] ' % int(binSpec.replace('k','000').replace('m','000000') )
            analysisDef = microBinConfig + analysisDef
            result = GalaxyInterface.runManual([ctrack], analysisDef, regSpec, '*', genome, printResults=False, printProgress=False)
            res = result.getGlobalResult()['Result']
            return res
        else:
            result = GalaxyInterface.runManual([ctrack], analysisDef, regSpec, binSpec, genome, printResults=False, printProgress=False)
            return [result[localKey][validFeature[1]] for localKey in sorted(result.keys())]

    @staticmethod
    def getFlattenedMatrix(matrix):
        (t,r) = matrix.shape #t is number of tracks and r is number of references
        resList = []
        for i in range(t):
            for j in range(r):
                resList.append(str(matrix[i,j]))
        return resList

    @staticmethod
    def print_data(matrix, jobFile):
        (t,r) = matrix.shape #t is number of tracks and r is number of references
        for i in range(t):
            for j in range(r):
                print>>jobFile, matrix[i,j],
                print>>jobFile, ", ",
