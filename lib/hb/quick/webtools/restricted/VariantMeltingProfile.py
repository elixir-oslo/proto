import os
import sqlite3
import subprocess
import sys
import time

from config.Config import URL_PREFIX
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import PlainTrack
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class VariantMeltingProfile(GeneralGuiTool):
    varmelt_dir = '/software/varmelt/'    
    ref_snp = []
    multiallelic = []
    port = 4002
    genomes = ['hg19', 'mm10']

    AMBIGUOUS_DNA = {
        'Y': ['C','T'],
        'R': ['A','G'],
        'W': ['A','T'],
        'S': ['C','G'],
        'K': ['T','G'],
        'M': ['A','C'],
        'D': ['A','G','T'],
        'V': ['A','C','G'],
        'H': ['A','C','T'],
        'B': ['C','G','T']
    }

    primer3_headers = ['Num', 'Chrom', 'Id', 'Product start', 'Product end', 'Forward primer temp', 'Reverse primer temp',
                    'Pcrprod length', 'Avg melt temp', 'Sequence', 'GC clamp position']

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Variant melting profiles"

    @staticmethod
    def isPublic():
        return True

    @staticmethod
    def isBatchTool():
        return False

    @staticmethod
    def getOutputFormat(choices):
        return 'html' if choices.run == 'Single' else 'customhtml'

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:
        
            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.
        
        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).
        '''
        return [('Genome build', 'genome'), ('Run', 'run'),
            ('Batch lines (click (i)-icon below for help)', 'batch'), ('RefSNP ID', 'rsid'),
            ('Chromosome', 'chr'), ('Position', 'pos'), ('Reference allele', 'ref'), ('Variant allele', 'var'),
            ('Search window length (bp)', 'win'),
            ('Opt size', 'optSize'), ('Min size', 'minSize'), ('Max size', 'maxSize'),
            ('Opt Tm', 'optTm'), ('Min Tm', 'minTm'), ('Max Tm', 'maxTm'),
            ('Number to return', 'numReturn'),
            ('Product size range', 'range'),
            ('GC clamp position', 'clamp'),
            ('Information', 'info')
            ]

    @classmethod
    def check_start_gfServer(cls, genome):
        port = cls.port + cls.genomes.index(genome)
        twobitfile = genome + '.2bit'
        logfile = 'log/gf.%d.%s.log' % (port,genome)
        pidfile = cls.varmelt_dir + '/pid/gf.%d.%s.pid' % (port,genome)
        startcmd = [cls.varmelt_dir+'/bin/gfServer', 'start', 'localhost', str(port), '-stepSize=5', '-canStop', '-log='+logfile, twobitfile]
        checkcmd = [cls.varmelt_dir+'/bin/gfServer', 'status', 'localhost', str(port)]

        try:
            with open(pidfile) as pf:
                pid = int(pf.read())
            os.kill(pid, 0)
        except:
            pid = None
        code = subprocess.call(checkcmd)
        if code != 0:
            if pid == None:
                proc = subprocess.Popen(startcmd, cwd=cls.varmelt_dir, close_fds=True)
                with open(pidfile, 'w') as pf:
                    pf.write(str(proc.pid))
                time.sleep(5)
                if proc.poll() != None:
                    return 'blat/gfServer port %d for %s not running, startup failed' % (port, genome)
                return 'blat/gfServer port %d for %s is starting up, please try again in a minute' % (port, genome)
            return 'blat/gfServer port %d for %s not ready, please try again in a minute' % (port, genome)
        return None

    @classmethod
    def get_ref_snp(cls, choices):
        rsidChoice = choices.rsid if choices.run == 'Single' else choices.batch 
        if not rsidChoice:
            return []
        if cls.ref_snp:
            return cls.ref_snp
        lines = rsidChoice.splitlines()
        
        cls.ref_snp = []
        cls.multiallelic = []
        
        dbsnp = cls.varmelt_dir + '/dbsnp/' + choices.genome + '.dbsnp.sqlite3'
        db = None
        c = None

        if os.path.exists(dbsnp):
            db = sqlite3.connect(dbsnp)
            db.text_factory = str
            c = db.cursor()

        for line in lines:
            if not line:
                continue
            rsid = line.strip().replace(' ', '')
            spec = rsid.split(':')
            if len(spec) > 2:
                rv = spec[2]
                #if len(rv) >= 3 and len(spec) == 3:
                #    spec[2] = rv[0]
                #    spec.append(rv[2])
                if len(spec) < 4:
                    spec += [''] * (4 - len(spec))
                cls.ref_snp.append(tuple([''] + spec))
                continue
            if rsid.lower().startswith('rs'):
                rsid = rsid[2:]

            if db and c:
                c.execute("select rsid,chr,pos,ref,vars from snp where rsid=?", [rsid])
                row = c.fetchone()
                if row:
                    rs = [str(col) for col in row]
                    rs[1] = 'chr' + rs[1]
                    #if len(rs[4]) > 1 and rs[4].find(',') == -1:
                    #    rs[4] = ','.join(list(rs[4]))
                    #    cls.multiallelic.append(rs)
                else:
                    rs = [rsid] + [''] * 4
            #print rs
            #assert len(rows) <= 1
            #if len(rows) == 1:
            #    cls.ref_snp.append([str(c) for c in rows[0]])
                cls.ref_snp.append(tuple(rs))

        if db:
            c.close()
            db.close()

        return cls.ref_snp

    @staticmethod    
    def getOptionsBoxRun(prevChoices): 
        return ['Single', 'Batch']

    @staticmethod    
    def getOptionsBoxBatch(prevChoices):
        if prevChoices.run == 'Batch':
            return '', 10
        return None

    @staticmethod
    def getInfoForOptionsBoxBatch(prevChoices):
        return '''Specify RefSNP IDs or custom chr:pos:ref:var<br>
            Example:<br>
            rs123<br>
            chr7:2496646:A:T
            '''

    @staticmethod    
    def getOptionsBoxRsid(prevChoices): 
        if prevChoices.run == 'Single':
            return ''
        return None

    @classmethod    
    def getOptionsBoxGenome(cls):
        #return [g[1] for g in GalaxyInterface.getAllGenomes()]
        return cls.genomes
 
    @classmethod
    def getOptionsBoxChr(cls, prevChoices):
        ref_snp = cls.get_ref_snp(prevChoices)
        if len(ref_snp) == 1 and prevChoices.run == 'Single':
            rs = ref_snp[0]
            return [rs[1]]
        elif len(ref_snp) > 1 or prevChoices.run == 'Batch':
            return None
        return GenomeInfo.getChrList(prevChoices.genome)
    
    @classmethod    
    def getOptionsBoxPos(cls, prevChoices): 
        ref_snp = cls.get_ref_snp(prevChoices)
        if len(ref_snp) == 1 and prevChoices.run == 'Single':
            rs = ref_snp[0]
            return rs[2], 1, True
        elif len(ref_snp) > 1 or prevChoices.run == 'Batch':
            return None
            #return '__hidden__', ';'.join([rs[2] for rs in ref_snp])
            
        return '1'
 
    @classmethod
    def getOptionsBoxRef(cls, prevChoices):
        sref = None
        ref_snp = cls.get_ref_snp(prevChoices)
        if len(ref_snp) == 1 and prevChoices.run == 'Single':
            rs = ref_snp[0]
            sref = rs[3]
            return [sref]
        elif len(ref_snp) > 1 or prevChoices.run == 'Batch':
            return None
            #return '__hidden__', ';'.join([rs[3] for rs in ref_snp])

        if len(ref_snp) == 0:
            ref = VariantMeltingProfile.get_reference_allele(prevChoices.genome, prevChoices.chr, prevChoices.pos)
        #if sref:
        #    assert sref == ref, 'reference not matching hg19!!!'
            if ref:
                return ref
        else:
            return ['N', 'A', 'C', 'G', 'T']

    @classmethod    
    def getOptionsBoxVar(cls, prevChoices):
        ref_snp = cls.get_ref_snp(prevChoices)
        if len(ref_snp) == 1 and prevChoices.run == 'Single':
            rs = ref_snp[0]
            vars = [rs[4]]
            if len(rs[4]) == 1 and cls.AMBIGUOUS_DNA.has_key(rs[4]):
                vars += cls.AMBIGUOUS_DNA[rs[4]]
            
            return vars
        elif len(ref_snp) > 1 or prevChoices.run == 'Batch':
            return None
            #return '__hidden__', ';'.join([rs[4] for rs in ref_snp])

        #return [b for b in ['A', 'C', 'G', 'T'] if b != prevChoices.ref]
        return ''

    @staticmethod    
    def getOptionsBoxWin(prevChoices): 
        return '500'
    
    @staticmethod    
    def getOptionsBoxLeft(prevChoices): 
        return '1'
    
    @staticmethod    
    def getOptionsBoxInternal(prevChoices): 
        return '1'
    
    @staticmethod    
    def getOptionsBoxRight(prevChoices): 
        return '1'
    
    @staticmethod    
    def getOptionsBoxOptSize(prevChoices): 
        return '20'
    
    @staticmethod    
    def getOptionsBoxMinSize(prevChoices): 
        return '18'
    
    @staticmethod    
    def getOptionsBoxMaxSize(prevChoices): 
        return '23'
    
    @staticmethod    
    def getOptionsBoxOptTm(prevChoices): 
        return '60'
    
    @staticmethod    
    def getOptionsBoxMinTm(prevChoices): 
        return '53'
    
    @staticmethod
    def getOptionsBoxMaxTm(prevChoices): 
        return '63'
    
    @staticmethod
    def getOptionsBoxNumReturn(prevChoices): 
        return '1'

    @staticmethod
    def getOptionsBoxStability(prevChoices): 
        return '9'
    
    @staticmethod
    def getOptionsBoxRange(prevChoices): 
        #return '150-200 100-300 301-400 401-500 501-600 601-700 701-850 851-1000'
        return '70-80 80-90 90-100 100-110 120-130 130-140 140-150 150-160'
    
    @staticmethod
    def getOptionsBoxClamp(prevChoices): 
        #return 'CGCCCGCCGCGCCCCGCGCCCGTCCCGCCGCCCCCGCCCGGG'
        #return True
        return ["Automatic", "5-prime end", "3-prime end", "None"]

    @classmethod
    def getOptionsBoxInfo(cls, prevChoices):
        if prevChoices.run == 'Batch' and len(cls.multiallelic) > 0:            
            return '__rawstr__', '''<div class="warningmessage">
            Multi-allelic SNPs (random allele selected): %s
            </div>''' % ( ', '.join(['rs'+rs[0] for rs in cls.multiallelic]) )
        return None

    @classmethod
    def validate_snp(cls, snps, genome):
        DNA = ['A','C','G','T'] + cls.AMBIGUOUS_DNA.keys()

        err = []
        for snp in snps:
            assert len(snp) == 5
            _rsid, _chr, _pos, _ref, _var = snp
            #spec = ':'.join(snp)
            spec = repr(snp)

            if _rsid and not _chr:
                err.append('Invalid RefSNP: rs' + _rsid)
                continue
            if _chr not in GenomeInfo.getChrList(genome):
                err.append(spec + ' Chromosome ' + _chr + ' is not valid')
                continue
            if not _pos.isdigit():
                err.append(spec + ' Position must numeric')
                continue
            if int(_pos) < 0:
                err.append(spec + ' Position must be higher than 0')
                continue

            chrLen = GenomeInfo.getChrLen(genome, _chr)
            if int(_pos) > chrLen:
                err.append(spec + ' Position is higher than length of %s (%d)' % (_chr, chrLen))
                continue
    
            ref = VariantMeltingProfile.get_reference_allele(genome, _chr, _pos, len(_ref))
            if _ref != ref:
                err.append(spec + ' Reference allele does not match reference genome, should be: ' + ref)
                continue
    
            if _ref == 'N':
                err.append(spec + ' Reference allele can not be N')
                continue
                    
            if not _var:
                err.append(spec + ' Variant allele not specified')
                continue

            if not all([v in DNA for v in _var]):
                err.append(spec + ' Variant allele ' + _var + " is not valid")
                continue

            if cls.AMBIGUOUS_DNA.has_key(_var) and _ref in cls.AMBIGUOUS_DNA[_var]:
                err.append(spec + ' Ambiguous variant allele includes reference')
                continue
                
                
        return err
        


    @classmethod
    def validateAndReturnErrors(cls, choices):
        
        DNA = ['A','C','G','T'] + cls.AMBIGUOUS_DNA.keys()

        gfcheck = cls.check_start_gfServer(choices.genome)
        if gfcheck:
            return gfcheck
        
        if choices.rsid and len(cls.ref_snp) == 0:
            return 'Invalid RefSNP ID'
        
        err = None
        
        if len(cls.get_ref_snp(choices)) == 0:
            if choices.pos != None:
                err = cls.validate_snp([('',choices.chr,choices.pos,choices.ref,choices.var)], choices.genome)
            else:
                return 'Batch list is empty'

        if len(cls.get_ref_snp(choices)) > 0:
            err = cls.validate_snp(cls.get_ref_snp(choices), choices.genome)                    
                    
        if err and len(err) > 0:
            return '<br>\n'.join(err)

        return None


    @staticmethod
    def get_reference_allele(genome, chr, pos, len = 1):
        pos = pos.strip()
        if not pos.isdigit() or int(pos) < 0:
            return None
        bpos = int(pos) - 1

        try:
            genReg = GenomeRegion(genome, chr, bpos, bpos + len)
            seqTV = PlainTrack( GenomeInfo.getSequenceTrackName(genome) ).getTrackView(genReg)
            #ge = seqTV.next()
            #return ge.val().upper()
            seq = ""
            for ge in seqTV:
                seq += ge.val().upper()
            return seq
        except Exception as e:
            print e
            return '-'



    @classmethod    
    def primer3_table_header(cls, core):
        core.tableHeader(cls.primer3_headers)

    
    @classmethod
    def run_varmelt(cls, dir, choices):
        port = cls.port + cls.genomes.index(choices.genome)

        
        cmd = [cls.varmelt_dir + 'varmelt.py']
        skip_params = ['rsid', 'run', 'batch', 'info', 'genome', 'ref', 'var', 'chr', 'pos', 'clamp']
        trans = {'win':'windowSize', 'range':'size_ranges'}

        for key, val in choices._asdict().items():
            if key not in skip_params:
                key = trans.get(key, key).lower()
                if key == 'size_ranges':
                    val = '"'+val+'"'
                cmd += ['--'+key, val]
#        if choices.clamp == True or choices.clamp == 'True':
#            cmd += ['--gc_clamp', 'auto']
#        else:
#            cmd += ['--gc_clamp', 'none']
        if choices.clamp:
            clamps = {'A': 'auto', '5': '5p', '3': '3p', 'N': 'none'}
            cmd += ['--gc_clamp', clamps[choices.clamp[0]]]

        cmd += [choices.ref, choices.var, choices.chr, str(choices.pos), choices.genome, str(port), dir]
        
        print ' '.join(cmd)

        os.environ['PERL5LIB'] += ':' + cls.varmelt_dir

        subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stdout, shell=False)


    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):        

        #rsids = choices.rsid.split()
        if choices.run == 'Batch':
            #print rsids
            return cls.execute_batch(choices,galaxyFn,username)
        elif choices.batch != '__batch__':
            print '<div class="debug">'
            
        
        results = GalaxyRunSpecificFile(['html'], galaxyFn)

        dir = os.path.dirname(results.getDiskPath(ensurePath=True))
        os.mkdir(dir + '/html')
         
        #print '<div class="debug">'

        cls.choices = choices
        cls.run_varmelt(dir, choices)
        
        url = results.getURL()

        if choices.run == 'Single' and choices.batch != '__batch__':
            print '</div></pre>'

        core = HtmlCore()
        core.header('Primer3 candidates')
        VariantMeltingProfile.primer3_table_header(core)
        VariantMeltingProfile.primer3_resultsfile_header(dir)
        
        for r in range(0, int(choices.numReturn)):
            datafile = dir + '/tempdata.' + str(r) + '.results.txt'
            if os.path.exists(datafile):
                variant_pos = VariantMeltingProfile.proc_temp_data(dir, str(r))
    
                chart = open(dir + '/html/chart-'+str(r)+'.html', 'w')
                chart.write(VariantMeltingProfile.make_chart(variant_pos, r))
                chart.write(cls.primer3_results_table(dir, r))
                chart.write('</body></html>')
                chart.close()
            
                cls.primer3_results(dir, r)
                cls.primer3_results_table(dir, r, core, url)
                print '<a href="%s/chart-%d.html">Results/graph num %d</a><br>' % (url, r, r+1)
            else:                
                cls.primer3_results(dir, r)
                cls.primer3_results_table(dir, r, core, None)
                break
                

        core.tableFooter()

        if choices.run == 'Single' and choices.batch != '__batch__':
            print str(core)
            print '<pre>'
        
        xcore = HtmlCore()
        xcore.begin()
        xcore.append(str(core))
        xcore.end()
        open(dir + '/results.html', 'w').write(str(xcore))

        
    @classmethod    
    def execute_batch(cls, choices, galaxyFn=None, username=''):
        print GalaxyInterface.getHtmlBeginForRuns(galaxyFn)
        html = HtmlCore()
        html.header('Batch run results')

        refSnps = cls.get_ref_snp(choices)
        #print refSnps

        batchMal = "$Tool[hb_variant_melting_profiles](" + '|'.join(["'%s'"] * len(choices)) + ")"
        cmdList = []
        for rs in refSnps:
            #if len(rs[4]) > 1:
            #    rs = list(rs)
            #    rs[4] = list(rs[4])[0]
            #    rs = tuple(rs)
            fakeChoices = (choices.genome, 'Single', '__batch__') + rs + choices[8:]
            #print rs
            cmdList.append(batchMal % fakeChoices)
        
        #print cmdList    
        GalaxyInterface.runBatchLines(cmdList, galaxyFn, username=username, printResults=False, printProgress=True)
        #print HtmlCore().styleInfoEnd()
        
        results_tsv = GalaxyRunSpecificFile(['results.tsv'], galaxyFn)
        results = results_tsv.getFile()
        baseurl = results_tsv.getURL().rpartition('/')[0]
        dir = os.path.dirname(results_tsv.getDiskPath())
        for i in range(0, len(cmdList)):
            header = True
            ri = 0
            for resultline in open('/'.join([dir, str(i), 'results.tsv'])):
                if header:
                    header = False
                    if i == 0:
                        headertxt = '#run\t' + resultline
                        results.write(headertxt)
                        html.tableHeader(headertxt.split('\t'))
                else:
                    results.write(str(i) + '\t' + resultline)
                    if resultline.count('?') == 0:
                        link = '<a href="%s/%d/html/chart-%d.html">%d (graph)</a>' % (baseurl, i, ri, i)
                    else:
                        link = str(i)
                    html.tableLine([link] + resultline.split('\t'))
                    ri += 1
                
        results.close()
        html.tableFooter()

        # XXX: temp fix for HB/stable bug
        if URL_PREFIX == '/hb':
            print '</div>'
        
        print '<p><b>' + results_tsv.getLink('Download results') + '</b></p>'
        print html
        print GalaxyInterface.getHtmlEndForRuns()        
        
        
    @staticmethod 
    def proc_temp_data(dir, rnr):
        
        data = dir + '/tempdata.' + rnr + '.results.txt'
        
        jsfile = open(dir + '/html/data-'+rnr+'.js', 'w')
        
        var_pos = None
        temp = []
        head = []
        for line in open(data, 'r'):
            if line.startswith('#'):
                continue
            
            cols = line.split('\t')
            head.append(cols[1])
            temp.append(cols[5].split(','))
            
            var_pos = int(cols[2])

        grs = '","'.join(head)

        js = 'var data = google.visualization.arrayToDataTable([["x","%s"],' % (grs)
        
        maxtemplen = max([len(t) for t in temp])
        for i in range(0, maxtemplen):
            js += '[' + str(i + 1)
            for g in range(0, len(temp)):
                if i < len(temp[g]):
                    js += ',' + temp[g][i]
                else:
                    js += ',null'
            js += '],'
                
        
        js += ']);\n'
        jsfile.write(js)
        jsfile.close()
        return var_pos


    @classmethod 
    def primer3_results_table(cls, dir, rnr, core = None, url = '.'):
        append = True
        if not core:
            append = False
            core = HtmlCore()
            core.header('Primer3 results')
            VariantMeltingProfile.primer3_table_header(core)
        
        rows = []
        try:
            p3 = open(dir + '/primer3.' + str(rnr) + '.results.txt', 'r')
            line = p3.readline()
            if line:
                if url != None:
                    link = '<a href="%s/chart-%d.html">%d (view)</a>' % (url, rnr, rnr + 1)
                else:
                    link = str(rnr + 1)
                row = [link]
                cols = line.strip().split('\t')
                for col in cols:
                    if len(col) > 40:
                        row.append('<br>'.join([col[c:c+40] for c in xrange(0, len(col), 40)]))
                    else:
                        row.append(col)
                row += [''] * (len(cls.primer3_headers) - len(cols) - 1)
            else:
                #XXX
                row = [link] + ['?']*10 + [line.split()[10]] + ['?']
            rows.append(row)
            p3.close()
                

        except IOError:
            rows.append([str(rnr + 1), cls.choices.chr[3:], 'No primers found'] + ['?']*8)
            
        for row in rows:
            core.tableLine(row)
        if not append:
            core.tableFooter()
            #core.append('<p><a href="javascript:window.history.back()">Go back</a></p>')
        return str(core)

    @classmethod 
    def primer3_resultsfile_header(cls, dir):
        with open(dir + '/results.tsv', 'w') as f:
            f.write('\t'.join(cls.primer3_headers) + '\n')
        

    @staticmethod
    def _get_id(choices):
        id = '_'.join((choices.chr[3:], choices.pos, choices.ref, choices.var))
        return id
        
    @classmethod 
    def primer3_results(cls, dir, rnr):
        rows = []
        tsv = open(dir + '/results.tsv', 'a')
        try:
            p3 = open(dir + '/primer3.' + str(rnr) + '.results.txt', 'r')
            line = p3.readline()
            if line:
                row = [str(rnr + 1)]
                cols = line.strip().split('\t')
                row += cols
                row += [''] * (len(cls.primer3_headers) - len(cols) - 1)
                p3.close()
        except IOError:
            row = ['0', cls.choices.chr[3:], 'No primers found'] + ['?']*8
        rows.append(row)
        tsv.write('\t'.join(row) + '\n')
        tsv.close()
        return rows

    @staticmethod 
    def make_chart(pos, rnr):
        html = """
<html>
<head>
    <link href="%(URL_PREFIX)s/static/style/base.css" rel="stylesheet" type="text/css" />
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load('visualization', '1.1', {packages: ['corechart', 'controls']});
    </script>
    
    <script type="text/javascript" src="data-%(result_nr)d.js"></script>
    <script type="text/javascript">
      function drawVisualization() {
        var dashboard = new google.visualization.Dashboard(
             document.getElementById('dashboard'));
      
         var control = new google.visualization.ControlWrapper({
           'controlType': 'ChartRangeFilter',
           'containerId': 'control',
           'options': {
             // Filter by the date axis.
             'filterColumnIndex': 0,
             'ui': {
               'chartType': 'LineChart',
               'chartOptions': {
                 'chartArea': {'width': '90%%', 'left': 60},
                 'hAxis': {'baseline': %(variant_pos)d, 'baselineColor': 'black'}
               },
               'chartView': {
                 'columns': [0,1,2]
               }
             }
           }
         });
      
         var chart = new google.visualization.ChartWrapper({
           'chartType': 'LineChart',
           'containerId': 'chart',
           'options': {
             // Use the same chart area width as the control for axis alignment.
             'chartArea': {'height': '90%%', 'width': '90%%', left: 60},
             'legend': {'position': 'in', 'textStyle': {'fontSize': 11}},
             'title': 'Variant melting curves',
             'hAxis': {'title': 'Position', 'baseline': %(variant_pos)d, 'baselineColor': 'black'},
             'vAxis': {'title': 'Temperature'}
           }
         });
         
         dashboard.bind(control, chart);
         dashboard.draw(data);
      }

      google.setOnLoadCallback(drawVisualization);
    </script>

</head>
  <body>

  <div id="dashboard">
        <div id="chart" style='width: 100%%; height: 500px;'></div>
        <div id="control" style='width: 100%%; height: 50px;'></div>
    </div>
"""

        return html % {'variant_pos': pos, 'result_nr': rnr, 'URL_PREFIX': URL_PREFIX}

