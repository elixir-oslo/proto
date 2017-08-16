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
<%def name="title()">View regulomes (table)</%def>

<%def name="linkToMap(map, text)">
    <a href="${gmi.BASE_URL}/${map}">${text}</a>
</%def>

<%def name="linkToTable(map, text)">
    <a href="${gmi.BASE_URL}/${map}/data/Result_table.html">${text}</a>
</%def>

<h4>Normalized on both rows and columns (focusing on column differences):</h4>
<table class="colored">
<tr>
<td></td>
<th>Diseases (<a href='http://www.hugenavigator.net/HuGENavigator/startPagePhenoPedia.do'>Phenopedia</a>)</th>
<th>Diseases (<a href='http://www.coremine.com/medical/'>PubGene</a>)</th>
<th>Neoplasms (<a href='http://www.coremine.com/medical/'>PubGene</a>)</th>
<th>Cancer genes, altered copy numbers (<a href='http://www.intogen.org/home'>IntOGen</a>)</th>
<th>Cancer genes, altered transcription (<a href='http://www.intogen.org/home'>IntOGen</a>)</th>
<th>Gene Ontology terms (<a href='http://www.coremine.com/medical/'>PubGene</a>)</th>
<th>Histone modifications (T-cell, <a href='http://www.ncbi.nlm.nih.gov/pubmed/17512414'>Barski 2007</a>)</th>
<th>Chromosome arms</th>
</tr>
<tr class="odd_row">
<th rowspan="2">Transcription factor binding (<a href='http://genome.cshlp.org/content/20/4/526.long'>Bar-Joseph predictions</a>)</th>
<td>${linkToMap('final_tfbs_barjoseph_phenopedia_min20_binary_average_euc_0.01_rowsum', 'Differential disease regulome (heatmap) *')}</td>
<td>${linkToMap('final_tfbs_barjoseph_diseases_min20_binary_average_euc_0.01_rowsum', 'Heatmap')}</td>
<td>${linkToMap('final_tfbs_barjoseph_neoplasms_binary_average_euc_0.01_rowsum', 'Heatmap')}</td>
<td>${linkToMap('final_tfbs_barjoseph_intogen_v2_tumors_copynumber_binary_average_euc_0.01_rowsum', 'Heatmap')}</td>
<td>${linkToMap('final_tfbs_barjoseph_intogen_v2_tumors_transcript_binary_average_euc_0.01_rowsum', 'Heatmap')}</td>
<td>${linkToMap('final_tfbs_barjoseph_geneontology_min20_binary_average_euc_0.01_rowsum', 'Heatmap *')}</td>
<td>${linkToMap('final_tfbs_histmod_count_average_euc_0.01_rowsum', 'Heatmap')}</td>
<td></td>
</tr>
<tr class="odd_row">
<td>${linkToTable('final_tfbs_barjoseph_phenopedia_min20_binary_average_euc_0.01_rowsum', 'Result table')}</td>
<td>${linkToTable('final_tfbs_barjoseph_diseases_min20_binary_average_euc_0.01_rowsum', 'Result table')}</td>
<td>${linkToTable('final_tfbs_barjoseph_neoplasms_binary_average_euc_0.01_rowsum', 'Result table')}</td>
<td>${linkToTable('final_tfbs_barjoseph_intogen_v2_tumors_copynumber_binary_average_euc_0.01_rowsum', 'Result table')}</td>
<td>${linkToTable('final_tfbs_barjoseph_intogen_v2_tumors_transcript_binary_average_euc_0.01_rowsum', 'Result table')}</td>
<td>${linkToTable('final_tfbs_barjoseph_geneontology_min20_binary_average_euc_0.01_rowsum', 'Result table')}</td>
<td>${linkToTable('final_tfbs_histmod_count_average_euc_0.01_rowsum', 'Result table')}</td>
<td></td>
</tr>
<tr>
<th rowspan="2">Transcription factor binding sites("TFBS Conserved" track from <a href='http://genome.ucsc.edu/'>UCSC Genome Browser</a>)</th>
<td>${linkToMap('final_tfbs_phenopedia_min10_binary_average_euc_0.01_rowsum', 'Heatmap')}</td>
<td>${linkToMap('final_tfbs_diseases_min10_binary_average_euc_0.01_rowsum', 'Heatmap')}</td>
<td></td><td></td><td></td><td></td><td></td>
<td>${linkToMap('final_tfbs_chrarms_count_average_euc_0.01_rowsum', 'Heatmap')}</td>
</tr>
<tr>
<td>${linkToTable('final_tfbs_phenopedia_min10_binary_average_euc_0.01_rowsum', 'Result table')}</td>
<td>${linkToTable('final_tfbs_diseases_min10_binary_average_euc_0.01_rowsum', 'Result table')}</td>
<td></td><td></td><td></td><td></td><td></td>
<td>${linkToTable('final_tfbs_chrarms_count_average_euc_0.01_rowsum', 'Result table')}</td>
</tr>
<tr class="odd_row">
<th rowspan="2">Histone modifications (T-cell, <a href='http://www.ncbi.nlm.nih.gov/pubmed/17512414'>Barski 2007</a>)</th>
<td></td><td></td><td></td><td></td><td></td>
<td>${linkToMap('final_histmod_geneontology_min1000art_count_average_euc_0.01_rowsum', 'Heatmap')}</td>
<td></td>
<td>${linkToMap('final_histmod_chrarms_count_average_euc_0.01_rowsum', 'Heatmap')}</td>
</tr>
<tr class="odd_row">
<td></td><td></td><td></td><td></td><td></td>
<td>${linkToTable('final_histmod_geneontology_min1000art_count_average_euc_0.01_rowsum', 'Result table')}</td>
<td></td>
<td>${linkToTable('final_histmod_chrarms_count_average_euc_0.01_rowsum', 'Result table')}</td>
</tr>
</table>

<h4>Normalized on rows only (focusing on column similarities)</h4>
<table class="colored">
<tr>
<td></td>
<th>Diseases (<a href='http://www.hugenavigator.net/HuGENavigator/startPagePhenoPedia.do'>Phenopedia</a>)</th>
<th>Diseases (<a href='http://www.coremine.com/medical/'>PubGene</a>)</th>
<th>Neoplasms (<a href='http://www.coremine.com/medical/'>PubGene</a>)</th>
</tr>
<tr class="odd_row">
<th rowspan="2">Transcription factor binding (<a href='http://genome.cshlp.org/content/20/4/526.long'>Bar-Joseph predictions</a>)</th>
<td>${linkToMap('final_tfbs_barjoseph_phenopedia_min20_binary_average_euc_0.01_rowcount', 'Heatmap')}</td>
<td>${linkToMap('final_tfbs_barjoseph_diseases_min20_binary_average_euc_0.01_rowcount', 'Heatmap')}</td>
<td>${linkToMap('final_tfbs_barjoseph_neoplasms_binary_average_euc_0.01_rowcount', 'Heatmap')}</td>
</tr>
<tr class="odd_row">
<td>${linkToTable('final_tfbs_barjoseph_phenopedia_min20_binary_average_euc_0.01_rowcount', 'Result table')}</td>
<td>${linkToTable('final_tfbs_barjoseph_diseases_min20_binary_average_euc_0.01_rowcount', 'Result table')}</td>
<td>${linkToTable('final_tfbs_barjoseph_neoplasms_binary_average_euc_0.01_rowcount', 'Result table')}</td>
</tr>
</table>


<%def name="toolHelp()">
<b>Table and heatmap representations of regulome</b>
<p>Both a table and a heatmap version of results are available, providing complementary representations of the regulomes. The table representation provides precise z-score values for specific TF-disease relations, and allows results to be sorted according to any row (TF) or column (disease) so as to get ranked associations to a given TF/disease. The z-scores indicate over-/under-representation of binding sites for each TF in sets of genes related to each disease (details are given in the article on the regulome).</p>
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
