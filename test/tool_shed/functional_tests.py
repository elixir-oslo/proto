#!/usr/bin/env python
"""Test driver for tool shed functional tests.

Launch this script by running ``run_tests.sh -t`` from GALAXY_ROOT.
"""
from __future__ import absolute_import

import os
import string
import sys
import tempfile

galaxy_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
# Need to remove this directory from sys.path
sys.path[0:1] = [ os.path.join( galaxy_root, "lib" ), os.path.join( galaxy_root, "test" ) ]

from base import driver_util
driver_util.configure_environment()
log = driver_util.build_logger()
tool_shed_test_tmp_dir = driver_util.setup_tool_shed_tmp_dir()

# This is for the tool shed application.
from galaxy.webapps.tool_shed import buildapp as toolshedbuildapp
from galaxy.web import buildapp as galaxybuildapp


tool_sheds_conf_xml_template = '''<?xml version="1.0"?>
<tool_sheds>
    <tool_shed name="Galaxy main tool shed" url="http://toolshed.g2.bx.psu.edu/"/>
    <tool_shed name="Galaxy test tool shed" url="http://testtoolshed.g2.bx.psu.edu/"/>
    <tool_shed name="Embedded tool shed for functional tests" url="http://${shed_url}:${shed_port}/"/>
</tool_sheds>
'''

shed_tool_conf_xml_template = '''<?xml version="1.0"?>
<toolbox tool_path="${shed_tool_path}">
</toolbox>
'''

tool_data_table_conf_xml_template = '''<?xml version="1.0"?>
<tables>
</tables>
'''

shed_data_manager_conf_xml_template = '''<?xml version="1.0"?>
<data_managers>
</data_managers>
'''


def main():
    """Entry point for test driver script."""
    # ---- Configuration ------------------------------------------------------
    if not os.path.isdir( tool_shed_test_tmp_dir ):
        os.mkdir( tool_shed_test_tmp_dir )
    shed_db_path = driver_util.database_files_path(tool_shed_test_tmp_dir, prefix="TOOL_SHED")
    shed_tool_data_table_conf_file = os.environ.get( 'TOOL_SHED_TEST_TOOL_DATA_TABLE_CONF', os.path.join( tool_shed_test_tmp_dir, 'shed_tool_data_table_conf.xml' ) )
    galaxy_shed_data_manager_conf_file = os.environ.get( 'GALAXY_SHED_DATA_MANAGER_CONF', os.path.join( tool_shed_test_tmp_dir, 'test_shed_data_manager_conf.xml' ) )
    galaxy_tool_data_table_conf_file = os.environ.get( 'GALAXY_TEST_TOOL_DATA_TABLE_CONF', os.path.join( tool_shed_test_tmp_dir, 'tool_data_table_conf.xml' ) )
    galaxy_tool_conf_file = os.environ.get( 'GALAXY_TEST_TOOL_CONF', driver_util.FRAMEWORK_UPLOAD_TOOL_CONF )
    galaxy_shed_tool_conf_file = os.environ.get( 'GALAXY_TEST_SHED_TOOL_CONF', os.path.join( tool_shed_test_tmp_dir, 'test_shed_tool_conf.xml' ) )
    galaxy_migrated_tool_conf_file = os.environ.get( 'GALAXY_TEST_MIGRATED_TOOL_CONF', os.path.join( tool_shed_test_tmp_dir, 'test_migrated_tool_conf.xml' ) )
    galaxy_tool_sheds_conf_file = os.environ.get( 'GALAXY_TEST_TOOL_SHEDS_CONF', os.path.join( tool_shed_test_tmp_dir, 'test_sheds_conf.xml' ) )
    if 'GALAXY_TEST_TOOL_DATA_PATH' in os.environ:
        tool_data_path = os.environ.get( 'GALAXY_TEST_TOOL_DATA_PATH' )
    else:
        tool_data_path = tempfile.mkdtemp( dir=tool_shed_test_tmp_dir )
        os.environ[ 'GALAXY_TEST_TOOL_DATA_PATH' ] = tool_data_path
    galaxy_db_path = driver_util.database_files_path(tool_shed_test_tmp_dir)
    shed_file_path = os.path.join( shed_db_path, 'files' )
    hgweb_config_file_path = tempfile.mkdtemp( dir=tool_shed_test_tmp_dir )
    new_repos_path = tempfile.mkdtemp( dir=tool_shed_test_tmp_dir )
    galaxy_shed_tool_path = tempfile.mkdtemp( dir=tool_shed_test_tmp_dir )
    galaxy_migrated_tool_path = tempfile.mkdtemp( dir=tool_shed_test_tmp_dir )
    hgweb_config_dir = hgweb_config_file_path
    os.environ[ 'TEST_HG_WEB_CONFIG_DIR' ] = hgweb_config_dir
    print "Directory location for hgweb.config:", hgweb_config_dir
    toolshed_database_conf = driver_util.database_conf(shed_db_path, prefix="TOOL_SHED")
    kwargs = dict( admin_users='test@bx.psu.edu',
                   allow_user_creation=True,
                   allow_user_deletion=True,
                   datatype_converters_config_file='datatype_converters_conf.xml.sample',
                   file_path=shed_file_path,
                   hgweb_config_dir=hgweb_config_dir,
                   job_queue_workers=5,
                   id_secret='changethisinproductiontoo',
                   log_destination="stdout",
                   new_file_path=new_repos_path,
                   running_functional_tests=True,
                   shed_tool_data_table_config=shed_tool_data_table_conf_file,
                   smtp_server='smtp.dummy.string.tld',
                   email_from='functional@localhost',
                   template_path='templates',
                   tool_parse_help=False,
                   tool_data_table_config_path=galaxy_tool_data_table_conf_file,
                   use_heartbeat=False )
    kwargs.update(toolshed_database_conf)
    # Generate the tool_data_table_conf.xml file.
    file( galaxy_tool_data_table_conf_file, 'w' ).write( tool_data_table_conf_xml_template )
    # Generate the shed_tool_data_table_conf.xml file.
    file( shed_tool_data_table_conf_file, 'w' ).write( tool_data_table_conf_xml_template )
    os.environ[ 'TOOL_SHED_TEST_TOOL_DATA_TABLE_CONF' ] = shed_tool_data_table_conf_file
    # ---- Build Tool Shed Application --------------------------------------------------
    toolshedapp = driver_util.build_shed_app(kwargs)

    # ---- Run tool shed webserver ------------------------------------------------------
    # TODO: Needed for hg middleware ('lib/galaxy/webapps/tool_shed/framework/middleware/hg.py')
    kwargs['global_conf']['database_connection'] = kwargs["database_connection"]
    tool_shed_server_wrapper = driver_util.launch_server(
        toolshedapp,
        toolshedbuildapp.app_factory,
        kwargs,
        prefix="TOOL_SHED",
    )
    tool_shed_test_host = tool_shed_server_wrapper.host
    tool_shed_test_port = tool_shed_server_wrapper.port
    log.info( "Functional tests will be run against %s:%s" % ( tool_shed_test_host, tool_shed_test_port ) )

    # ---- Optionally start up a Galaxy instance ------------------------------------------------------
    if 'TOOL_SHED_TEST_OMIT_GALAXY' not in os.environ:
        # Generate the shed_tool_conf.xml file.
        tool_sheds_conf_template_parser = string.Template( tool_sheds_conf_xml_template )
        tool_sheds_conf_xml = tool_sheds_conf_template_parser.safe_substitute( shed_url=tool_shed_test_host, shed_port=tool_shed_test_port )
        file( galaxy_tool_sheds_conf_file, 'w' ).write( tool_sheds_conf_xml )
        # Generate the tool_sheds_conf.xml file.
        shed_tool_conf_template_parser = string.Template( shed_tool_conf_xml_template )
        shed_tool_conf_xml = shed_tool_conf_template_parser.safe_substitute( shed_tool_path=galaxy_shed_tool_path )
        file( galaxy_shed_tool_conf_file, 'w' ).write( shed_tool_conf_xml )
        # Generate the migrated_tool_conf.xml file.
        migrated_tool_conf_xml = shed_tool_conf_template_parser.safe_substitute( shed_tool_path=galaxy_migrated_tool_path )
        file( galaxy_migrated_tool_conf_file, 'w' ).write( migrated_tool_conf_xml )
        os.environ[ 'GALAXY_TEST_SHED_TOOL_CONF' ] = galaxy_shed_tool_conf_file
        # Generate shed_data_manager_conf.xml
        if not os.environ.get( 'GALAXY_SHED_DATA_MANAGER_CONF' ):
            open( galaxy_shed_data_manager_conf_file, 'wb' ).write( shed_data_manager_conf_xml_template )
        kwargs = dict( enable_tool_shed_check=True,
                       hours_between_check=0.001,
                       migrated_tools_config=galaxy_migrated_tool_conf_file,
                       shed_data_manager_config_file=galaxy_shed_data_manager_conf_file,
                       shed_tool_data_table_config=shed_tool_data_table_conf_file,
                       shed_tool_path=galaxy_shed_tool_path,
                       tool_data_path=tool_data_path,
                       tool_config_file=[ galaxy_tool_conf_file, galaxy_shed_tool_conf_file ],
                       tool_sheds_config_file=galaxy_tool_sheds_conf_file,
                       tool_data_table_config_path=galaxy_tool_data_table_conf_file )
        kwargs.update(driver_util.setup_galaxy_config(galaxy_db_path, use_test_file_dir=False, default_install_db_merged=False))
        print "Galaxy database connection:", kwargs["database_connection"]

        # ---- Run galaxy webserver ------------------------------------------------------
        galaxyapp = driver_util.build_galaxy_app(kwargs)
        galaxy_server_wrapper = driver_util.launch_server(
            galaxyapp,
            galaxybuildapp.app_factory,
            kwargs,
        )
        log.info("Galaxy tests will be run against %s:%s" % (galaxy_server_wrapper.host, galaxy_server_wrapper.port))

    # ---- Find tests ---------------------------------------------------------
    success = False
    try:
        success = driver_util.nose_config_and_run()
    except:
        log.exception( "Failure running tests" )

    log.info( "Shutting down" )
    # ---- Tear down -----------------------------------------------------------
    tool_shed_server_wrapper.stop()
    tool_shed_server_wrapper = None
    if galaxy_server_wrapper is not None:
        galaxy_server_wrapper.stop()
        galaxy_server_wrapper = None
    driver_util.cleanup_directory(tool_shed_test_tmp_dir)
    if success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit( main() )
