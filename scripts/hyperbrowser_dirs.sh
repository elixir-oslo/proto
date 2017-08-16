#!/usr/bin/env bash

#
# This script handles all HyperBrowser specific directory and symlinks
#

# Move to "script/" directory and other setup

curdir=$("pwd")

cd "$(dirname "$0")"/..
echo $("pwd")

set -e

if [ -z "$GALAXY_CONFIG_FILE" ]; then
    echo "GALAXY_CONFIG_FILE is not set. Exiting."
    exit 1
fi

#
# Convenience functions
#

function link_dir {
    source=$(python scripts/hyperbrowser_config.py -c $1)
    target=$(python scripts/hyperbrowser_config.py -c $2)

#    echo $1 $source
#    echo $2 $target

    if [ ! -z "$source" ] && [ ! -z "$target" ]
    then
        if [ ! -d $4$target ]
        then
            echo "Creating symlink: $4$target -> $3$source"
            ln -sfT $3$source $4$target
        fi
    else
        echo "Error: Empty input variables to function link_dir"
        exit 1
    fi
}

function create_dir_if_not_exists {
    source=$(python scripts/hyperbrowser_config.py -c $1)
#    echo $1 $source

    if [ ! -z "$source" ]
    then
        if [ ! -d "$source" ]
        then
            echo "Creating directory: $source"
            mkdir -p "$source"
        fi
    fi
}

function rename_to_old_if_not_empty {
    target=$(python scripts/hyperbrowser_config.py -c $1)
#    echo $1 $target

    if [ ! -z "$target" ]
    then
        if [ -d "$target" ] && [ ! -L "$target" ]
        then
            if [ ! -z "$(ls -A $target)" ]
            then
                echo "Renaming: $target => $target.old"
                mv -T "$target" "$target.old"
            else
                echo "Removing empty directory: $target"
                rmdir "$target"
            fi
        fi
    fi
}

function rename_from_old_if_exists {
    target=$(python scripts/hyperbrowser_config.py -c $1)
#    echo $1 $target

    if [ ! -z "$target" ]
    then
        if [ -d "$target.old" ] && [ ! -L "$target.old" ]
        then
            echo "Renaming: $target.old => $target"
            mv -T "$target.old" "$target"
        fi
    fi
}

function remove_link_if_exists {
    target=$(python scripts/hyperbrowser_config.py -c $1)
#    echo $1 $target

    if [ ! -z "$target" ]
    then
        if [ -h $target ]
        then
            echo "Removing: $target"
            rm $target
        fi
    fi
}

function create_rename_old_and_link {
    source=$(python scripts/hyperbrowser_config.py -c $1)
#    echo $1 $source

    if [ ! -z "$source" ]
    then
        create_dir_if_not_exists "$1"
        remove_link_if_exists "$2"
        rename_to_old_if_not_empty "$2"
        link_dir "$1" "$2"
    else
        remove_link_if_exists "$2"
        rename_from_old_if_exists "$2"
        create_dir_if_not_exists "$2"
    fi
}

#
# Store config in shelve file for speed
#

$(python scripts/hyperbrowser_config.py -r)
$(python scripts/hyperbrowser_config.py -s)

#
# Handle external HyperBrowser data directories
#

create_rename_old_and_link 'EXT_NONSTANDARD_DATA_PATH'      'NONSTANDARD_DATA_PATH'
create_rename_old_and_link 'EXT_ORIG_DATA_PATH'             'ORIG_DATA_PATH'
create_rename_old_and_link 'EXT_PROCESSED_DATA_PATH'        'PROCESSED_DATA_PATH'
create_rename_old_and_link 'EXT_PARSING_ERROR_DATA_PATH'    'PARSING_ERROR_DATA_PATH'
create_rename_old_and_link 'EXT_NMER_CHAIN_DATA_PATH'       'NMER_CHAIN_DATA_PATH'
create_rename_old_and_link 'EXT_DATA_FILES_PATH'            'DATA_FILES_PATH'
create_rename_old_and_link 'EXT_UPLOAD_FILES_PATH'          'UPLOAD_FILES_PATH'
create_rename_old_and_link 'EXT_LOG_PATH'                   'LOG_PATH'
create_rename_old_and_link 'EXT_TMP_PATH'                   'GALAXY_NEW_FILE_PATH'
create_rename_old_and_link 'EXT_TOOL_DATA_PATH'             'GALAXY_TOOL_DATA_PATH'

#
# Create HyperBrowser results directory, either externally, or via internal links
#

create_rename_old_and_link 'EXT_RESULTS_PATH'               'RESULTS_PATH'

remove_link_if_exists     'GALAXY_FILE_PATH'
remove_link_if_exists     'GALAXY_JOB_WORKING_DIR'

if [ -z $(python scripts/hyperbrowser_config.py -c 'EXT_RESULTS_PATH') ]
then
    link_dir 'GALAXY_REL_FILE_PATH' 'RESULTS_FILES_PATH' ../../
    link_dir 'GALAXY_REL_JOB_WORKING_DIR' 'RESULTS_JOB_WORKING_DIR' ../../
else
    create_rename_old_and_link 'RESULTS_FILES_PATH'         'GALAXY_FILE_PATH'
    create_rename_old_and_link 'RESULTS_JOB_WORKING_DIR'    'GALAXY_JOB_WORKING_DIR'
fi

#
# For subdirs of RESULTS_PATH, which must thus be created first
#

create_dir_if_not_exists   'RESULTS_STATIC_PATH'
create_rename_old_and_link 'EXT_MEMOIZED_DATA_PATH'         'MEMOIZED_DATA_PATH'
create_rename_old_and_link 'EXT_MAPS_PATH'                  'MAPS_PATH'
link_dir                   'MAPS_TEMPLATE_PATH'             'MAPS_COMMON_PATH'


#
# Remove shelve file
#

$(python scripts/hyperbrowser_config.py -r)

# Move back to original dir

cd $curdir
