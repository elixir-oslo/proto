'''
Created on Jun 26, 2015

@author: boris
'''


from config.Config import STATIC_DIR, GALAXY_BASE_DIR, HB_SOURCE_CODE_BASE_DIR
from proto.CommonFunctions import createGalaxyToolURL, getGalaxyUploadLinkOnclick
from quick.webtools.article.ClusTrackTool import ClusTrackTool
from quick.webtools.gsuite.CoincidingTracksFromTwoGSuitesTool import CoincidingTracksFromTwoGSuitesTool
from quick.webtools.gsuite.CompileGSuiteFromArchiveTool import CompileGSuiteFromArchiveTool
from quick.webtools.gsuite.CreateGSuiteFileFromHistoryElementsTool import CreateGSuiteFileFromHistoryElementsTool
from quick.webtools.gsuite.GSuiteRepresentativeAndUntypicalTrackTool import GSuiteRepresentativeAndUntypicalTrackTool
from quick.webtools.gsuite.GSuiteTracksCoincidingWithQueryTrackTool import GSuiteTracksCoincidingWithQueryTrackTool
from quick.webtools.gsuite.PilotPageBasicOverviewOfTracksInGSuiteTool import PilotPageBasicOverviewOfTracksInGSuiteTool
from quick.webtools.gsuite.PilotPageSimilarityAndUniquenessOfTracksTool import \
    PilotPageSimilarityAndUniquenessOfTracksTool
from quick.webtools.gtrack.TabularToGtrackTool import TabularToGtrackTool
from quick.webtools.imports.TrackGlobalSearchTool import TrackGlobalSearchTool
from quick.webtools.imports.TrackSourceTestTool import TrackSourceTestTool
from quick.webtools.tfbs.AllTargetsOfTfs import AllTargetsOfTfs
from quick.webtools.tfbs.AllTfsOfRegions import AllTfsOfRegions
from quick.webtools.track.ExtractSubtracksTool import ExtractSubtracksTool

from collections import OrderedDict
from LinkExpansion import LinkExpansion


def getNameFromToolXml(toolXmlFn):
    from config.Config import HB_SOURCE_CODE_BASE_DIR
    import xml.etree.ElementTree as ET
    root = ET.parse(HB_SOURCE_CODE_BASE_DIR + toolXmlFn).getroot()
    return root.attrib['name']


class WelcomePageGenerator(object):
    '''
    Generate content directly to welcome.html.
    It parses the file wpcontent.txt, and to get the contents for the new welcome.html it concatenates:
    1. wpprefix.html
    2. the parsed wpcontent.txt
    3. wppostfix.html

    It also expands all links with the LinkExpansion class (see LinkExpansion doc for more info on expandable links).

    '''

    TRACK_VS_COLLECTION_TOOL_TITLE = getNameFromToolXml('/quick/webtools/gsuite/GSuiteTracksCoincidingWithQueryTrackTool.xml')
    COLLECTION_TOOL_TITLE = getNameFromToolXml('/quick/webtools/gsuite/GSuiteRepresentativeAndUntypicalTrackTool.xml')
    COLLECTION_VS_COLLECTION_TOOL_TITLE = getNameFromToolXml('/quick/webtools/gsuite/CoincidingTracksFromTwoGSuitesTool.xml')
    UPLOAD_FILE_TOOL_TITLE = "Upload file"
    BASIC_SEARCH_TOOL_TITLE = getNameFromToolXml('/quick/webtools/imports/TrackGlobalSearchTool.xml')
    ADVANCED_SEARCH_TOOL_TITLE = getNameFromToolXml('/quick/webtools/imports/TrackSourceTestTool.xml')
    GSUITE_FROM_HISTORY_TOOL_TITLE = getNameFromToolXml('/quick/webtools/gsuite/CreateGSuiteFileFromHistoryElementsTool.xml')
    DEMO_TRACK_TITLE = "sample track with Multiple Sclerosis-associated regions, expanded 10kb in both directions"
    OVERLAP_BETWEEN_TRACKS_TITLE = getNameFromToolXml('/quick/webtools/gsuite/PilotPageBasicOverviewOfTracksInGSuiteTool.xml')
    EXTRACT_FROM_ARCHIVE_TITLE = getNameFromToolXml('/quick/webtools/gsuite/CompileGSuiteFromArchiveTool.xml')
    SIMILARITY_AND_UNIQUENESS_TITLE = getNameFromToolXml('/quick/webtools/gsuite/PilotPageSimilarityAndUniquenessOfTracksTool.xml')
    CONSTRUCT_GSUITE_PAGE_TITLE = "a tool for constructing a track suite (GSuite)"
    GSUITE_FROM_REPOSITORY_TOOL_TITLE = getNameFromToolXml('/quick/webtools/track/ExtractSubtracksTool.xml')
    #     DEMO_GWAS_BLUPRINT_TRACK_TITLE = "sample GWAS Blueprint track"
    DEMO_TCGA_PRAD_TRACK_TITLE = "sample track with genomic locations of somatic variants in prostate adenocarcinoma (the COAD set from The Cancer Genome Atlas)"
    DEMO_GSUITE_159_TF_GM12878_TITLE = "sample GSuite collection: genomic locations of binding sites of various TFs for the gm12878 lymphoblastoid cell line"
    DEMO_GSUITE_CMYC_43_CELL_TYPES_TITLE = "sample GSuite collection: genomic locations of binding sites of the transcription factor c-myb in various cell types"
    DEMO_GSUITE_DNASE_40_CELL_TYPES_TITLE = "sample GSuite of DNaseI accessibility for different cell types"
    DEMO_GSUITE_HIST_K562_TITLE = "sample GSuite collection: genomic locations of various histone modifications for the K562 chronic myelogenous leukemia cell line"
    DEMO_GSUITE_GWAS_TITLE = "sample GSuite collection: genomic locations of lead SNP variants for various traits"
    CREATE_GTRACK_FROM_TABULAR_TOOL_TITLE = getNameFromToolXml('/quick/webtools/gtrack/TabularToGtrackTool.xml')
    DEMO_TRACK_K562_ENHANCERS_TITLE = "sample track with genomic locations of enhancer regions active within the K562 chronic myelogenous leukemia cell line"
    CLUS_TRACK_TOOL_TITLE = getNameFromToolXml('/quick/webtools/article/ClusTrackTool.xml')
    DEMO_GSUITE_SOMATIC_COAD_TITLE = "sample GSuite collection: somatic variant locations for 216 Colon adenocarcinoma patients (the COAD dataset from The Cancer Genome Atlas)"
    DEMO_GSUITE_SELECTED_TFBS_TITLE = "sample GSuite collection: genomic locations of binding sites of selected TFs (CEBPB, FOS, JUN, MYC, NANOG, NR2F2, TEAD4)"
    DEMO_GSUITE_K562_ENHANCERS_TITLE = "sample track with genomic locations of enhancer regions active within the K562 chronic myelogenous leukemia cell line"
    DEMO_TRACK_MYC_BS_TITLE = "sample track with Myc binding sites"
    DEMO_GSUITE_TCGA_EXOME_TITLE = "sample GSuite collection: exon locations for 560 genes included in the Cancer Census"
    FILE_FORMATS_PAGE_TITLE = "supported file formats"
    DEMO_GSUITE_TFS_WITH_PWMS_TITLE = "sample GSuite collection: genomic locations of binding sites of selected TFs in K562 (CTCF, c-Jun, c-Myc, GATA-1 and more) with added PWM metadata"
    MATCH_TF_WITH_PWMS_TOOL_TITLE = getNameFromToolXml('/quick/webtools/gsuite/MatchTfWithPWM.xml')
    EDIT_GSUITE_METADATA_TOOL_TITLE = getNameFromToolXml('/quick/webtools/gsuite/EditGsuiteMetadataTool.xml')
    GSUITE_TRACKS_VS_GSUITE_TOOL_TITLE = getNameFromToolXml('/quick/webtools/gsuite/DetermineSuiteTracksCoincidingWithAnotherSuite.xml')
    DEMO_TRACK_LICA_CN_TITLE = "sample track with genomic locations of somatic variants in liver cancer (the LICA-CN set from The Cancer Genome Atlas)"
    ALL_TARGETS_OF_TFS_TOOL_TITLE = getNameFromToolXml('/quick/webtools/tfbs/AllTargetsOfTfs.xml')
    ALL_TFS_OF_REGION_TOOL_TITLE = getNameFromToolXml('/quick/webtools/tfbs/AllTfsOfRegions.xml')
    TF_BINDING_DISRUPTION_TOOL_TITLE = getNameFromToolXml('/quick/webtools/article/TfBindingDisruption.xml')

    from quick.util.CommonFunctions import getLoadToGalaxyHistoryURL
    LOAD_GSUITE_SINGLE_TRACK_SAMPLE_FILE_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/MS_regions_expanded_10kb.bed', 'hg19',
         'bed', urlPrefix='..', histElementName=DEMO_TRACK_TITLE)
    LOAD_GSUITE_159_TF_GM12878_SAMPLE_GSUITE_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/159_TFs_in_gm12878_cell_type.gsuite',
         'hg19', 'gsuite', urlPrefix='..', histElementName=DEMO_GSUITE_159_TF_GM12878_TITLE)
    LOAD_GSUITE_CMYC_43_CELL_TYPES_SAMPLE_GSUITE_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/cMyc_across_43_cell_types.gsuite', 'hg19',
         'gsuite', urlPrefix='..', histElementName=DEMO_GSUITE_CMYC_43_CELL_TYPES_TITLE)
    LOAD_GSUITE_DNASE_40_CELL_TYPES_SAMPLE_GSUITE_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/DNase_in_40_cell_types.gsuite', 'hg19',
         'gsuite', urlPrefix='..', histElementName=DEMO_GSUITE_DNASE_40_CELL_TYPES_TITLE)
    LOAD_GSUITE_TCGA_PRAD_SAMPLE_TRACK_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/TCGA_PRAD.gtrack', 'hg19', 'gtrack',
         urlPrefix='..', histElementName=DEMO_TCGA_PRAD_TRACK_TITLE)
    LOAD_GSUITE_GWAS_SAMPLE_GSUITE_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/gwas.gsuite', 'hg19', 'gsuite',
         urlPrefix='..', histElementName=DEMO_GSUITE_GWAS_TITLE)
    LOAD_GSUITE_HIST_K562_SAMPLE_GSUITE_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/hist_k562.gsuite', 'hg19', 'gsuite',
         urlPrefix='..', histElementName=DEMO_GSUITE_HIST_K562_TITLE)
    LOAD_GSUITE_K562_ENHANCERS_SAMPLE_BED_TRACK_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/demo_track_k562_enhancers.bed', 'hg19', 'bed',
         urlPrefix='..', histElementName=DEMO_TRACK_K562_ENHANCERS_TITLE)
    LOAD_GSUITE_COAD_TCGA_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/demo_gsuite_sv_colade.gsuite', 'hg19', 'gsuite',
         urlPrefix='..', histElementName=DEMO_GSUITE_SOMATIC_COAD_TITLE)
    LOAD_DEMO_GSUITE_SELECTED_TFBS_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/demo_gsuite_selected_tfbs.gsuite', 'hg19', 'gsuite',
         urlPrefix='..', histElementName=DEMO_GSUITE_SELECTED_TFBS_TITLE)
    LOAD_DEMO_GSUITE_K562_ENHANCERS_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/demo_gsuite_k562_enhancers.gsuite', 'hg19', 'gsuite',
         urlPrefix='..', histElementName=DEMO_GSUITE_K562_ENHANCERS_TITLE)
    LOAD_DEMO_TRACK_MYC_BS_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/demo_track_myc_bs.bed', 'hg19', 'bed',
         urlPrefix='..', histElementName=DEMO_TRACK_MYC_BS_TITLE)
    LOAD_DEMO_GSUITE_TCGA_EXOME_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/demo_gsuite_tcga_exome.gsuite', 'hg19', 'gsuite',
         urlPrefix='..', histElementName=DEMO_GSUITE_TCGA_EXOME_TITLE)
    LOAD_DEMO_GSUITE_TFS_WITH_PWMS_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/demo_gsuite_tfs_with_pwms.gsuite', 'hg19', 'gsuite',
         urlPrefix='..', histElementName=DEMO_GSUITE_TFS_WITH_PWMS_TITLE)
    LOAD_DEMO_TRACK_LICA_CN_URL = getLoadToGalaxyHistoryURL \
        (STATIC_DIR + '/data/gsuite/demo_track_lica_cn.gtrack', 'hg19', 'gtrack',
         urlPrefix='..', histElementName=DEMO_TRACK_LICA_CN_TITLE)

    TRACK_VS_COLLECTION_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_g_suite_tracks_coinciding_with_query_track_tool&isBasic=1&isBasic=True"
    COLLECTION_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_g_suite_representative_and_untypical_track_tool&isBasic=1&isBasic=True"
    COLLECTION_VS_COLLECTION_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_coinciding_tracks_from_two_g_suites_tool&isBasic=1&isBasic=True"
    UPLOAD_FILE_TOOL_URL = createGalaxyToolURL('upload1')
    UPLOAD_FILE_TOOL_ONCLICK = getGalaxyUploadLinkOnclick()
    BASIC_SEARCH_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_track_global_search_tool" #add basicQuestionId param
    ADVANCED_SEARCH_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_track_source_test_tool" #add basicQuestionId param
    GSUITE_FROM_HISTORY_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_create_g_suite_file_from_history_elements_tool" #add basicQuestionId param
#     DEMO_TRACK_URL = "../tool_runner?tool_id=file_import&dbkey=hg19&runtool_btn=yes&input=L3NvZnR3YXJlL2dhbGF4eS9nYWxheHlfZGV2ZWxvcGVyL3N0YXRpYy9oeXBlcmJyb3dzZXIvZGF0YS9nc3VpdGUvTVNfcmVnaW9uc19leHBhbmRlZF8xMGtiLmJlZA==&datatype=bed" #add basicQuestionId param
    DEMO_TRACK_URL = LOAD_GSUITE_SINGLE_TRACK_SAMPLE_FILE_URL #add basicQuestionId param
    OVERLAP_BETWEEN_TRACKS_URL = "../hyper?mako=generictool&tool_id=hb_pilot_page_overlap_between_tracks_tool"
    EXTRACT_FROM_ARCHIVE_URL = "../hyper?mako=generictool&tool_id=hb_compile_g_suite_from_archive_tool" #add basicQuestionId param
    SIMILARITY_AND_UNIQUENESS_URL = "../hyper?mako=generictool&tool_id=hb_pilot_page_similarity_and_uniqueness_of_tracks_tool"
    CONSTRUCT_GSUITE_PAGE_URL = "welcome_gsuite_construct.html?aaa=bbb" #add basicQuestionId; aaa=bbb is a temporary hack because of the way we build some of the urls later.
    GSUITE_FROM_REPOSITORY_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_extract_subtracks_tool"
#     DEMO_GWAS_BLUPRINT_TRACK_URL = "$LOAD_GSUITE_GWAS_BLUEPRINT_SAMPLE_TRACK_URL"
    DEMO_TCGA_PRAD_TRACK_URL = LOAD_GSUITE_TCGA_PRAD_SAMPLE_TRACK_URL
    DEMO_GSUITE_159_TF_GM12878_URL = LOAD_GSUITE_159_TF_GM12878_SAMPLE_GSUITE_URL
    DEMO_GSUITE_CMYC_43_CELL_TYPES_URL = LOAD_GSUITE_CMYC_43_CELL_TYPES_SAMPLE_GSUITE_URL
    DEMO_GSUITE_DNASE_40_CELL_TYPES_URL = LOAD_GSUITE_DNASE_40_CELL_TYPES_SAMPLE_GSUITE_URL
    DEMO_GSUITE_HIST_K562_URL = LOAD_GSUITE_HIST_K562_SAMPLE_GSUITE_URL
    DEMO_GSUITE_GWAS_URL = LOAD_GSUITE_GWAS_SAMPLE_GSUITE_URL
    CREATE_GTRACK_FROM_TABULAR_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_tabular_to_gtrack_tool" #add basicQuestionId param
    DEMO_TRACK_K562_ENHANCERS_URL = LOAD_GSUITE_K562_ENHANCERS_SAMPLE_BED_TRACK_URL
    CLUS_TRACK_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_clus_track_tool&isBasic=1&isBasic=True"
    DEMO_GSUITE_SOMATIC_COAD_URL = LOAD_GSUITE_COAD_TCGA_URL
    DEMO_GSUITE_SELECTED_TFBS_URL = LOAD_DEMO_GSUITE_SELECTED_TFBS_URL
    DEMO_GSUITE_K562_ENHANCERS_URL = LOAD_DEMO_GSUITE_K562_ENHANCERS_URL
    DEMO_TRACK_MYC_BS_URL = LOAD_DEMO_TRACK_MYC_BS_URL
    DEMO_GSUITE_TCGA_EXOME_URL = LOAD_DEMO_GSUITE_TCGA_EXOME_URL
    FILE_FORMATS_PAGE_URL = "welcome_formats.html?aaa=bbb"
    DEMO_GSUITE_TFS_WITH_PWMS_URL = LOAD_DEMO_GSUITE_TFS_WITH_PWMS_URL
    MATCH_TF_WITH_PWMS_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_match_tf_with_pwm&isBasic=1&isBasic=True"
    EDIT_GSUITE_METADATA_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_edit_gsuite_metadata_tool&isBasic=1&isBasic=True"
    GSUITE_TRACKS_VS_GSUITE_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_determine_suite_tracks_coinciding_with_another_suite&isBasic=1&isBasic=True"
    DEMO_TRACK_LICA_CN_URL = LOAD_DEMO_TRACK_LICA_CN_URL
    ALL_TARGETS_OF_TFS_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_all_targets_of_tfs&isBasic=1&isBasic=True"
    ALL_TFS_OF_REGION_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_all_tfs_of_regions&isBasic=1&isBasic=True"
    TF_BINDING_DISRUPTION_TOOL_URL = "../hyper?mako=generictool&tool_id=hb_tf_binding_disruption"

    TRACK_VS_COLLECTION_TOOL_HOVER = ""
    COLLECTION_TOOL_HOVER = ""
    COLLECTION_VS_COLLECTION_TOOL_HOVER = ""
    UPLOAD_FILE_TOOL_HOVER = ""
    BASIC_SEARCH_TOOL_HOVER = ""
    ADVANCED_SEARCH_TOOL_HOVER = ""
    GSUITE_FROM_HISTORY_TOOL_HOVER = ""
    DEMO_TRACK_HOVER = ""
    OVERLAP_BETWEEN_TRACKS_HOVER = ""
    EXTRACT_FROM_ARCHIVE_HOVER = ""
    SIMILARITY_AND_UNIQUENESS_HOVER = ""
    CONSTRUCT_GSUITE_PAGE_HOVER = ""
    GSUITE_FROM_REPOSITORY_TOOL_HOVER = ""
#     DEMO_GWAS_BLUPRINT_TRACK_HOVER = ""
    DEMO_TCGA_PRAD_TRACK_HOVER = ""
    DEMO_GSUITE_159_TF_GM12878_HOVER = ""
    DEMO_GSUITE_CMYC_43_CELL_TYPES_HOVER = ""
    DEMO_GSUITE_DNASE_40_CELL_TYPES_HOVER = ""
    DEMO_GSUITE_HIST_K562_HOVER = ""
    DEMO_GSUITE_GWAS_HOVER = ""
    CREATE_GTRACK_FROM_TABULAR_TOOL_HOVER = ""
    DEMO_TRACK_K562_ENHANCERS_HOVER = ""
    CLUS_TRACK_TOOL_HOVER = ""
    DEMO_GSUITE_SOMATIC_COAD_HOVER = ""
    DEMO_GSUITE_SELECTED_TFBS_HOVER = ""
    DEMO_GSUITE_K562_ENHANCERS_HOVER = ""
    DEMO_TRACK_MYC_BS_HOVER = ""
    DEMO_GSUITE_TCGA_EXOME_HOVER = ""
    FILE_FORMATS_HOVER = ""
    DEMO_GSUITE_TFS_WITH_PWMS_HOVER = ""
    MATCH_TF_WITH_PWMS_TOOL_HOVER = ""
    EDIT_GSUITE_METADATA_TOOL_HOVER = ""
    GSUITE_TRACKS_VS_GSUITE_TOOL_HOVER = ""
    DEMO_TRACK_LICA_CN_HOVER = ""
    ALL_TARGETS_OF_TFS_TOOL_HOVER = ""
    ALL_TFS_OF_REGION_TOOL_HOVER = ""
    TF_BINDING_DISRUPTION_TOOL_HOVER = ""

    TRACK_VS_COLLECTION_TOOL_PLACEHOLDER = "__tc_tool__"
    COLLECTION_TOOL_PLACEHOLDER = "__c_tool__"
    COLLECTION_VS_COLLECTION_TOOL_PLACEHOLDER = "__cc_tool__"
    UPLOAD_FILE_TOOL_PLACEHOLDER = "__uf_tool__"
    BASIC_SEARCH_TOOL_PLACEHOLDER = "__bs_tool__"
    ADVANCED_SEARCH_TOOL_PLACEHOLDER = "__as_tool__"
    GSUITE_FROM_HISTORY_TOOL_PLACEHOLDER = "__ch_tool__"
    DEMO_TRACK_PLACEHOLDER = "__dt_ms__"
    OVERLAP_BETWEEN_TRACKS_PLACEHOLDER = "__pp_obt_tool__"
    EXTRACT_FROM_ARCHIVE_PLACEHOLDER = "__efa_tool__"
    SIMILARITY_AND_UNIQUENESS_PLACEHOLDER = "__pp_sau_tool__"
    CONSTRUCT_GSUITE_PAGE_PLACEHOLDER = "__page_cg__"
    GSUITE_FROM_REPOSITORY_TOOL_PLACEHOLDER = "__cr_tool__"
#     DEMO_GWAS_BLUPRINT_TRACK_PLACEHOLDER = "__dt_gwas__"
    DEMO_TCGA_PRAD_TRACK_PLACEHOLDER = "__dt_tcga__"
    DEMO_GSUITE_159_TF_GM12878_PLACEHOLDER = "__dgs_tf_gm12878__"
    DEMO_GSUITE_CMYC_43_CELL_TYPES_PLACEHOLDER = "__dgs_cmyc__"
    DEMO_GSUITE_DNASE_40_CELL_TYPES_PLACEHOLDER = "__dgs_dnase__"
    DEMO_GSUITE_HIST_K562_PLACEHOLDER = "__dgs_hist_k562__"
    DEMO_GSUITE_GWAS_PLACEHOLDER = "__dgs_gwas__"
    CREATE_GTRACK_FROM_TABULAR_TOOL_PLACEHOLDER = "__gt_tab_tool__"
    DEMO_TRACK_K562_ENHANCERS_PLACEHOLDER = "__dt_k562_enhancers__"
    CLUS_TRACK_TOOL_PLACEHOLDER = "__cgst_tool__"
    DEMO_GSUITE_SOMATIC_COAD_PLACEHOLDER = "__dgs_sv_colade__"
    DEMO_GSUITE_SELECTED_TFBS_PLACEHOLDER = "__selected_tfbs__"
    DEMO_GSUITE_K562_ENHANCERS_PLACEHOLDER = "__dt_k562_enhancers__"
    DEMO_TRACK_MYC_BS_PLACEHOLDER = "__myc_bs__"
    DEMO_GSUITE_TCGA_EXOME_PLACEHOLDER = "__dgs_tcga_exome__"
    FILE_FORMATS_PAGE_PLACEHOLDER = "__page_ff__"
    DEMO_GSUITE_TFS_WITH_PWMS_PLACEHOLDER = "__tfs_with_pwms__"
    MATCH_TF_WITH_PWMS_TOOL_PLACEHOLDER = "__tf_to_pwm_tool__"
    EDIT_GSUITE_METADATA_TOOL_PLACEHOLDER = "__edit_mdc_tool__"
    GSUITE_TRACKS_VS_GSUITE_TOOL_PLACEHOLDER = "__event_incidence_tool__"
    DEMO_TRACK_LICA_CN_PLACEHOLDER = "__dt_lica_cn__"
    ALL_TARGETS_OF_TFS_TOOL_PLACEHOLDER = "__tf_scan_targets__"
    ALL_TFS_OF_REGION_TOOL_PLACEHOLDER = "__region_scan_tfs__"
    TF_BINDING_DISRUPTION_TOOL_PLACEHOLDER = "__ftbd_tool__"

    #The 4th element of the tuple is a flag whether we should add the parameter basicQuestionId to the url to enable redirect back to the basic welcome page
    #The 5th element of the tuple is a flag whether we should add the parameter nmQid to the url to enable the analysis question to be displayed in the tool
    PLACEHOLDERS_DICT = {
                        TRACK_VS_COLLECTION_TOOL_PLACEHOLDER : (TRACK_VS_COLLECTION_TOOL_URL, TRACK_VS_COLLECTION_TOOL_TITLE, TRACK_VS_COLLECTION_TOOL_HOVER, True, True, False),
                        COLLECTION_TOOL_PLACEHOLDER : (COLLECTION_TOOL_URL, COLLECTION_TOOL_TITLE, COLLECTION_TOOL_HOVER, True, True, False),
                        COLLECTION_VS_COLLECTION_TOOL_PLACEHOLDER : (COLLECTION_VS_COLLECTION_TOOL_URL, COLLECTION_VS_COLLECTION_TOOL_TITLE, COLLECTION_VS_COLLECTION_TOOL_HOVER, True, True, False),
                        UPLOAD_FILE_TOOL_PLACEHOLDER : (UPLOAD_FILE_TOOL_URL, UPLOAD_FILE_TOOL_TITLE, UPLOAD_FILE_TOOL_HOVER, False, False, UPLOAD_FILE_TOOL_ONCLICK),
                        BASIC_SEARCH_TOOL_PLACEHOLDER : (BASIC_SEARCH_TOOL_URL, BASIC_SEARCH_TOOL_TITLE, BASIC_SEARCH_TOOL_HOVER, True, False, False),
                        ADVANCED_SEARCH_TOOL_PLACEHOLDER : (ADVANCED_SEARCH_TOOL_URL, ADVANCED_SEARCH_TOOL_TITLE, ADVANCED_SEARCH_TOOL_HOVER, True, False, False),
                        GSUITE_FROM_HISTORY_TOOL_PLACEHOLDER : (GSUITE_FROM_HISTORY_TOOL_URL, GSUITE_FROM_HISTORY_TOOL_TITLE, GSUITE_FROM_HISTORY_TOOL_HOVER, True, False, False),
                        DEMO_TRACK_PLACEHOLDER : (DEMO_TRACK_URL, DEMO_TRACK_TITLE, DEMO_TRACK_HOVER, True, False, False),
                        OVERLAP_BETWEEN_TRACKS_PLACEHOLDER : (OVERLAP_BETWEEN_TRACKS_URL, OVERLAP_BETWEEN_TRACKS_TITLE, OVERLAP_BETWEEN_TRACKS_HOVER, True, True, False),
                        EXTRACT_FROM_ARCHIVE_PLACEHOLDER : (EXTRACT_FROM_ARCHIVE_URL, EXTRACT_FROM_ARCHIVE_TITLE, EXTRACT_FROM_ARCHIVE_HOVER, True, False, False),
                        SIMILARITY_AND_UNIQUENESS_PLACEHOLDER : (SIMILARITY_AND_UNIQUENESS_URL, SIMILARITY_AND_UNIQUENESS_TITLE, SIMILARITY_AND_UNIQUENESS_HOVER, True, True, False),
                        CONSTRUCT_GSUITE_PAGE_PLACEHOLDER : (CONSTRUCT_GSUITE_PAGE_URL, CONSTRUCT_GSUITE_PAGE_TITLE, CONSTRUCT_GSUITE_PAGE_HOVER, True, False, False),
                        GSUITE_FROM_REPOSITORY_TOOL_PLACEHOLDER : (GSUITE_FROM_REPOSITORY_TOOL_URL, GSUITE_FROM_REPOSITORY_TOOL_TITLE, GSUITE_FROM_REPOSITORY_TOOL_HOVER, True, False, False),
#                         DEMO_GWAS_BLUPRINT_TRACK_PLACEHOLDER : (DEMO_GWAS_BLUPRINT_TRACK_URL, DEMO_GWAS_BLUPRINT_TRACK_TITLE, DEMO_GWAS_BLUPRINT_TRACK_HOVER, True, False, False),
                        DEMO_TCGA_PRAD_TRACK_PLACEHOLDER : (DEMO_TCGA_PRAD_TRACK_URL, DEMO_TCGA_PRAD_TRACK_TITLE, DEMO_TCGA_PRAD_TRACK_HOVER, True, False, False),
                        DEMO_GSUITE_159_TF_GM12878_PLACEHOLDER : (DEMO_GSUITE_159_TF_GM12878_URL, DEMO_GSUITE_159_TF_GM12878_TITLE, DEMO_GSUITE_159_TF_GM12878_HOVER, True, False, False),
                        DEMO_GSUITE_CMYC_43_CELL_TYPES_PLACEHOLDER : (DEMO_GSUITE_CMYC_43_CELL_TYPES_URL, DEMO_GSUITE_CMYC_43_CELL_TYPES_TITLE, DEMO_GSUITE_CMYC_43_CELL_TYPES_HOVER, True, False, False),
                        DEMO_GSUITE_DNASE_40_CELL_TYPES_PLACEHOLDER : (DEMO_GSUITE_DNASE_40_CELL_TYPES_URL, DEMO_GSUITE_DNASE_40_CELL_TYPES_TITLE, DEMO_GSUITE_DNASE_40_CELL_TYPES_HOVER, True, False, False),
                        DEMO_GSUITE_HIST_K562_PLACEHOLDER : (DEMO_GSUITE_HIST_K562_URL, DEMO_GSUITE_HIST_K562_TITLE, DEMO_GSUITE_HIST_K562_HOVER, True, False, False),
                        DEMO_GSUITE_GWAS_PLACEHOLDER : (DEMO_GSUITE_GWAS_URL, DEMO_GSUITE_GWAS_TITLE, DEMO_GSUITE_GWAS_HOVER, True, False, False),
                        DEMO_TRACK_K562_ENHANCERS_PLACEHOLDER : (DEMO_TRACK_K562_ENHANCERS_URL, DEMO_TRACK_K562_ENHANCERS_TITLE, DEMO_TRACK_K562_ENHANCERS_HOVER, True, False, False),
                        CREATE_GTRACK_FROM_TABULAR_TOOL_PLACEHOLDER : (CREATE_GTRACK_FROM_TABULAR_TOOL_URL, CREATE_GTRACK_FROM_TABULAR_TOOL_TITLE, CREATE_GTRACK_FROM_TABULAR_TOOL_HOVER, True, False, False),
                        CLUS_TRACK_TOOL_PLACEHOLDER : (CLUS_TRACK_TOOL_URL, CLUS_TRACK_TOOL_TITLE, CLUS_TRACK_TOOL_HOVER, True, False, False),
                        DEMO_GSUITE_SOMATIC_COAD_PLACEHOLDER: (DEMO_GSUITE_SOMATIC_COAD_URL, DEMO_GSUITE_SOMATIC_COAD_TITLE, DEMO_GSUITE_SOMATIC_COAD_HOVER, True, False, False),
                        DEMO_GSUITE_SELECTED_TFBS_PLACEHOLDER: (DEMO_GSUITE_SELECTED_TFBS_URL, DEMO_GSUITE_SELECTED_TFBS_TITLE, DEMO_GSUITE_SELECTED_TFBS_HOVER, True, False, False),
                        DEMO_TRACK_MYC_BS_PLACEHOLDER: (DEMO_TRACK_MYC_BS_URL, DEMO_TRACK_MYC_BS_TITLE, DEMO_TRACK_MYC_BS_HOVER, True, False, False),
                        DEMO_GSUITE_TCGA_EXOME_PLACEHOLDER: (DEMO_GSUITE_TCGA_EXOME_URL, DEMO_GSUITE_TCGA_EXOME_TITLE, DEMO_GSUITE_TCGA_EXOME_HOVER, True, False, False),
                        FILE_FORMATS_PAGE_PLACEHOLDER: (FILE_FORMATS_PAGE_URL, FILE_FORMATS_PAGE_TITLE, FILE_FORMATS_HOVER, True, False, False),
                        DEMO_GSUITE_TFS_WITH_PWMS_PLACEHOLDER : (DEMO_GSUITE_TFS_WITH_PWMS_URL, DEMO_GSUITE_TFS_WITH_PWMS_TITLE, DEMO_GSUITE_TFS_WITH_PWMS_HOVER, True, False, False),
                        MATCH_TF_WITH_PWMS_TOOL_PLACEHOLDER : (MATCH_TF_WITH_PWMS_TOOL_URL, MATCH_TF_WITH_PWMS_TOOL_TITLE, MATCH_TF_WITH_PWMS_TOOL_HOVER, True, True, False),
                        EDIT_GSUITE_METADATA_TOOL_PLACEHOLDER : (EDIT_GSUITE_METADATA_TOOL_URL, EDIT_GSUITE_METADATA_TOOL_TITLE, EDIT_GSUITE_METADATA_TOOL_HOVER, True, False, False),
                        GSUITE_TRACKS_VS_GSUITE_TOOL_PLACEHOLDER : (GSUITE_TRACKS_VS_GSUITE_TOOL_URL, GSUITE_TRACKS_VS_GSUITE_TOOL_TITLE, GSUITE_TRACKS_VS_GSUITE_TOOL_HOVER, True, True, False),
                        DEMO_TRACK_LICA_CN_PLACEHOLDER : (DEMO_TRACK_LICA_CN_URL, DEMO_TRACK_LICA_CN_TITLE, DEMO_TRACK_LICA_CN_HOVER, True, False, False),
                        ALL_TARGETS_OF_TFS_TOOL_PLACEHOLDER : (ALL_TARGETS_OF_TFS_TOOL_URL, ALL_TFS_OF_REGION_TOOL_TITLE, ALL_TARGETS_OF_TFS_TOOL_HOVER, True, True, False),
                        ALL_TFS_OF_REGION_TOOL_PLACEHOLDER : (ALL_TFS_OF_REGION_TOOL_URL, ALL_TFS_OF_REGION_TOOL_TITLE, ALL_TFS_OF_REGION_TOOL_HOVER, True, True, False),
                        TF_BINDING_DISRUPTION_TOOL_PLACEHOLDER : (TF_BINDING_DISRUPTION_TOOL_URL, TF_BINDING_DISRUPTION_TOOL_TITLE, TF_BINDING_DISRUPTION_TOOL_HOVER, True, False, False)
                         }

    def __init__(self, fileName, prefixFn, postfixFn):
        self.categoryCount = 0
        self.questionCount = 0
        self.content = ''
        self.fileName = fileName

        #flags
        self._analysisStepsOpen = False;
        self._infoBoxOpen = False;
        self._analysisDescriptionOpen = False;
        self._subAnalysisStepOpen = False
        
        self.questionCatalog = OrderedDict()

        self.content += open(prefixFn).read()

        # Yes, it is a hack:
        self.content = self.content.replace('$LOAD_GSUITE_SINGLE_TRACK_SAMPLE_FILE_URL', self.LOAD_GSUITE_SINGLE_TRACK_SAMPLE_FILE_URL)

        self.generateContent()
        self.content += open(postfixFn).read()

    def closeDiv(self):
        self.content += '\n</div>'


    def parseQuestion(self, line):
        self.content += '''
            <div class="question" id="q%s" onclick="toggleDiv('#a%s', '#i%s');" onmouseover="this.style.background='#F8F0B1';this.style.border='1px solid #F8F0B1';"
            onmouseout="this.style.background='#FBDF6E';this.style.border='1px dotted #333333';">
            <img data-open='false' id="i%s" src="hyperbrowser/images/div/DNAlying.png" width="15" height="15" />
            %s
            </div>

        ''' % tuple([self.getCatPlusQuestion()]*4 + [line])

    def getCatPlusQuestion(self, separator=''):
        return separator.join([str(self.categoryCount), str(self.questionCount)])


    def _createLinkPlaceholder(self, val):
        lph = '<<EL|'

        href = val[0]

        paramSeparator = '&'
        if val[3]:
#             if '?' not in href:
#                 paramSeparator = '?'

            href += paramSeparator + 'basicQuestionId=' + str(self.categoryCount) + '_' + str(self.questionCount)

        if val[4]:
            href += paramSeparator + 'bmQid=' + str(self.categoryCount) + '_' + str(self.questionCount)

        lph += 'href===' + href

        if val[1] and val[1] != '':
            lph += '|title===' + val[1]

        if val[2] and val[2] != '':
            lph += '|hover===' + val[1]

        if val[5] and val[5] != '':
            lph += '|onclick===' + val[5]

        lph += '>>'

        return lph

    def updateLinks(self, answer):

        for key, val in WelcomePageGenerator.PLACEHOLDERS_DICT.iteritems():
            lnPlaceHolder = self._createLinkPlaceholder(val)
            answer = answer.replace(key, lnPlaceHolder)

        return answer

    def parseAnswer(self, answer):

        answer = self.updateLinks(answer)

        self.content += '''
        <div class="answer" id="a%s">
            %s
            </div>


        ''' % (self.getCatPlusQuestion(), answer)


    def startAnalysisDetails(self, line):
        self._analysisStepsOpen = True
        return '<div id="analysisDetails">\n<h3 class="welcomeAnalysisDetails">Analysis details</h3>\n'


    def closeAnalysisDetails(self):
        if self._analysisStepsOpen:
            self._analysisStepsOpen = False
            return '</div>'


    def startInfoBox(self, line):
        self._infoBoxOpen = True
        divId = 'infoBox' + str(self.categoryCount) + '_' + str(self.questionCount)
        toggleIB = '</br><img onclick="toggleInfoBox(\'#%s\')" data-open="false" id="img" + "_" + str(self.questionCount) + " src="june_2007_style/HB/info_small.png" width="15" height="15" />' % divId
        return '%s\n<div id="%s" class="infoBox">\n' % (toggleIB, divId)


    def closeInfoBox(self):
        self._infoBoxOpen = False;
        return '\n</div>'


    def startAnalysisSteps(self, line):
        self._analysisStepsOpen = True
        return '\n<div class="analysisSteps">\n<h3 class="welcomeAnalysisSteps">Analysis steps</h3>\n<ol>'


    def addAnalysisStep(self, line):
        if self._subAnalysisStepOpen:
                self._subAnalysisStepOpen = False
                return '\n</ol>\n<li>%s</li>' % line
        return '\n<li>%s</li>' % line


    def addAnalysisSubStep(self, line):
        ret = ''
        if not self._subAnalysisStepOpen:
            ret += '<ol type="a">'
            self._subAnalysisStepOpen = True
        ret += '<li>%s</li>' % line
        return ret


    def closeAnalysisSteps(self):
        ret = ''
        if self._subAnalysisStepOpen:
            self._subAnalysisStepOpen = False
            ret += '\n</ol>'
        self._analysisStepsOpen = False
        ret += '\n</ol>\n</div>'
        return ret


    def updateQuestionCatalog(self):
        pass
    
    
    def generateContent(self):
        answer = ''
        with open(self.fileName, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('-'):
                if answer is not '':
                    if self._analysisStepsOpen:
                        answer += self.closeAnalysisSteps()
                    self.parseAnswer(answer)
                    answer = ''
                self.categoryCount += 1
                if self.categoryCount > 1:
                    self.closeDiv()
                self.parseCategory(line)
                self.questionCount = 0
            elif line.startswith('\t-'):
                if answer is not '':
                    if self._analysisStepsOpen:
                        answer += self.closeAnalysisSteps()
                    self.parseAnswer(answer)
                    answer = ''
                self.questionCount+=1
#                 if self.questionCount > 1:
#                     self.closeDiv()
                self.parseQuestion(line)
                self.questionCatalog[self.getCatPlusQuestion(separator='_')] = line.strip()
            elif line.startswith('\t\t- Analysis details'):
                answer += self.startAnalysisDetails(line)
            elif line.startswith('\t\t- Info-box'):
                answer += self.closeAnalysisDetails()
                answer += self.startInfoBox(line)
            elif line.startswith('\t\t- Analysis steps'):
                answer += self.closeInfoBox()
                answer += self.startAnalysisSteps(line)
            elif line.startswith('\t\t\t-') and self._analysisStepsOpen:
                answer += self.addAnalysisStep(line)
            elif line.startswith('\t\t\t\t-') and self._analysisStepsOpen:
                answer += self.addAnalysisSubStep(line)
            elif line.startswith('\t\t'):
                answer+=line[2:]
            else:
                answer+='<br>' + line

    def parseCategory(self, line):
        self.content +=\
        '''
        <div class="question-wrapper" onclick="toggleDiv('#q%i', '#i%i');" onmouseover="this.style.background='#F8F0B1';this.style.border='1px solid #F8F0B1';"
            onmouseout="this.style.background='#FBDF6E';this.style.border='1px dotted #333333';">
            <p>
                <img data-open='false' id="i%i" src="hyperbrowser/images/div/DNAlying.png"
                width="20" height="20" />
                <span> %s </span>
             </p>

        </div>
        <div id='q%i' class="answer-wrapper">
        ''' % tuple([self.categoryCount]*3 +[line] + [self.categoryCount])

    def getBasicModeQuestionCatalogContent(self):
        content = '#This catalog is autogenerated by the WelcomePageBasic.py script\n'
        content += '#Please DO NOT update it manually. The questions are defined in wpcontent.txt'
        content += '\n\n'
        content += 'from collections import OrderedDict'
        content += '\n\n'
        content += 'Catalog = ' + str(self.questionCatalog)
        content += '\n\n'
        return content
    

if __name__ == '__main__':
    # import os, sys
    # os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

    import os

    path = os.path.dirname(__file__)
    wg = WelcomePageGenerator(path + '/wpcontent.txt',
                              path +'/wpprefix.html',
                              path + '/wppostfix.html')
    with open(GALAXY_BASE_DIR + '/static/welcome.html', 'w') as f:
#     with open('testWelcome.html', 'w') as f:
        f.write(LinkExpansion(wg.content).expandLinks())
    
    with open(HB_SOURCE_CODE_BASE_DIR +
              '/quick/toolguide/BasicModeQuestionCatalog.py', 'w') as f:
        f.write(wg.getBasicModeQuestionCatalogContent())
    # print LinkExpansion(wg.content).expandLinks()
        print 'OK: Finished generating welcome page'
