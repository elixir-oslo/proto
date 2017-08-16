#note cannot import HB.GalaxyInterface here due to rpy threading issue

from urllib import quote, unquote
from collections import OrderedDict
from galaxy.util.json import from_json_string, to_json_string
import os, re

def getDataFilePath(root, id):
    from proto.CommonFunctions import getGalaxyFnFromAnyDatasetId
    return getGalaxyFnFromAnyDatasetId(id, root)

def load_input_parameters( filename, erase_file = False ):
    datasource_params = {}
    try:
        json_params = from_json_string( open( filename, 'r' ).read() )
        datasource_params = json_params.get( 'param_dict' )
    except:
        json_params = None
        for line in open( filename, 'r' ):
            try:
                line = line.strip()
                fields = line.split( '\t' )
                datasource_params[ fields[0] ] = unquote(fields[1]).replace('\r','')
            except:
                continue
    if erase_file:
        open( filename, 'w' ).close() #open file for writing, then close, removes params from file
    return json_params, datasource_params


def fileToParams(filename):
    return load_input_parameters( filename, False )[1]


def getJobFromDataset(job_hda):
    # mojo: copied from tool_runner.py
    # Get the associated job, if any. If this hda was copied from another,
    # we need to find the job that created the origial hda
    while job_hda.copied_from_history_dataset_association:#should this check library datasets as well?
        job_hda = job_hda.copied_from_history_dataset_association
    if not job_hda.creating_job_associations:
        print "Could not find the job for this dataset hid %d" % job_hda.hid
        return None
    # Get the job object
    job = None
    for assoc in job_hda.creating_job_associations:
        job = assoc.job
        break   
    if not job:
        print "Failed to get job information for dataset hid %d" % job_hda.hid
    return job


class GalaxyWrapper:
    trans = None
    params = {}
    
    def __init__(self, trans):
        self.trans = trans
        params = trans.request.rerun_job_params if hasattr(trans.request, 'rerun_job_params') else trans.request.params
        for key in params.keys():
            try:
                self.params[key] = unicode(params[key]) if params[key] != None else None
            except:
                self.params[key] = params[key]

    def encode_id(self, id):
        from proto.config.Security import galaxySecureEncodeId
        return galaxySecureEncodeId(id)

    def decode_id(self, id):
        from proto.config.Security import galaxySecureDecodeId
        return galaxySecureDecodeId(id)

    def getDataFilePath(self, id):
        from proto.CommonFunctions import getGalaxyFnFromAnyDatasetId
        return getGalaxyFnFromAnyDatasetId(id)

    def getHistory(self, exts = None, dbkey = None):
        datasets = []
        if self.trans.get_history():
            for dataset in self.trans.get_history().active_datasets:
                if dataset.visible and dataset.state == 'ok':
                    if exts is None or (dataset.extension in exts and (dbkey is None or dataset.dbkey == dbkey)) \
                            or any([isinstance(dataset.datatype, ext) for ext in exts if isinstance(ext, type)]):
                        datasets.append(dataset)
        return datasets

    def optionsFromHistory(self, exts, sel=None, datasets=None):
        html = ''

        if not datasets:
            datasets = self.getHistory(exts)

        for dataset in datasets:
            option = self.makeHistoryOption(dataset, sel)[0]
            html += option
        return html

    def optionsFromHistoryFn(self, exts = None, tools = None, select = None):
        html = '<option value=""> --- Select --- </option>\n'
        vals = [None]
        for dataset in self.getHistory(exts):
            if tools:
                job = getJobFromDataset(dataset)
                tool_id = job.tool_id if job else None
            if tools is None or tool_id in tools:
                option, val = self.makeHistoryOption(dataset, select)
                vals.append(val)
                html += option
        return html, vals

    def itemsFromHistoryFn(self, exts = None):
        items = OrderedDict()
        for dataset in self.getHistory(exts):
            option_tag, val = self.makeHistoryOption(dataset)
            items[unicode(dataset.dataset_id)] = val
        return items

    def makeHistoryOption(self, dataset, select=None, sep=':'):
        assert sep in (',', ':')
        name = dataset.name.replace('[', '(').replace(']', ')')
        sel_id = self.getHistoryOptionId(select)

        if sep == ',':
            vals = ['galaxy', self.encode_id(dataset.dataset_id), dataset.extension]
        else:
            vals = ['galaxy', dataset.extension, self.encode_id(dataset.dataset_id), self.makeHistoryOptionName(dataset)]

        val = sep.join(vals)
        html = '<option value="%s" %s>%d: %s [%s]</option>\n' % (val, selected(dataset.dataset_id, sel_id), dataset.hid, name, dataset.dbkey)
        return (html, val)

    def getHistoryOptionSecureIdAndExt(self, select):
        from proto.CommonFunctions import getSecureIdAndExtFromDatasetInfoAsStr
        id_sel, ext = getSecureIdAndExtFromDatasetInfoAsStr(select)
        return id_sel, ext

    def getHistoryOptionId(self, select):
        id_sel = self.getHistoryOptionSecureIdAndExt(select)[0]
        if id_sel:
            sep = select[6]
            try:
                sel_id = self.decode_id(id_sel)
            except:
                if sep == ',':
                    sel_id = int(id_sel)
                elif id_sel and os.path.exists(id_sel):
                    sel_id = int(re.findall(r'/dataset_([0-9]+)\.dat', id_sel)[0])
        else:
            sel_id = 0
        return sel_id

    def makeHistoryOptionName(self, dataset):
        name = dataset.name.replace('[', '(').replace(']', ')')
        return str(dataset.hid) + quote(' - ' + name, safe='')

    def getUserName(self):
        user = self.trans.get_user()
        return user.email if user else ''

    def getUserIP(self):
        return self.trans.environ['REMOTE_ADDR']
        
    def getSessionKey(self):
        session = self.trans.get_galaxy_session()
#        key = session.session_key if session.is_valid and session.user_id else None
        key = session.session_key if session.is_valid else None
        return key
    
    def hasSessionParam(self, param):
        user = self.trans.get_user()
        if user and user.preferences.has_key('hb_' + param):
#            hbdict = from_json_string(user.preferences['hyperbrowser'])
#            if hbdict.has_key(param):
            return True
        return False

    def getSessionParam(self, param):
        prefs = self.trans.get_user().preferences
        value = from_json_string(prefs['hb_'+param])
        return value

    def setSessionParam(self, param, value):
        if self.trans.get_user():
            prefs = self.trans.get_user().preferences
            #hbdict = dict()
            #hbdict[param] = value
            prefs['hb_'+param] = to_json_string(value)
            self.trans.sa_session.flush()



def selected(opt, sel):
    return ' selected="selected" ' if opt == sel else ''

def checked(opt, sel):
    return ' checked="checked" ' if opt == sel else ''

def disabled(opt, sel):
    return ' disabled="disabled" ' if opt == sel else ''

def _disabled(opt, sel):
    return ' disabled="disabled" ' if opt != sel else ''


def joinAttrs(attrs):
    str = ''
    for k, v in attrs.items():
        str += k + '="' + v + '" '
    return str

class Element:
    def __init__(self):
        pass
    def setHTML(self, html):
        self.html = html
    def getHTML(self):
        self.make()
        return self.html;
    def make(self):
        pass


class SelectElement(Element):
    def __init__(self, id = None, options = [], selected = None):
        Element.__init__(self)
        self.id = id
        self.options = options
        self.attrs = {}
        if self.id:
            self.attrs['id'] = self.id
            self.attrs['name'] = self.id    
        self.selectedOption = selected
        self.hasSelection = False
        #self.onChange = "this.form.action = ''; this.form.submit();"
        self.onChange = "reloadForm(this.form, this);"

    def make(self):
        html = '<select ' + joinAttrs(self.attrs) + '>'
        for opt in self.options:
#            if opt[1] == '':
#                val = '*'
            selected = ''
            if (opt[2] and not self.hasSelection) or (self.selectedOption != None and opt[1] == self.selectedOption):
                selected = 'selected'
                self.hasSelection = True
            html += '<option value="%s" %s>%s</option>' % (opt[1], selected, opt[0])
        html += '</select>\n'
        self.setHTML(html)

    def getScript(self):
        self.script = '<script type="text/javascript">\n $(document).ready(function () {'
        self.script += "$('#%s').change(function (){%s})" % (self.attrs['id'], self.onChange)
        self.script += '}); \n</script>\n'
        return self.script
