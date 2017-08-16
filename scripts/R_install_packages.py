# This script will install the R libraries in the
# ./lib/galaxy/dependencies/r-libraries.txt file into the
# .venv/R/library virtualenv directory.
#
# Note that the script needs to be run with the virtualenv
# activated: ". .venv/bin/activate"


import sys

try:
    from rpy2.robjects import r
except:
    sys.exit(1)


class InstallError(Exception):
    pass


def _install_and_check_r_library(library):
    try:
        r("library('%s')" % library)
    except:
        install_cmds = \
            ["install.packages('%s', repos='http://cran.r-project.org', dependencies=TRUE)",
             "source('http://www.bioconductor.org/biocLite.R'); "
                "biocLite('%s', suppressUpdates=TRUE, dependencies=TRUE)",
             "install.packages('%s', repos='http://hyperbrowser.uio.no/eggs_repo/R', "
                "dependencies=TRUE)"]
        exceptions = []

        for cmd in install_cmds:
            try:
                r(cmd % (library))
                r("library('%s')" % (library))
                print "OK: Installed R package '%s'." % library
                break
            except Exception, e:
                exceptions.append(e)
        else:
            print "FAILED: Did not find or manage to install R package '%s'. Error:" % library
            for e in exceptions:
                print "        " + str(e).strip()
            raise InstallError

    print "OK: Found R package '%s'." % library


def install_and_check_r_libraries():
    r('sink(file("/dev/null", open="wt"), type="message")')

    with open('./lib/galaxy/dependencies/r-packages.txt') as req_library_file:
        for line in req_library_file:
            line = line.strip()
            if line == '' or line[0] == '#':
                continue

            try:
                _install_and_check_r_library(line)
            except InstallError, e:
                raise
            except Exception, e:
                print 'R installation error:', e
                raise


if __name__ == '__main__':
    rval = 0
    try:
        install_and_check_r_libraries()
    except InstallError, e:
        print 'Install error'
        rval = 1
    except Exception, e:
        print 'An error occurred: ', e
        rval = 1
    sys.exit( rval )
