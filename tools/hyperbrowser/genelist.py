import sys, os, getopt,types

import galaxy.eggs
from galaxy.util import restore_text

from gold.application.GalaxyInterface import *


def main():
    output = sys.argv[1]
    genes = sys.argv[2]
    genome = sys.argv[3]
    
    genelist = []
    genes = restore_text(genes).replace('XX', '\n')
    for gene in genes.split('\n'):
        gene = gene.strip()
        if gene != '':
            genelist.append(gene)

    print 'GalaxyInterface.getEnsemblGenes', (genome, genelist, output)
    #sys.stdout = open(output, "w", 0)
    GalaxyInterface.getEnsemblGenes(genome, genelist, output)
    
if __name__ == "__main__":
    main()
