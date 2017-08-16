from proto.RSetup import r
from config.Config import HB_SOURCE_CODE_BASE_DIR
import os

PLOT_BED_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'rCode', 'plotBed.r'])
PLOT_CHR_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'rCode', 'ChromosomePlot.r'])
OUTPUT_PATH = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'data'])

r('source("%s")' % PLOT_BED_FN)
r('source("%s")' % PLOT_CHR_FN)
r('loadedBedData <- plot.bed("/xanadu/home/geirksa/_data/test.wig")')
print len(r['loadedBedData'])
#r('plot.chrom(segments=loadedBedData, dir.print="%s", data.unit="bp")' % OUTPUT_PATH)
r('plot.chrom(segments=loadedBedData, data.unit="bp", dir.print="/hyperdata")')
