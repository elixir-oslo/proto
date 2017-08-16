#!/usr/bin/env python
import os
import sys
import third_party.safeshelve as safeshelve
from config.Config import DATA_FILES_PATH

commands = safeshelve.open(DATA_FILES_PATH + os.sep +'CommandCatalog.shelve')

if len(sys.argv) == 1:
    print 'syntax: '
    print 'to add: add [name] [command]'
    print 'to remove: rm [name] [command]'
    print 'to print: print [name]'    
    print 'to use: [name]'
    print 'available commands: '
    print ','.join(commands.keys() )
    sys.exit(0)
    
if sys.argv[1] == 'add':
    assert(len(sys.argv) >= 4)
    commands[sys.argv[2]] = ' '.join(sys.argv[3:])
elif sys.argv[1] == 'rm':
    assert(len(sys.argv) == 3)
    del commands[sys.argv[2]]
elif sys.argv[1] == 'print':
    assert(len(sys.argv) == 3)
    print commands[sys.argv[2]] 
else:
    assert(len(sys.argv) == 2)
    command = commands[sys.argv[1]]
    commands.close()
    os.system( command )
    
commands.close()
