<%!
import sys, os
from cgi import escape
from urllib import quote, unquote

import quick.extra.GoogleMapsInterface as gmi


%>
<%
#galaxy = gui.GalaxyWrapper(trans)
#params = galaxy.params


%>
<%inherit file="base.mako"/>
<%def name="title()">View regulomes (list)</%def>

<%def name="linkToMap(map, text)">
    <a href="${gmi.BASE_URL}/${map}">${text}</a>
</%def>

<%def name="linkToTable(map, text)">
    <a href="${gmi.BASE_URL}/${map}/data/Result_table.html">${text}</a>
</%def>

<ul><p><li>The Genomic HyperBrowser allows large-scale regulatory analyses to be performed with ease. 
We have generated several regulomes, where the main result is the 

${linkToMap('final_tfbs_barjoseph_phenopedia_min20_binary_average_euc_0.01_rowsum', 'Differential disease regulome (heatmap)')} 
(and corresponding ${linkToTable('final_tfbs_barjoseph_phenopedia_min20_binary_average_euc_0.01_rowsum', 'result table')}).

The regulome shows how a range of TFs with TF-gene predictions from this <a href='http://genome.cshlp.org/content/20/4/526.long'>paper</a> are over/under-represented in a range of diseases with gene associations retrieved from <a href='http://www.hugenavigator.net/HuGENavigator/startPagePhenoPedia.do'>Phenopedia</a>. The map is normalized differentially for both TFs and diseases. *
</p>

<p><li>The same regulome is also generated in a version that is instead normalized differentially for only TFs

(${linkToMap('final_tfbs_barjoseph_phenopedia_min20_binary_average_euc_0.01_rowcount', 'heatmap')} 
, ${linkToTable('final_tfbs_barjoseph_phenopedia_min20_binary_average_euc_0.01_rowcount', 'result table')}). 
</p>

<p><li>We have also generated regulomes for the same TF predictions, but with diseases-gene associations calculated from the <a href='http://www.coremine.com/medical/'>PubGene</a> database of literature co-citations. The map is normalized differentially in both directions 

(${linkToMap('final_tfbs_barjoseph_diseases_min20_binary_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_tfbs_barjoseph_diseases_min20_binary_average_euc_0.01_rowsum', 'result table')}),

and only for TFs

(${linkToMap('final_tfbs_barjoseph_diseases_min20_binary_average_euc_0.01_rowcount', 'heatmap')} 
, ${linkToTable('final_tfbs_barjoseph_diseases_min20_binary_average_euc_0.01_rowcount', 'result table')}). 
</p>

<p><li>Using the same disease-gene associations, we have created regulomes on a subset of diseases defined as neoplasms, both normalized differentially in both directions 

(${linkToMap('final_tfbs_barjoseph_neoplasms_binary_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_tfbs_barjoseph_neoplasms_binary_average_euc_0.01_rowsum', 'result table')}),

and only for TFs

(${linkToMap('final_tfbs_barjoseph_neoplasms_binary_average_euc_0.01_rowcount', 'heatmap')} 
, ${linkToTable('final_tfbs_barjoseph_neoplasms_binary_average_euc_0.01_rowcount', 'result table')}). 
</p>

<p><li>Continuing in the similar vein, we have created regulomes that makes use of experimentally-based cancer gene associations, retrieved from the <a href='http://www.intogen.org/home'>IntOGen</a> database. We provide two variants. First, for genes identified as having altered copy number variation in cancer cells

(${linkToMap('final_tfbs_barjoseph_intogen_v2_tumors_copynumber_binary_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_tfbs_barjoseph_intogen_v2_tumors_copynumber_binary_average_euc_0.01_rowsum', 'result table')}),

and second, for genes transcriptionally altered

(${linkToMap('final_tfbs_barjoseph_intogen_v2_tumors_transcript_binary_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_tfbs_barjoseph_intogen_v2_tumors_transcript_binary_average_euc_0.01_rowsum', 'result table')}). 
</p>

<p><li>In addition to the disease regulomes in different versions, we have generated maps showing combinations of TFs and gene lists associated with Gene ontology terms, also based on the <a href='http://www.coremine.com/medical/'>PubGene</a> database of literature co-citations

(${linkToMap('final_tfbs_barjoseph_geneontology_min20_binary_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_tfbs_barjoseph_geneontology_min20_binary_average_euc_0.01_rowsum', 'result table')}). * 
</p>

<p><li>We have also generated a similar set of regulomes based on transcription factor binding site predictions (the "TFBS Conserved" track from <a href='http://genome.ucsc.edu/'>UCSC Genome Browser</a>). All these regulomes are normalized in both directions. First we have created a regulome based on the <a href='http://www.hugenavigator.net/HuGENavigator/startPagePhenoPedia.do'>Phenopedia</a> disease-gene associations
(${linkToMap('final_tfbs_phenopedia_min10_binary_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_tfbs_phenopedia_min10_binary_average_euc_0.01_rowsum', 'result table')}).

Second, a regulome based on diseases-gene associations calculated from the <a href='http://www.coremine.com/medical/'>PubGene</a> database
(${linkToMap('final_tfbs_diseases_min10_binary_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_tfbs_diseases_min10_binary_average_euc_0.01_rowsum', 'result table')}). 
</p>

<p><li>Furthermore, we have generated maps that are not based on gene lists at all, but that instead query the relation between TF binding sites and DNA regions wound around nucleosomes with particular histone modifications in T-cells 

(${linkToMap('final_tfbs_histmod_count_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_tfbs_histmod_count_average_euc_0.01_rowsum', 'result table')}). 
</p>

<p><li>We also present a map of the relation between histone modifications in T-Cells and the Gene ontology terms of the genes where such modifitacion are over/under-expressed around the TSS

(${linkToMap('final_histmod_geneontology_min1000art_count_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_histmod_geneontology_min1000art_count_average_euc_0.01_rowsum', 'result table')}). 
</p>

<p><li>Looking at other regulatory elements apart from TFs and histone modifications, we present a map of MiRNAs versus diseases

(${linkToMap('mirna_diseases_hyper_0.05_5kb_flanked_min3_count_av_ep_0.01_rowsum_balanced', 'heatmap')} 
, ${linkToTable('mirna_diseases_hyper_0.05_5kb_flanked_min3_count_av_ep_0.01_rowsum_balanced', 'result table')}) 

 and a map of repeating elements versus disases 

(${linkToMap('repeats_diseases_hyper_0.05_5kb_flanked_min3_count_av_euc_0.01_rowsum_balanced', 'heatmap')} 
, ${linkToTable('repeats_diseases_hyper_0.05_5kb_flanked_min3_count_av_euc_0.01_rowsum_balanced', 'result table')})

(both based on <a href='http://www.coremine.com/medical/'>PubGene</a> data). These maps are in need of updates.

</p>

<p><li>Finally, we have generated maps of how different TFs (according to TFBS predictions) preferentially regulate genes of particular chromosome arms

(${linkToMap('final_tfbs_chrarms_count_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_tfbs_chrarms_count_average_euc_0.01_rowsum', 'result table')}),

as well as maps of how different histone modifications (in T-cells) distribute across chromosome arms

(${linkToMap('final_histmod_chrarms_count_average_euc_0.01_rowsum', 'heatmap')} 
, ${linkToTable('final_histmod_chrarms_count_average_euc_0.01_rowsum', 'result table')}). 
</p>
</ul>

<%def name="toolHelp()">
<b>Table and heatmap representations of regulome</b>
<p>Both a table and a heatmap version of the results are available, providing complementary representations of the regulomes. The table representation provides precise z-score values for specific TF-disease relations, and allows results to be sorted according to any row (TF) or column (disease) so as to get ranked associations to a given TF/disease. The z-scores indicate over-/under-representation of binding sites for each TF in sets of genes related to each disease (details are given in the article on the regulome).</p>
<p>The heatmap representation allows a broader overview of results, providing powerful visual clues of the most deviant associations and providing a broad impression of similarities and differences between specific TFs/disesases of interest. As both rows and columns are clustered, diseases with similar profiles of association to TFs will be adjacent (and similarly for TFs against diseases), allowing larger patterns of associations between sets of diseases and TFs to be spotted visually (as well as specific deviances within such clusters). Colors represent the same z-scores as in the table representation, with blue to cyan (lowest) as under-representation, and red to yellow (highest) as over-representation (see detailed color legend at the upper left corner of the heatmaps). Furthermore, each cell in the heatmap contains a host of further detailed information that can be accessed by marking the cell. This includes further information on the disease and the TF, as well as the list of genes associated to the disease and TF binding in these genes.</p>
<b>Regulome interface</b>
<ul>
<li>To create markers (for single cells) or clusters (for multiple cells), click the corresponding button and then click on the desired place on the map. Markers can be moved by clicking and dragging. Clusters can be resized in the same manner.
<li>To access the underlying information, click a marker, or inside a cluster.
<li>To delete a marker or cluster, click "Delete mark" and then click the marker or cluster you want to delete.
<li>To store all your markers and clusters, click "Save marks" and type a name. This name is not connected to any one user or computer and can be shared with others.
<li>To reload previously stored markers and clusters, click "Load marks" and type the name used for storage. 
<li>To remove all markers and cluster, click "Reset map".
<li>To get an overview over the details of all specified clusters on a single page, click "All clusters".
<li>To search for a row and/or column, use the text box to the right of the buttons. Just type in any part of the row/column name and press the 'return' key.
</ul>
<hr/ class='space'>
* These regulomes include a set of manually selected clusters. To see them, click "Load marks" and choose "common" (which is default).
</%def>
