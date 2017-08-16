# Installing the Genomic HyperBrowser

### Software requirements

The following pieces of software must be installed prior to installing
the Genomic HyperBrowser:

- Python 2.7
- R 3.2 or later
- Perl 5.8 or later
- Numpy 1.7.0 or later
- ImageMagick 6.2.8 or later (only for use in generating Google map-based heatmaps)
- rsync

Make sure that all software is available for the setup script (e.g. using `PATH`,
`PYTHONPATH`, `RHOME` and `R_LIBS` paths.)


### Installation procedure

1.  Make a copy the 'config/galaxy.ini.sample' file, named 'config/galaxy.ini',
    and edit this according to standard Galaxy configuration:

    - Make sure that the configuration options `id_secret` and `proto_id_secret`
    are set to different non-default values. Otherwise, no HyperBrowser
    specific options need to be changed from the default values.

    - In order to access your installation from other computers, you need to set
    the `host` option to `0.0.0.0`


2.  Enter the Galaxy folder and start Galaxy:

        sh run.sh 

    Note that will take a long time in the first startup due to compiling of
    Python and R packages, as well as setting up HyperBrowser test data.

    Watch the output log for any errors.

    To shut down the server, type Ctrl-K


3.  By default, the Genomic HyperBrowser will be available at:

        https://hostname:8080

    Where hostname by default is "localhost"


4.  To run the Genomic HyperBrowser in the background, use:

        sh run.sh --daemon

    to start the server, and:

        sh run.sh --stop-daemon

    to shut it down.

    Watch paster.log for any errors when you start the process as a daemon.


5.  More advanced setup and configuration will in most cases be equal to standard Galaxy setup.
    Please consult the online documentation at:

    https://galaxyproject.org/admin/get-galaxy/


### Contact
If you encounter any problems, feel free to contact us at hyperbrowser-bugs@usit.uio.no. Note that
the Genomic HyperBrowser currently does not support updating an existing installation running on an
older Galaxy version. If this is important for you, please contact us.
