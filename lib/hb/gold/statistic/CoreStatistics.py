import inspect
import os
import gold.statistic
import quick.statistic
from gold.statistic.MagicStatFactory import MagicStatFactory

def importStats(branch):
    statFiles = [fn for fn in os.listdir(globals()[branch].__dict__['statistic'].__path__[0]) \
                 if fn.endswith('Stat.py')]
    
    for statFile in statFiles:
        statName = os.path.splitext(statFile)[0]
#        print statName
        module = __import__('.'.join([branch, 'statistic', statName]), globals(), locals(), ['*'])
        globals().update(module.__dict__)
        
importStats('gold')
importStats('quick')

STAT_CLASS_DICT = dict([cls.__name__, cls] for cls in globals().values() \
                  if inspect.isclass(cls) and issubclass(cls, MagicStatFactory) and cls!=MagicStatFactory)
