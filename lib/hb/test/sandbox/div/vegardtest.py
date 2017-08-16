

print "inne i vegardtest"
import re
import itertools
import time
import datetime

import third_party.safeshelve as safeshelve
from gold.description.TrackInfo import TrackInfo
'''
from gold.util.CommonFunctions import createOrigPath
from gold.description.TrackInfo import SHELVE_FN
#SHELVE_FN = '/usit/titan/u1/vegardny/prosjekter/hyperbrowser/trackopprydding/testdata' + os.sep + 'TEST_TrackInfo.shelve'
print "SHELVE_FN=", SHELVE_FN
trackInfoShelve = safeshelve.open(SHELVE_FN, 'w')
allkeys=trackInfoShelve.keys()
trackInfoShelve.close()

count = 0
for key in allkeys:
    #print key, count
    try: 
        ti = TrackInfo.createInstanceFromKey(key)
        if ti.timeOfPreProcessing > datetime.datetime(2011, 11, 8, 0,0,0):
            print createOrigPath(ti.genome, ti.trackName) , ti.timeOfPreProcessing
            
            # ti.id = None
            # prepocess(ti) #not correct syntax.
    #else:
    #    print "before", createOrigPath(ti.genome, ti.trackName) , ti.timeOfPreProcessing
    except Exception, e: # fikk assert-feil paa track med : i navnet.
        #do nothing
        count=count
    count = count +1
    #if count > 1000:
    #    break
'''

'''
tup =(('Description', 'description', 'self.description', 'textbox'),
                ('Version', 'version', 'self.version', 'textbox'),
                ('Reference', 'reference', 'self.reference', 'textbox'),
                ('HyperBrowser contact', 'hbContact', 'self.hbContact', 'textbox'),
                ('Quality', 'quality', 'self.quality', 'textbox'),
                ('Private (our group only)', 'private', 'self.private', 'checkbox'),
                ('File type', None, 'self.fileType', 'text'),
                ('Track format', None, 'self.trackFormatName', 'text'),
                ('Mark type', None, 'self.markType', 'text'),
                ('Original element count', None, 'self.origElCount', 'text'),
                ('Element count after merging', None, 'self.clusteredElCount', 'text'),
                ('Time of preprocessing', None, 'self.timeOfPreProcessing', 'text'),
                ('Time of last update', None, 'self.timeOfLastUpdate', 'text'),
                ('Last update by', None, 'self.lastUpdatedBy', 'text'))

print tup


'''
'''
#filteredtup = filter( istextbox, tup)
#filteredtup = filter( lambda x:x[3]=='textbox' or x[3]=='checkbox', tup)
attrdict={}
for x in tup:
    if x[3]=='textbox' or x[3]=='checkbox':
     attrdict[x[1]] = x[2]

print "attrdict"
print attrdict
'''
'''
testname = ["vegard" , "vegard34", "paa", "de/g"]

a=re.match("veg", testname)
'''

'''
import string
valid_chars =''.join([chr(i) for i in range(33, 127) if i not in [47, 92]])
print valid_chars
illegalchars = ''.join(c for c in ''.join(testname) if c not in valid_chars)
if len(illegalchars)>0:
    print 'Illegal characters found in chromosome names "%s". Please rename using legal characters "%s".' % (illegalchars,valid_chars)
'''    
    
'''
import string
valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
name = "vegard_hei"
illegalchars = ''.join(c for c in name if c not in valid_chars)
if len(illegalchars)>0:
    print "Illegal characters found in chromosome names '%s'. Please rename using legal characters " % (illegalchars,valid_chars)
'''
'''
import re

a = re.search("[ /]", "abc/def")
if a:
    print "treff"
'''
from gold.description.TrackInfo import TrackInfo
genome="hg18"
tn = ['Private', 'Vegard', 'test', 'test1']

ti = TrackInfo(genome, tn)
print(ti.getUIRepr())




print "ferdig"
