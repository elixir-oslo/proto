#note cannot import HB.GalaxyInterface here due to rpy threading issue


from proto.hyper_gui import *
from proto.hyper_gui import _disabled


class TrackWrapper:
    has_subtrack = False

    def __init__(self, name, api, preTracks, galaxy, datasets, genome='', ucscTracks=True):
        params = galaxy.params
        self.api = api
        self.galaxy = galaxy
        self.datasets = datasets
        self.nameMain = name
        self.nameFile = self.nameMain + 'file'
        self.nameState = self.nameMain + '_state'
        self.state = params.get(self.nameState)
        if self.state != None:
            self.state = unquote(self.state)

        if params.has_key(name) and (not params.has_key(self.nameLevel(0))):
            parts = params[name].split(':')
            if len(parts) == 4 and parts[0] == 'galaxy':
                params[self.nameFile] = params[name]
                self.setValueLevel(0, parts[0])
            else:
                for i in range(len(parts)):
                    self.setValueLevel(i, parts[i])
        
        self.preTracks = []
        self.extraTracks = []
        if len(datasets) > 0:
            self.extraTracks.append(('-- From history (bed, wig, ...) --', 'galaxy', False))
        self.extraTracks += preTracks

        self.main = self.valueLevel(0)
        self.file = params.get(self.nameFile)
        if not self.file and len(self.datasets) > 0:
            self.file = self.galaxy.makeHistoryOption(self.datasets[0])[1]
        else:
            self._checkHistoryFile()

        self.tracks = []
        self.ucscTracks = ucscTracks
        self.genome = genome
        self.numLevels = len(self.asList())
        self.valid = True

    def _checkHistoryFile(self):
        did = self.galaxy.getHistoryOptionId(self.file)
        for dataset in self.datasets:
            if dataset.dataset_id == did:
                self.file = self.galaxy.makeHistoryOption(dataset)[1]
                break

    def optionsFromHistory(self, sel=None, exts=None):
        return self.galaxy.optionsFromHistory(exts, sel=sel, datasets=self.datasets)

    def getState(self, q = True):
        return quote(self.state) if self.state and q else self.state if self.state else ''

    def fetchTracks(self):
        for i in range(0, self.numLevels + 1):
            self.getTracksForLevel(i)
        self.numLevels = len(self.tracks)
   
    def hasSubtrack(self):
        ldef = len(self.definition())
        if len(self.tracks) > ldef:
            if len(self.tracks[ldef]) > 0:
                return True
        return False

    def nameLevel(self, level):
        return self.nameMain + '_' + str(level)

    def valueLevel(self, level):
        val = self.galaxy.params.get(self.nameLevel(level))
        if val == '-':
            return None
        return val

    def setValueLevel(self, level, val):
        self.galaxy.params[self.nameLevel(level)] = val

    def asList(self):
        vals = []
        for i in range(0, 10):
            val = self.valueLevel(i)
            if val != None and val != '-':
                vals.append(val)
            else:
                break
        return vals

    def asString(self):
        vals = self.definition(False)
        return ':'.join(vals)

    def selected(self):
        if (len(self.definition()) >= 1 and not self.hasSubtrack()) or self.valueLevel(0) == '':
            self.valid = self.api.trackValid(self.genome, self.definition())
            if self.valid == True:
                return True
        print self.valid
        return False

    def definition(self, unquotehistoryelementname=True, use_path=False):
        arr = [self.main]
        if self.main == 'galaxy' and self.file:
            f = self.file.split(':')
            if not use_path:
                path = self.galaxy.encode_id(f[2]) if len(f[2]) < 16 and f[2].isdigit() else f[2]
            else:
                path = self.galaxy.getDataFilePath(f[2])
            arr.append(str(f[1]))
            arr.append(str(path))
            if unquotehistoryelementname:
                arr.append(str(unquote(f[3])))
            else:
                arr.append(str(f[3]))
        elif self.valueLevel(0) == '':
            arr = []
        else:
            arr = self.asList()
        return arr



    def getTracksForLevel(self, level):
        if not self.genome:
            return []
        if level < len(self.tracks):
            return self.tracks[level]
        self.has_subtrack = False
        tracks = None
        if level == 0:
            tracks = self.mainTracks()
            val = self.valueLevel(0)
            if val != None:
                ok = False
                for t in tracks:
                    if val == t[1]:
                        ok = True
                if not ok:
                    self.setValueLevel(0, None)
        else:
            trk = []
            for i in range(0, level):
                val = self.valueLevel(i)
                if val != None and val != 'galaxy':
                    trk.append(val)
                else:
                    trk = []
                    break
            if len(trk) > 0 and val not in ['', '-']:
                try:
                    tracks, self.state = self.api.getSubTrackNames(self.genome, trk, False, self.galaxy.getUserName(), self.state)
                except OSError, e:
                    self.setValueLevel(i, None)
                    self.has_subtrack = False
                    if e.errno != 2:
                        raise e
                if tracks and len(tracks) > 0:
                    self.has_subtrack = True
        if tracks == None:
            self.setValueLevel(level, None)
        else:
            self.tracks.append(tracks)
        return tracks

    def mainTracks(self):
        tracks = self.api.getMainTrackNames(self.genome, self.preTracks, self.extraTracks, self.galaxy.getUserName(), self.ucscTracks)
        return tracks



class TrackSelectElement(SelectElement):
    def __init__(self, track, level):
        SelectElement.__init__(self)
        self.id = track.nameLevel(level)
        self.attrs['id'] = self.id
        self.attrs['name'] = self.id
        self.options = [('----- Select ----- ', '-', False)]
        self.selectedOption = track.valueLevel(level)
        self.onChange = "try{$('#" + track.nameLevel(level + 1) + "').val('')} catch(e){} " + self.onChange
        opts = track.getTracksForLevel(level)
        if opts:
            self.options.extend(opts)


def optionListFromDatasets(datasets, exts = None, sel = None):
    assert False, 'fix or remove me'
    list = []
    for dataset in datasets:
        if exts == None or dataset.extension in exts:
            val = 'galaxy,' + str(dataset.dataset_id) + ',' + dataset.extension
            txt = '%d: %s [%s]' % (dataset.hid, dataset.name, val)
            tup = (txt, val, False)
            list.append(tup)
    return list


# def getValidRScripts(self):
#     datasets = []
#     try:
#         for dataset in self.getHistory(['R']):
#             rfilename = self.getDataFilePath(dataset.dataset_id)
#             qid = '[scriptFn:=' + rfilename.encode('hex_codec') + ':] -> CustomRStat'
#             # if hyper.isRScriptValid(tracks[0].definition(), tracks[1].definition(), qid):
#             datasets.append(dataset)
#     except AttributeError:
#         pass
#     return datasets
