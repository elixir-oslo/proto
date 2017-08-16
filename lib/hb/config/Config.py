# from config.LocalOSConfig import *

from config.DebugConfig import DebugConfig, DebugModes
from proto.config.Config import (config, URL_PREFIX, RESTRICTED_USERS,
                                 GALAXY_BASE_DIR, OUTPUT_PRECISION, PROTO_TOOL_DIR)

#
# Version information
#

HB_VERSION = 'v2.0b4'


#
# Functionality settings
#

IS_EXPERIMENTAL_INSTALLATION = config.getWithDefault('is_experimental_installation', False, 'hyperbrowser')
USE_MEMORY_MEMOIZATION = config.getWithDefault('use_memory_memoization', True, 'hyperbrowser')
LOAD_DISK_MEMOIZATION = config.getWithDefault('load_disk_memoization', False, 'hyperbrowser')
STORE_DISK_MEMOIZATION = config.getWithDefault('store_disk_memoization', False, 'hyperbrowser')
PRINT_PROGRESS = config.getWithDefault('print_progress', True, 'hyperbrowser')
ALLOW_COMP_BIN_SPLITTING = config.getWithDefault('allow_comp_bin_splitting', False, 'hyperbrowser')
ALLOW_GSUITE_FILE_PROTOCOL = config.getWithDefault('allow_gsuite_file_protocol', False, 'hyperbrowser')
USE_PARALLEL = config.getWithDefault('use_parallel', False, 'hyperbrowser')

#
# Debugging
#

DEBUG_MODE = config.getWithDefault('debug_mode', 'NO_DEBUG', 'hyperbrowser').upper()
try:
    DebugConfig.changeMode(getattr(DebugModes, DEBUG_MODE))
except AttributeError:
    pass

#
# Optimization and limits
#

COMP_BIN_SIZE = config.getWithDefault('comp_bin_size', 100000, 'hyperbrowser')
MEMMAP_BIN_SIZE = config.getWithDefault('memmap_bin_size', 1024 * 1024, 'hyperbrowser')
MAX_NUM_USER_BINS = config.getWithDefault('max_num_user_bins', 330000, 'hyperbrowser')
MAX_LOCAL_RESULTS_IN_TABLE = config.getWithDefault('max_local_results_in_table', 100000, 'hyperbrowser')
MAX_CONCAT_LEN_FOR_OVERLAPPING_ELS = \
    config.getWithDefault('max_concat_len_for_overlapping_els', 20, 'hyperbrowser')


#
# Relative paths from standard Galaxy config
#

GALAXY_REL_FILE_PATH = config.getWithDefault('file_path', 'database/files')
GALAXY_REL_NEW_FILE_PATH = config.getWithDefault('new_file_path', 'database/tmp')
GALAXY_REL_TOOL_CONFIG_FILE = config.getWithDefault('tool_config_file', 'config/tool_conf.xml')
GALAXY_REL_TOOL_PATH = config.getWithDefault('tool_path', 'tools')
GALAXY_REL_TOOL_DATA_PATH = config.getWithDefault('tool_data_path', 'tool-data')
GALAXY_REL_DATATYPES_CONFIG_FILE = config.getWithDefault('datatypes_config_file', 'config/datatypes_conf.xml')
GALAXY_REL_JOB_WORKING_DIR = config.getWithDefault('job_working_directory', 'database/job_working_directory')
GALAXY_TMP_DIR = config.getWithDefault('new_file_path','database/tmp')


#
# External absolute paths (not used in the default setup)
#

EXT_NONSTANDARD_DATA_PATH = config.getWithDefault('ext_nonstandard_data_path', '', 'hyperbrowser')
EXT_ORIG_DATA_PATH = config.getWithDefault('ext_orig_data_path', '', 'hyperbrowser')
EXT_PARSING_ERROR_DATA_PATH = config.getWithDefault('ext_parsing_error_data_path', '', 'hyperbrowser')
EXT_PROCESSED_DATA_PATH = config.getWithDefault('ext_processed_data_path', '', 'hyperbrowser')
EXT_MEMOIZED_DATA_PATH = config.getWithDefault('ext_memoized_data_path', '', 'hyperbrowser')
EXT_DATA_FILES_PATH = config.getWithDefault('ext_data_files_path', '', 'hyperbrowser')
EXT_UPLOAD_FILES_PATH = config.getWithDefault('ext_upload_files_path', '', 'hyperbrowser')
EXT_STATIC_FILES_PATH = config.getWithDefault('ext_static_files_path', '', 'hyperbrowser')
EXT_TOOL_DATA_PATH = config.getWithDefault('ext_tool_data_path', '', 'hyperbrowser')
EXT_NMER_CHAIN_DATA_PATH = config.getWithDefault('ext_nmer_chain_data_path', '', 'hyperbrowser')
EXT_MAPS_PATH = config.getWithDefault('ext_maps_path', '', 'hyperbrowser')
EXT_LOG_PATH = config.getWithDefault('ext_log_path', '', 'hyperbrowser')
EXT_RESULTS_PATH = config.getWithDefault('ext_results_path', '', 'hyperbrowser')
EXT_TMP_PATH = config.getWithDefault('ext_tmp_path', '', 'hyperbrowser')



#
# Parallelization and cluster offload setup
#

CLUSTER_ACCOUNTNAME = config.getWithDefault('cluster_accountname', 'user', 'hyperbrowser')
CLUSTER_TEMP_PATH = config.getWithDefault('cluster_temp_path', '/tmp', 'hyperbrowser')
CLUSTER_SOURCE_CODE_DIRECTORY = config.getWithDefault('cluster_source_code_directory', '/src', 'hyperbrowser')
ONLY_USE_ENTIRE_CLUSTER_NODES = config.getWithDefault('only_use_entire_cluster_nodes', False, 'hyperbrowser')
CLUSTER_CORES_PER_NODE = config.getWithDefault('cluster_cores_per_node', 1, 'hyperbrowser')
SBATCH_PATH = config.getWithDefault('sbatch_path', '/bin/sbatch', 'hyperbrowser')
CLUSTER_MEMORY_PER_CORE_IN_MB = config.getWithDefault('cluster_memory_per_core_in_mb', 2048, 'hyperbrowser')
DEFAULT_WALLCLOCK_LIMIT_IN_SECONDS = config.getWithDefault('default_wallclock_limit_in_seconds', 3600, 'hyperbrowser')
DEFAULT_NUMBER_OF_REMOTE_WORKERS = config.getWithDefault('default_number_of_remote_workers', 8, 'hyperbrowser')

PP_NUMBER_OF_LOCAL_WORKERS = config.getWithDefault('pp_number_of_local_workers', 2, 'hyperbrowser')
PP_PASSPHRASE = config.getWithDefault('pp_passphrase', 'USING THE DEFAULT IS NOT SECURE!', 'hyperbrowser')
PP_PORT = config.getWithDefault('pp_port', 8180, 'hyperbrowser')
PP_MANAGER_PORT = config.getWithDefault('pp_manager_port', 8190, 'hyperbrowser')


#
# Dependent constants
#

GALAXY_FILE_PATH = GALAXY_BASE_DIR + '/' + GALAXY_REL_FILE_PATH
GALAXY_NEW_FILE_PATH = GALAXY_BASE_DIR + '/' + GALAXY_REL_NEW_FILE_PATH
GALAXY_TOOL_CONFIG_FILE = GALAXY_BASE_DIR + '/' + GALAXY_REL_TOOL_CONFIG_FILE
GALAXY_TOOL_PATH = GALAXY_BASE_DIR + '/' + GALAXY_REL_TOOL_PATH
GALAXY_TOOL_DATA_PATH = GALAXY_BASE_DIR + '/' + GALAXY_REL_TOOL_DATA_PATH
GALAXY_DATATYPES_CONFIG_FILE = GALAXY_BASE_DIR + '/' + GALAXY_REL_DATATYPES_CONFIG_FILE
GALAXY_JOB_WORKING_DIR = GALAXY_BASE_DIR + '/' + GALAXY_REL_JOB_WORKING_DIR

GALAXY_COMPILED_TEMPLATES = GALAXY_BASE_DIR + '/database/compiled_templates'
GALAXY_TEMPLATES_PATH = GALAXY_BASE_DIR + '/templates'
GALAXY_LIB_PATH = GALAXY_BASE_DIR + '/lib'

STATIC_DIR = '/static/hyperbrowser'
STATIC_REL_PATH = URL_PREFIX + STATIC_DIR
STATIC_PATH = GALAXY_BASE_DIR + STATIC_DIR

HB_SOURCE_CODE_BASE_DIR = GALAXY_BASE_DIR + '/lib/hb'
HB_SOURCE_DATA_BASE_DIR = HB_SOURCE_CODE_BASE_DIR + '/data'

HB_DATA_BASE_DIR = GALAXY_BASE_DIR + '/hyperbrowser'
TRACKS_BASE_DIR = HB_DATA_BASE_DIR + '/tracks'
NONSTANDARD_DATA_PATH = TRACKS_BASE_DIR + '/collectedTracks'
ORIG_DATA_PATH = TRACKS_BASE_DIR + '/standardizedTracks'
PARSING_ERROR_DATA_PATH = TRACKS_BASE_DIR + '/parsingErrorTracks'
PROCESSED_DATA_PATH = TRACKS_BASE_DIR + '/preProcessedTracks'
NMER_CHAIN_DATA_PATH = TRACKS_BASE_DIR + '/nmerChains'
DATA_FILES_PATH = HB_DATA_BASE_DIR + '/data'
UPLOAD_FILES_PATH = HB_DATA_BASE_DIR + '/upload'
LOG_PATH = HB_DATA_BASE_DIR + '/logs'
SRC_PATH = HB_DATA_BASE_DIR + '/src'

RESULTS_PATH = HB_DATA_BASE_DIR + '/results'
RESULTS_FILES_PATH = RESULTS_PATH + '/files'
RESULTS_JOB_WORKING_DIR = RESULTS_PATH + '/job_working_directory'
MEMOIZED_DATA_PATH = RESULTS_PATH + '/memoizedData'
RESULTS_STATIC_PATH = RESULTS_PATH + '/static'
MAPS_PATH = RESULTS_STATIC_PATH + '/maps'
MAPS_COMMON_PATH = MAPS_PATH + '/common'
MAPS_TEMPLATE_PATH = GALAXY_TEMPLATES_PATH + '/hyperbrowser/gmap'

PROTO_HB_TOOL_DIR = PROTO_TOOL_DIR + '/hyperbrowser'

#
# To be removed
#

DEFAULT_GENOME = 'hg18'
STOREBIOINFO_USER = 'hs'
STOREBIOINFO_PASSWD = 'ssh123'
