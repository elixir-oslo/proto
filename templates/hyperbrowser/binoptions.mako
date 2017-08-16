<%page args="galaxy=None,gui=None,hyper=None,genome=None,methodLabel='Compare in',updateRunDescription=True,useBinSize=True,methodOptions=None,method=None,track1=None,track2=None,category=None,extract=False"/>

<%
#if methodOptions == None:
#    methodOptions = [('Chromosome arms','__chrArms__'), ('Chromosomes','__chrs__'), ('Cytobands','__chrBands__'), ('Genes (Ensembl)','__genes__'), ('Bounding regions','__brs__'), ('Custom specification','__custom__'), ('Bins from history','__history__')]

if track1 is not None:
    trackName1 = track1.definition()
else:
    trackName1 = None

if track2 is not None:
    trackName2 = track2.definition()
else:
    trackName2 = None

# binCatFilter = hyper.getBinningCategories(genome, trackName1, trackName2)

## methodOptions = hyper.getBinningCategoryTuples(genome, trackName1, trackName2)
if not methodOptions:
    assert category is not None
    methodOptions = hyper.getBinningCategoryTuples(category, genome, trackName1, trackName2)

params = galaxy.params
region = params.get('region', '*')
binsize = params.get('binsize', '1m')
binfile = params.get('binfile', None)
if method is None:
#    method = params.get('method', '__chrArms__')
    method = params.get('method', methodOptions[0][1])

jsUpdRunDescr = 'false'
jsValidate = ''
if updateRunDescription:
    jsUpdRunDescr = 'true'
    jsValidate = 'onchange="validate(form)"'

%>
<div>
    <label>${methodLabel}
	<select id="method" name="method" onchange="methodOnChange(this,event,${jsUpdRunDescr})">
	%for option in methodOptions:
#				%if option[0] in binCatFilter:
				    <%
						#Hack to support rerun of old histories
						if method == 'auto':
								method = '__custom__'
						elif method == 'binfile':
								method = '__history__'
						%>
						<option value="${option[1]}" ${gui.selected(option[1], method)}>${option[0]}</option>
#				%endif
	%endfor
	</select>
    </label>

		<%
            chrArmNote = '<i><b>Note:</b> For hypothesis tests where the positions of elements are randomized, the centromeres ' \
        'and other regions where the elements are never found should be removed from the analysis regions. ' \
        'In this case, use the chromosome arms as analysis regions, define specific bounding regions for the ' \
        'tracks, or use custom analysis regions. If this is not done, the resulting p-values are ' \
        'generally better than what they should have been.</i>'
        %>


    <p id="pnlRegion" class="hidden">
    <label>Regions of the genome: <input id="region" name="region" value="${region}" ${jsValidate}></label>
    <i>Region specification as in UCSC Genome browser, * means whole genome. k and m denoting thousand and million bps, respectively. Several regions may be specified if separated by comma. If the end position is omitted, it is set equal to the end of the chromosome. Example: chr1:1-20m, chr2:10m-</i>
    </p>

    %if useBinSize:
    <p id="pnlBinSize" class="hidden">
    <label>Bin size: <input size="10" id="binsize" name="binsize" value="${binsize}" ${jsValidate}></label>
    <i>The selected regions are divided into bins of this size. k and m denoting thousand and million bps, respectively. * means whole region / whole chromosome. E.g. 100k</i>
    </p>
    %endif

		<select id="pnlUserRegion" name="binfile" class="hidden" ${jsValidate}>
	<option value=""> - Choose from history - </option>
        ${galaxy.optionsFromHistory(hyper.getSupportedGalaxyFileFormatsForBinning(), binfile)}
    </select>

		<p id="pnl__brs__" class="hidden">
    <i>Use the bounding regions of the selected track(s), if defined. If more than one track is selected,
		   the intersection of the bounding regions is used, i.e. where the bounding regions are overlapping.
        <br><br></i>
       <a href="#help_bounding_regions" title="Help" onclick="getHelp('bounding_regions')">More information about bounding regions</a>
       <div id="help_bounding_regions" class="infomessagesmall help"></div>
    </p>

		<p id="pnl__chrs__" class="hidden">
    <label>Which: <input size="30" name="__chrs__" value="${params.get('__chrs__', '*')}" ${jsValidate}></label>
    <i>comma separated list of chromosomes, * means all. (E.g. chr1,chr3)</i>
    </p>

    <p id="pnl__chrArms__" class="hidden">
    <label>Which: <input size="30" name="__chrArms__" value="${params.get('__chrArms__', '*')}" ${jsValidate}></label>
    <i>comma separated list of chromosome arms, * means all. (E.g. chr1p,chr1q,chr2p)</i>
    </p>

    <p id="pnl__chrBands__" class="hidden">
    <label>Which: <input size="30" name="__chrBands__" value="${params.get('__chrBands__', '*')}" ${jsValidate}></label>
    <i>comma separated list of cytobands (chromosome bands), * means all. (E.g. 1p36.33,1p36.23)</i>
    </p>

    <p id="pnl__genes__" class="hidden">
    <label>Which: <input size="30" name="__genes__" value="${params.get('__genes__', '*')}" ${jsValidate}></label>
    <i>comma separated list of Ensembl gene ids , * means all. (E.g. ENSG00000208234, ENSG00000199674)</i>
    </p>

		<p id="pnlChrArmNote" class="hidden">
    <i>${chrArmNote if not extract else ''}</i>
    </p>

</div>
