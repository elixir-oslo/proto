from gold.application.GalaxyInterface import GalaxyInterface
#GalaxyInterface.run(['HCNE','density_mm8_90pc_50col'], ['genes','refseq'], '[altHyp:=ha1:]a -> PointPositioningPValStat','chr1','10m')

print GalaxyInterface.getTrackInfoRecord('hg18',['Regulation','CpG islands'])
GalaxyInterface.setTrackInfoRecord('hg18',['Regulation','CpG islands'], {'description':'Test'}, False)
print GalaxyInterface.getTrackInfoRecord('hg18',['Regulation','CpG islands'])
GalaxyInterface.setTrackInfoRecord('hg18',['Regulation','CpG islands'], {'private':True}, False)
print GalaxyInterface.getTrackInfoRecord('hg18',['Regulation','CpG islands'])
GalaxyInterface.setTrackInfoRecord('hg18',['Regulation','CpG islands'], {'description':''}, False)
GalaxyInterface.setTrackInfoRecord('hg18',['Regulation','CpG islands'], {'private':False}, False)
print GalaxyInterface.getTrackInfoRecord('hg18',['Regulation','CpG islands'])
