<%!
import sys
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui


def _disabled(opt, sel):
    return ' disabled="disabled" ' if opt != sel else ''

%>
<%
#reload(gui)

galaxy = gui.GalaxyWrapper(trans)

params = galaxy.params

genomes = hyper.getAllGenomes(galaxy.getUserName())
genome = params.get('dbkey', genomes[0][1])
genomeElement = gui.SelectElement('dbkey', genomes, genome)

intensityname = params.get('intensityname', '')
numctrltracks = int(params.get('numctrltracks', '1'))
create_as = params.get('create_as', 'history')

try:
    datasets = galaxy.getHistory(hyper.getSupportedGalaxyFileFormats())
except:
    datasets = []

mainTrack = gui.TrackWrapper('track1', hyper, [], galaxy, datasets, genome)
mainTrack.legend = 'Main track'
mainTrack.fetchTracks()
valid = mainTrack.selected()

ctrlTracks = [None] * numctrltracks

try:
    datasets = galaxy.getHistory(hyper.getSupportedGalaxyFileFormatsForFunction())
except:
    datasets = []

for i in range(len(ctrlTracks)):
    ctrlTracks[i] = gui.TrackWrapper('track' + str(i+2), hyper, [], galaxy, datasets, genome)
    ctrlTracks[i].fetchTracks()
    ctrlTracks[i].legend = 'Control track ' + str(i+1)
    valid = valid and ctrlTracks[i].selected()


formAction = ''

if valid:
    formAction = h.url_for('/tool_runner')

%>
<%namespace name="functions" file="functions.mako" />

<%inherit file="base.mako"/>

<%def name="title()">Generate intensity track for confounder handling</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
    </script>
</%def>

<form method="post" action="${formAction}">


<p>
##    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}    
    ${functions.genomeChooser(galaxy, genomeElement, genome)}
</p>

${functions.trackChooser(mainTrack, 0, params)}

%for ti in range(len(ctrlTracks)):
    ${functions.trackChooser(ctrlTracks[ti], ti + 1, params)}
%endfor

<p>
    <input type="hidden" name="numctrltracks" value="${numctrltracks}">
    <input type="button" id="newtrackbtn" value="Add another control track" onclick="with(form){numctrltracks.value ++;action='';submit();}">
</p>
        <fieldset><legend>Binning options</legend>
        
            <%include file="binoptions.mako" args="galaxy=galaxy,gui=gui,hyper=hyper,genome=genome,
                updateRunDescription=False,track1=mainTrack,track2=ctrlTracks[0]"/>
        
        </fieldset>

%if hyper.userHasFullAccess(galaxy.getUserName()):    
    <fieldset><legend>Intensity track</legend>

    <label>Generate intensity track as: <select name="create_as" onchange="with($('#input_name')){if(this.selectedIndex==1)show();else hide()}">
        <option value="history" ${gui.selected(create_as, 'history')}>History element</option>
        <option value="track" ${gui.selected(create_as, 'track')}>HyperBrowser track</option>
        </select></label>
    <br>
    <label id="input_name" ${'style="display:none"' if create_as == 'history' else ''}>Name: <input size="50" name="intensityname" value="${intensityname}"></label>
    </fieldset>
%endif

    <p><input id="start" type="submit" value="Generate track" ${_disabled(valid, True)}></p>

    <INPUT TYPE="HIDDEN" NAME="mako" VALUE="intensity">
    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_intensity">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

    %if params.has_key('setparams'):
    <script type="text/javascript">
      $(document).ready(function () { with (document.forms[0]) { action='?'; submit(); }});
    </script>
    %endif
    
</form>

<%def name="toolHelp()">

<button onclick="location.href='${h.url_for("hyper?mako=intensity&tool_id=hb_intensity&setparams=1&dbkey=sacCer1&numctrltracks=2&track1=Genes%20and%20gene%20subsets%3AExon%20boundaries%3ALefts&track2=Sequence%3AGC%20content%3ASliding%20window%3ALeft%20100bps%20triangular&track3=Sequence%3AGC%20content%3ASliding%20window%3ARight%20100bps%20triangular&method=__chrs__&__chrs__=*&sepFilePrRegion=1")}'">Fill out demo selections</button>
<hr/ class='space'>

The Genomic HyperBrowser only does hypothesis testing on up to two tracks at at time. In order to take any confounding tracks into account, the concept of intensity tracks were invented. This tool is used to generate such tracks.

An intensity track is basicly a function track that provides a probability score to each basepair. Intensity tracks regulate the randomization of one track, and is therefore connected to a particular track that will be analyzed. One or more control tracks must then be selected. These are the possible confounding tracks that needs to be controlled for.

<hr class='space'>
<b>Genome build</b>
<p>Choose the Genome build for the track where you want to do the analysis. The track list will update accordingly</p>

<hr class='space'>
<b>Main track</b>
<p>Select the track that you want to make an intensity track for.</p>

<hr class='space'>
<b>Control track 1</b>
<p>Select a track that you want to control for. Presently, only function tracks can be selected.</p>

<hr class='space'>
<b>Add another control track</b>
<p>Pressing this, presents a selection box where you can select another track to control for. You can control for as many tracks as needed.</p>

<hr class='space'>
<b>Extract options</b>
<p>Define which regions of the track where you want to generate an intensity track, e.g. where you want to do the analysis. There are several options:
<ul>
<li><i>Chromosomes:</i> Any or all complete chromosomes of the genome
<li><i>Chromosome arms:</i> Any or all complete chromosome arms (excluding centromers) of the genome
<li><i>Cytobands:</i> Any or all complete cytobands of the genome
<li><i>Genes (Ensembl):</i> Any or all Ensembl genes in the genome
<li><i>Custom specification:</i> Any consecutive region of the genome, divided into equal-sized bins
<li><i>Bins from history:</i> Use the regions defined in a history element (either BED of wig-format)
</ul>
<i>All options may not be available for all genomes or tracks</i></p>

<hr/ class='space'>
<b>Example</b>
<p><a href="u/hb-superuser/p/creating-intensity-curves-to-control-for-confounders" target=_top>See full example</a> of how to use this tool.</p>
</%def>

