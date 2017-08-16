
# cd /usit/invitro/data/hyperbrowser/hb_core_developer/trunk    ##jeg klarer ikke kjoere herfra. Noe feil i oppsettet mitt som det var foer.
# python test/sandbox/div/standardfolders.py

## slik kjoerer jeg det.
# cd /usit/invitro/data/hyperbrowser/hb_core_stable/trunk
# python ../../hb_core_developer/trunk/test/sandbox/div/standardfolders.py


print("start standardfolders.py")

from gold.description.TrackInfo import TrackInfo
from quick.application.GalaxyInterface import GalaxyInterface
from gold.util.CommonFunctions import getOrigFn, getOrigFns


# Iterates genomes and updateorcreate standardfolders.
def updateStandardFoldersForAllGenomes():
    for genomeinfo in GalaxyInterface.getAllGenomes():
     genome = genomeinfo[1]
     if genome=="hg18":  #trengs dette?
           genome="hg18"
     if genome=="TestGenome":   ############### ta bort for aa oppdatere alle genomer.
        updateOrCreateStandardFolders(genome)
     
     
def updateOrCreateStandardFolders(genome):
    print "update or create ", genome
    for x in standardFolderInfo:
        ti = TrackInfo(genome, x[0])
        ti.description = x[1]
        ti.reference = x[2]
        ti.quality = x[3]
        
        ### sjekke om folderen eksisterer, hvis ikke lage den. Dette er ikke helt implementer da jeg er usikker om jeg fikk det til med eksisterende metoder.
        if not getOrigFns( genome, x[0], ''): # returns empty list if no folder? But what does it return when no tracks is in the folder?
            print x[0] ,"is missing"# lage folder og preprocess?

        #print "ti=", ti
        ti.store()


### name, description, referece, quality
standardFolderInfo = [
    [ ["Genome build properties"] , "Very large segments such as Chromosome arms, Cytobands, Assambly gaps and so on.", "", ""],
    [ ["Comparative genomics"], "Similarities between this genome and others, typically conserved regions.", "", ""],
    [ ["Gene regulation"], "Such as miRNA, Transcription Factor related and more.", "", ""],
    [ ["Genes and gene subsets"], "Genes, gene subunits and gene sets from different authorities as Ensembl, Entrez and so on.", "", ""],
    [ ["Sequence"], "?", "", ""],
    [ ["Expression"], "Data from RNA experiments.", "", ""],
    [ ["Phenotype and disease associations"], "Regions associated with traits or disease reported by scientific articles and data bases.", "", ""] ]

updateStandardFoldersForAllGenomes()
print("finished standardfolders")