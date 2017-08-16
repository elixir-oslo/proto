<%!
from cgi import escape
from urllib import quote, unquote

def _disabled(opt, sel):
    return ' disabled="disabled" ' if opt != sel else ''

%>
<%
p = control.params
numclustertracks = int(p.get('numclustertracks', '1'))
numreferencetracks = int(p.get('numreferencetracks','1'))
testparameter = p.get('testparameter', 'default')
region = p.get('region', '*')
binsize = p.get('binsize', '1m')
Chromosomes = p.get('Chromosomes','*')
Chromosome_arms = p.get('Chromosome_arms','*')
Cytobands = p.get('Cytobands','*')

clusterTracks = [None] * numclustertracks
referenceTracks = [None] * numreferencetracks
chosenFeatures = [None] * numreferencetracks ##for the case using refTracks
expansionOpts = [None] * numreferencetracks ##for the expansion of refTracks

valid = numclustertracks >= 1 and p.has_key('clusterCase') ##clusterCase is chosen

for i in range(len(clusterTracks)):
    clusterTracks[i] = control.getTrackElement('track' + str(i+1), 'Track ' + str(i+1),True)
    valid = valid and clusterTracks[i].selected()

clusterCase = p.get('clusterCase', 'default')
if clusterCase == "use refTracks" :
	for i in range(len(referenceTracks)):
	    referenceTracks[i] = control.getTrackElement('reftrack' + str(i+1), 'Reference track ' + str(i+1),True)
	    chosenFeatures[i] = 'ref'+str(i)+'feature'
	    expansionOpts[i] = ['yes_no'+str(i),'how_many'+str(i),'up_down'+str(i)]
	    valid = valid and referenceTracks[i].selected() and p.get(chosenFeatures[i]) != "--select--"
	    if p.get(expansionOpts[i][0]) == "Yes" :
	    	valid = valid and p.get(expansionOpts[i][1]) != "--select--" ## do not work perfectly here
	valid = valid and p.get('distanceType') != "--select--"
elif clusterCase == "use pair distance" :
	valid = valid and p.has_key('pair_feature')
	if p.has_key('pair_feature+') :
		valid = valid and p.get('pair_feature+') != "--select--"  ## again here, one refresh for late
elif clusterCase == "self feature" :
	valid = valid and p.has_key('self_feature')
	valid = valid and p.get('distanceType') != "--select--"
elif clusterCase == "regions clustering" :
	#numreferancetracks = 1
	referenceTracks[0] = control.getTrackElement('reftrack1', 'refTrack1 ',True)
	valid = valid and referenceTracks[0].selected()

valid = valid and p.get('clusterMethod') != "--select--" and p.get('clusterMethod+','--select--') != "--select--"

formAction = ''

if valid:
    formAction = h.url_for('/tool_runner')

%>
<%namespace name="functions" file="functions.mako" />

<%inherit file="base.mako"/>

<%def name="title()">ClusTrack: Cluster tracks based on genome level similarity</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
    </script>
</%def>

<form method="post" action="${formAction}">

## %if control.userHasFullAccess():

<p>
    ${functions.genomeChooser(control)}
</p>

<fieldset><legend>Tracks to cluster</legend>
%for ti in range(len(clusterTracks)):
    ${functions.trackChooser(clusterTracks[ti], ti + 1, p)}
%endfor

<p>
    <input type="hidden" name="numclustertracks" value="${numclustertracks}">
    <input type="button" id="newtrackbtn" value="Add another track to cluster" onclick="with(form){numclustertracks.value ++;action='';submit();}">
</p>
</fieldset>
<p>
    <input type="radio" name="clusterCase" value="self feature" ${'checked' if (p.has_key('clusterCase') and p.get("clusterCase")=="self feature") else ''} onchange="with(form){action='';submit();}">Use similarity of positional distribution along the genome<br>
    <input type="radio" name="clusterCase" value="use refTracks" ${'checked' if (p.has_key('clusterCase') and p.get("clusterCase")=="use refTracks") else ''} onchange="with(form){action='';submit();}">Use similarity of relations to other sets of genomic features<br>
    <input type="radio" name="clusterCase" value="use pair distance" ${'checked' if (p.has_key('clusterCase') and p.get("clusterCase")=="use pair distance") else ''} onchange="with(form){action='';submit();}">Use direct sequence-level similarity<br>
    	<input type="radio" name="clusterCase" value="regions clustering" ${'checked' if (p.has_key('clusterCase') and p.get("clusterCase")=="regions clustering") else ''} onchange="with(form){action='';submit();}">Regions clustering<br>
</p>

%if (p.has_key('clusterCase') and p.get("clusterCase") == "use refTracks") :
<fieldset><legend>Reference tracks & options</legend>
%for ti in range(len(referenceTracks)):
    ${functions.trackChooser(referenceTracks[ti], ti + 1, p)}
    %if (p.has_key('track1') and clusterTracks[0].selected() and p.has_key('reftrack'+str(ti+1)) and referenceTracks[ti].selected()):
		<%
		genome = control.getGenome() ##could also use control.get('dbkey')
		ctrack = clusterTracks[0].definition()
		rtrack = referenceTracks[ti].definition()
		validFeature = control.getValidFeatures(genome, ctrack, rtrack)
		%>
		<%doc>
		Choose feature :
		%if len(validFeature.keys()) == 0 :
			There is not any valid feature for this reference track and cluster track.<br>
		%elif len(validFeature.keys()) == 1 :
			<input type="radio" name=${chosenFeatures[ti]} value="${validFeature.keys()[0]}" 'checked'>${validFeature.keys()[0]}<br>
		%else :
			%for key in validFeature.keys():
	    		<input type="radio" name=${chosenFeatures[ti]} value="${key}" ${'checked' if (p.has_key(chosenFeatures[ti]) and p.get(chosenFeatures[ti])==key) else ''}>${key}<br>
			%endfor
		%endif
		</%doc>
		Choose feature :
		%if len(validFeature.keys()) == 0 :
			There is not any valid feature for this reference track. <br>
		%else :
			<select name="${chosenFeatures[ti]}" onchange="with(form){action='';submit();}">
			<option>--select--</option>
			%for key in validFeature.keys() :
				<option ${'selected' if (p.has_key(chosenFeatures[ti]) and p.get(chosenFeatures[ti])== key) else ''}>${key}</option>
			%endfor
			</select><br>
		%endif
		Expand this reference track, and use as a new reference track :
		<select name="${expansionOpts[ti][0]}" onchange="with(form){action='';submit();}">
			<option 'selected'>No</option>
			<option ${'selected' if (p.has_key(expansionOpts[ti][0]) and p.get(expansionOpts[ti][0])=="Yes") else ''}>Yes</option>
		</select>
		%if p.get(expansionOpts[ti][0]) == "Yes" :
			##<label>how many expansions : <input name="${expansionOpts[ti][1]}" size="1" value="${p.get(expansionOpts[ti][1]) if (p.has_key(expansionOpts[ti][1])) else '1'}"></label>
			How many expansions :
			<select name="${expansionOpts[ti][1]}" onchange="with(form){action='';submit();}">
			<option>--select--</option>
			<option ${'selected' if (p.has_key(expansionOpts[ti][1]) and p.get(expansionOpts[ti][1])=="1") else ''}>1</option>
			<option ${'selected' if (p.has_key(expansionOpts[ti][1]) and p.get(expansionOpts[ti][1])=="2") else ''}>2</option>
			<option ${'selected' if (p.has_key(expansionOpts[ti][1]) and p.get(expansionOpts[ti][1])=="3") else ''}>3</option>
			<option ${'selected' if (p.has_key(expansionOpts[ti][1]) and p.get(expansionOpts[ti][1])=="4") else ''}>4</option>
			<option ${'selected' if (p.has_key(expansionOpts[ti][1]) and p.get(expansionOpts[ti][1])=="5") else ''}>5</option>
			<option ${'selected' if (p.has_key(expansionOpts[ti][1]) and p.get(expansionOpts[ti][1])=="6") else ''}>6</option>
			<option ${'selected' if (p.has_key(expansionOpts[ti][1]) and p.get(expansionOpts[ti][1])=="7") else ''}>7</option>
			</select><br>
			%if	(p.has_key(expansionOpts[ti][1]) and p.get(expansionOpts[ti][1]) != "--select--") :
				%for index in range(int(p.get(expansionOpts[ti][1]))) :
					<label>Upstream : Downstream </label>
					<input name="${str(ti)+'_'+str(index)+'up'}" size="5" value="${p.get(str(ti)+'_'+str(index)+'up') if p.has_key(str(ti)+'_'+str(index)+'up') else '0'}">
					<input name="${str(ti)+'_'+str(index)+'down'}" size="5" value="${p.get(str(ti)+'_'+str(index)+'down') if p.has_key(str(ti)+'_'+str(index)+'down') else '0'}"><br>
				%endfor
			%endif
		%endif
    %endif
    <br>
%endfor

<p>
    <input type="hidden" name="numreferencetracks" value="${numreferencetracks}">
    <input type="button" id="newreftrackbtn" value="Add reference track" onclick="with(form){numreferencetracks.value ++;action='';submit();}">
</p>
</fieldset>
%elif (p.has_key('clusterCase') and p.get("clusterCase") == "use pair distance"):
    <fieldset><legend>Options for pair distance</legend>
    %if (p.has_key('track1') and p.has_key('track2') and clusterTracks[0].selected() and clusterTracks[1].selected()) :
    	<%
		genome = p.get('dbkey')
		ctrack1 = p.get('track1').split(':')
		ctrack2 = p.get('track2').split(':')
		validFeature = {}
		validFeature = control.getDirectDistanceFeatures(genome, ctrack1, ctrack2)
		%>
		%if len(validFeature.keys()) == 0 :
			Could not compute distance between these tracks<br>
		%else :
			%for key in validFeature.keys():
	    		<input type="radio" name="pair_feature" value="${key}" ${'checked' if (p.has_key("pair_feature") and p.get("pair_feature")==key) else ''} onchange="with(form){action='';submit();}">${key}<br>
			%endfor
		%endif
		%if p.has_key("pair_feature") and p.get("pair_feature")=='Ratio of intersection vs union of segments' :
			Distance is :
			<select name="pair_feature+" onchange="with(form){action='';submit();}">
			<option>--select--</option>
			<option ${'selected' if (p.has_key("pair_feature+") and p.get("pair_feature+")=="1 minus the ratio") else ''}>1 minus the ratio</option>
			<option ${'selected' if (p.has_key("pair_feature+") and p.get("pair_feature+")=="1 over the ratio") else ''}>1 over the ratio</option>
			</select>
		%endif

    %else :
    	Tracks to be clustered are not selected.<br>
    %endif
    </fieldset>
%elif (p.has_key('clusterCase') and p.get("clusterCase") == "self feature") :
    <fieldset><legend>Feature calculation options</legend>
    %if (p.has_key('track1') and p.has_key('track2') and clusterTracks[0].selected() and clusterTracks[1].selected()) :
    	<%
		genome = p.get('dbkey')
		ctrack1 = clusterTracks[0].definition()
		#ctrack2 = clusterTracks[1].definition()
		#ctrack1 = p.get('track1').split(':')
		validFeature = {}
		validFeature = control.getLocalResultsAsFeaturesCatalog(genome, ctrack1)
		%>
		%if len(validFeature.keys()) == 0 :
			There is not any relevant feature for this track format<br>
		%else :
			%for key in validFeature.keys():
	    		<input type="radio" name="self_feature" value="${key}" ${'checked' if (p.has_key("self_feature") and p.get("self_feature")==key) else ''} onchange="with(form){action='';submit();}">${key}<br>
			%endfor
		%endif

    %else :
    	Tracks to be clustered are not selected.<br>
    %endif
    </fieldset>

%elif (p.has_key('clusterCase') and p.get("clusterCase") == "regions clustering") :
	${functions.trackChooser(referenceTracks[0],1, p)}
	%if p.has_key('reftrack1') and referenceTracks[0].selected() :
		##${referenceTracks[0].definition()}
		${control.getHistoryTrackDef('reftrack1')}
		##${p.get('reftrack1')}
		${control.getHistoryTrackDef('track1')}
	%endif

%endif

<fieldset><legend>Region & scale</legend>

Compare in :
<select name="compare_in" onchange="with(form){action='';submit();}">
<option>--select--</option>
<option ${'selected' if (p.has_key("compare_in") and p.get("compare_in")=="Chromosomes") else ''}>Chromosomes</option>
<option ${'selected' if (p.has_key("compare_in") and p.get("compare_in")=="Chromosome arms") else ''}>Chromosome arms</option>
<option ${'selected' if (p.has_key("compare_in") and p.get("compare_in")=="Cytobands") else ''}>Cytobands</option>
<option ${'selected' if (p.has_key("compare_in") and p.get("compare_in")=="Custom specification") else ''}>Custom specification</option>
</select>
<br>
%if p.has_key("compare_in") and p.get("compare_in")=="Custom specification" :
	<label>Considering regions : <input name="region" size="20" value="${region}"></label>
	<i>Region specification as in UCSC Genome browser, * means whole genome. k and m denoting thousand and million bps, respectively. Several regions may be specified if separated by comma. If the end position is omitted, it is set equal to the end of the chromosome. Example: chr1:1-20m, chr2:10m-</i><br>
	<label>Bin size :<input name="binsize" size="20" value="${binsize}"></label>
	<i>The selected regions are divided into bins of this size. k and m denoting thousand and million bps, respectively. * means whole region / whole chromosome. E.g. 100k</i><br>
%elif p.has_key("compare_in") and p.get("compare_in")=="Chromosomes" :
	<label>with : <input name="Chromosomes" value="${Chromosomes}"></label>
	<i>comma separated list of chromosomes, * means all (e.g. chr1,chr2)</i>
%elif p.has_key("compare_in") and p.get("compare_in")=="Chromosome arms" :
	<label>with : <input name="Chromosome_arms" value="${Chromosome_arms}"></label>
	<i>comma separated list of chromosome arms, * means all (e.g. chr1p,chr1q,chr2p)</i>
%elif p.has_key("compare_in") and p.get("compare_in")=="Cytobands" :
	<label>with : <input name="Cytobands" value="${Cytobands}"></label>
	<i>comma separated list of cytobands(chromosome bands), * means all (e.g. 1p36.33,1p36.23)</i>
%endif

</fieldset>

<fieldset><legend>Clustering method & options</legend>
%if (p.has_key("clusterCase") and p.get("clusterCase")!="use pair distance"):
	Clustering method :
	<select name="clusterMethod" onchange="with(form){action='';submit();}">
	<option>--select--</option>
	<option ${'selected' if (p.has_key("clusterMethod") and p.get("clusterMethod")=="Hierarchical clustering") else ''}>Hierarchical clustering</option>
	<option ${'selected' if (p.has_key("clusterMethod") and p.get("clusterMethod")=="K-means clustering") else ''}>K-means clustering</option>
	</select>
	%if p.has_key("clusterMethod") and p.get("clusterMethod")=="Hierarchical clustering" :
		Clustering algorithm :
		<select name="clusterMethod+" onchange="with(form){action='';submit();}">
		<option>--select--</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="single") else ''}>single</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="average") else ''}>average</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="complete") else ''}>complete</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="ward") else ''}>ward</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="median") else ''}>median</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="centroid") else ''}>centroid</option>
		</select>
		<br>
		Distance between feature vectors :
		<select name="distanceType" onchange="with(form){action='';submit();}">
		<option>--select--</option>
		<option ${'selected' if (p.has_key("distanceType") and p.get("distanceType")=="euclidean") else ''}>euclidean</option>
		<option ${'selected' if (p.has_key("distanceType") and p.get("distanceType")=="maximum") else ''}>maximum</option>
		<option ${'selected' if (p.has_key("distanceType") and p.get("distanceType")=="manhattan") else ''}>manhattan</option>
		<option ${'selected' if (p.has_key("distanceType") and p.get("distanceType")=="canberra") else ''}>canberra</option>
		<option ${'selected' if (p.has_key("distanceType") and p.get("distanceType")=="binary") else ''}>binary</option>
		<option ${'selected' if (p.has_key("distanceType") and p.get("distanceType")=="minkowski") else ''}>minkowski</option>
		</select><br>
	%elif p.has_key("clusterMethod") and p.get("clusterMethod")=="K-means clustering" :
		Clustering algorithm :
		<select name="kmeans_alg" onchange="with(form){action='';submit();}">
		<option>--select--</option>
		<option ${'selected' if (p.has_key("kmeans_alg") and p.get("kmeans_alg")=="Hartigan") else ''}>Hartigan</option>
		<option ${'selected' if (p.has_key("kmeans_alg") and p.get("kmeans_alg")=="Lloyd") else ''}>Lloyd</option>
		<option ${'selected' if (p.has_key("kmeans_alg") and p.get("kmeans_alg")=="MacQueen") else ''}>MacQueen</option>
		<option ${'selected' if (p.has_key("kmeans_alg") and p.get("kmeans_alg")=="Forgy") else ''}>Forgy</option>
		</select><br>
		Number of clusters :
		<select name="clusterMethod+" onchange="with(form){action='';submit();}">
		<option>--select--</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="2") else ''}>2</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="3") else ''}>3</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="4") else ''}>4</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="5") else ''}>5</option>
		</select>
	%endif
%else :
	Clustring method :
	<select name="clusterMethod" onchange="with(form){action='';submit();}">
	<option>--select--</option>
	<option ${'selected' if (p.has_key("clusterMethod") and p.get("clusterMethod")=="Hierarchical clustering") else ''}>Hierarchical clustering</option>
	</select>
	%if p.has_key("clusterMethod") and p.get("clusterMethod")=="Hierarchical clustering" :
		Clustering algorithm :
		<select name="clusterMethod+" onchange="with(form){action='';submit();}">
		<option>--select--</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="single") else ''}>single</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="average") else ''}>average</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="complete") else ''}>complete</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="ward") else ''}>ward</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="median") else ''}>median</option>
		<option ${'selected' if (p.has_key("clusterMethod+") and p.get("clusterMethod+")=="centroid") else ''}>centroid</option>
		</select>
	%endif
%endif

</fieldset>

    <p><input id="start" type="submit" value="Cluster tracks" ${_disabled(valid, True)}></p>

##%else:
##        <p>You must be one of us to cluster tracks</p>
##
##%endif


    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_clustering">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">
	<INPUT TYPE="HIDDEN" NAME="mako" VALUE="clusteringtool">
</form>

<%def name="toolHelp()">
		<p>This tool is used to investigate relations between multiple tracks in an
		unsupervised manner (a manuscript on the tool has been submitted). The tool
		allows an essentially unlimited number of tracks to be selected, and further
		allows the distance measure to be used for the clustering to be precisely
		specified through selection among a varied set of a notions of track
		similarity.</p>

		<hr>
        <b>Example</b>
        <p><a href="${h.url_for('/u/hb-superuser/p/cluster-tracks')}" target=_top>See full examples</a> of how to use this tool.</p>
</%def>
