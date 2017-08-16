#!/bin/bash
## sbatch parameters:
# Project:
#SBATCH --account=nrr
#
# Wall clock limit:
#SBATCH --time=01:00:00
#
# Max memory usage:
#SBATCH --mem-per-cpu=8G

## Set up job environment
source /site/bin/jobsetup

#cp $datafilename $SCRATCH
#chkfile $datafilename

module load imagemagick

module load R/2.7.2
export RHOME="/xanadu/site/common/VERSIONS/R-2.7.2/lib64/R"

module load compython/2.5

cd $SCRATCH


datafilename=$1

#module list 2> $datafilename

TOOLS=/xanadu/project/rrresearch/galaxy_developer/tools/hyperbrowser
export PYTHONPATH=/xanadu/project/rrresearch/galaxy_developer/galaxy_hb/lib:/xanadu/project/rrresearch/new_hb_develop_titan/trunk

umask 0002
python $TOOLS/batchrun-for-titan.py $datafilename

touch ${datafilename}.done
