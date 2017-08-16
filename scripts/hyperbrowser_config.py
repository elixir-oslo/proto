import sys, os
from getopt import GetoptError, getopt
import shelve

galaxy_dir = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2])
new_path = [os.path.join(galaxy_dir, "lib")]
new_path.extend(sys.path[1:])  # remove scripts/ from the path
sys.path = new_path

SHELVE_FN = galaxy_dir + '/database/hb_config.shelve'

def usage():
    print '''
Script to print a config constant for The Genomic HyperBrowser config

Usage: python setup.py -c CONSTANT

OPTIONS:
    -c CONSTANT:
        The constant whose value should be printed.

    -s, --store:
        Store all config values in a pickle file

    -r, --release:
        Release config values, deleting the pickle file

    -h, --help:
        Returns this help screen.
'''


if __name__ == '__main__':
    configConstant = ''
    store = False
    release = False

    try:
        opts, args = getopt(sys.argv[1:], 'hc:sr',
                            ['help', 'config-constant', 'store', 'release'])
    except GetoptError:
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        if opt in ('-c', '--config-constant'):
            configConstant = arg
        if opt in ('-s', '--store'):
            store = True
        if opt in ('-r', '--release'):
            release = True

    if not configConstant and not store and not release:
        # print configConstant, store, release
        print 'Error, config constant needs to be specified. Usage:'
        usage()
        sys.exit(0)

    if len(args) > 0:
        usage()
        sys.exit(0)

    if not os.environ.get('GALAXY_CONFIG_FILE'):
        os.environ['GALAXY_CONFIG_FILE'] = 'config/galaxy.ini'

    if store:
        import config.Config as Config
        shelveFile = shelve.open(SHELVE_FN)
        for attr in dir(Config):
            try:
                shelveFile[attr] = getattr(Config, attr)
            except:
                pass

    if release and os.path.exists(SHELVE_FN):
        os.remove(SHELVE_FN)

    if configConstant:
        if os.path.exists(SHELVE_FN):
            shelveFile = shelve.open(SHELVE_FN, 'r')
            print shelveFile[configConstant]
        else:
            import config.Config as Config
            print Config.__dict__.get(configConstant)

