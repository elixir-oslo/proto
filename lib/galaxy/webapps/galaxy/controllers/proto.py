from __future__ import absolute_import

import logging
import os
import pkgutil
import traceback

from multiprocessing import Process, Pipe, Queue
from importlib import import_module

from galaxy.web.base.controller import web, error, BaseUIController


log = logging.getLogger( __name__ )

#from sqlalchemy import create_engine, event, exc
#from sqlalchemy.orm.session import Session, sessionmaker
#from sqlalchemy.orm.scoping import scoped_session



class ProtoController( BaseUIController ):

    def run_fork(self, response, trans, mako):
        # this can close active connections in parent threads, since db server endpoint closes
        #trans.sa_session.get_bind().dispose()

        # don't know why this has no effect
        #engine = create_engine(trans.app.config.database_connection, pool_size=1)
        #trans.app.model.context = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=True))

        # logging locks and/or atexit handlers may be cause of deadlocks in a fork from thread
        # attempt to fix by shutting down and reloading logging module and clear exit handlers
        # logging.shutdown()
        # import atexit
        # for handler in atexit._exithandlers:
        #    print repr(handler)
        #    try:
        #        handler[0]()
        #    except Exception, e:
        #        print e
        #
        # atexit._exithandlers = []
        # reload(logging)
        # log.warning('fork log test')
        
        exc_info = None
        html = ''
        #response.send_bytes('ping')

        try:
            html = self.run_tool(mako, trans)
        except Exception, e:
            html = '<html><body><pre>\n'
            html += str(e) + ':\n' + traceback.format_exc()
            html += '\n</pre></body></html>'

        response.send_bytes(html)
        response.close()

        #trans.sa_session.flush()
        #engine.dispose()

    @staticmethod
    def _convert_mako_from_rel_to_abs(mako):
        return '/proto/' + mako

    @staticmethod
    def _get_controller_module_name(rel_mako):
        return 'proto.' + rel_mako

    def _parse_mako_filename(self, mako):
        if not mako.startswith('/'):
            rel_mako = mako
            mako = self._convert_mako_from_rel_to_abs(mako)
        else:
            rel_mako = mako.split('/')[-1]

        controller_module_name = self._get_controller_module_name(rel_mako)
        template_mako = mako + '.mako'
        return controller_module_name, template_mako

    @staticmethod
    def _fill_mako_template(template_mako, tool_controller, trans):
        return trans.fill_template(template_mako, trans=trans, control=tool_controller)

    def run_tool(self, mako, trans):
        controller_module_name, template_mako = self._parse_mako_filename(mako)

        controller_loader = pkgutil.find_loader(controller_module_name)
        if controller_loader:
            tool_module = import_module(controller_module_name)
            tool_controller = tool_module.getController(trans)
        else:
            tool_controller = None

        html = self._fill_mako_template(template_mako, tool_controller, trans)

        return html

    @web.expose
    def index(self, trans, mako='generictool', **kwd):
        return self._index(trans, mako, **kwd)

    def _index(self, trans, mako, **kwd):

        if kwd.has_key('rerun_hda_id'):
            self._import_job_params(trans, kwd['rerun_hda_id'])
                    
        if isinstance(mako, list):
            mako = mako[0]

        timeout = 60
        retry = 3
        while retry > 0:
            retry -= 1

            my_end, your_end = Pipe()
            proc = Process(target=self.run_fork, args=(your_end,trans,str(mako)))

            #trans.sa_session.flush()

            # this avoids database exceptions in fork, but defies the point of having a
            # connection pool
            #trans.sa_session.get_bind().dispose()

            # attempt to fully load history/dataset objects to avoid "lazy" loading from
            # database in forked process
            if trans.get_history():
                for hda in trans.get_history().active_datasets:
                    _ = hda.visible, hda.state, hda.dbkey, hda.extension, hda.datatype

            proc.start()
            html = ''
            if proc.is_alive():
                if my_end.poll(timeout):
                    #ping = my_end.recv_bytes()
                    html = my_end.recv_bytes()
                    my_end.close()
                    break
                else:
                    log.warn('Fork timed out after %d sec. Retrying...' % (timeout,))
            else:
                log.warn('Fork died on startup.')
                break

            proc.join(1)
            if proc.is_alive():
                proc.terminate()
                log.warn('Fork did not exit, terminated.')

        return html


    @web.json
    def json(self, trans, module = None, **kwd):
        response = Queue()
        proc = Process(target=self.__json, args=(response,trans,module,kwd))
        proc.start()
        dict = response.get(True, 120)
        proc.join(30)
        if proc.is_alive():
            proc.terminate()
            print 'json fork did not join; terminated.'
        response = None
        return dict

    @web.json
    def check_job(self, trans, pid = None, filename = None):
        # Avoid caching
        trans.response.headers['Pragma'] = 'no-cache'
        trans.response.headers['Expires'] = '0'
        rval = {'running': True}
        try:
            os.kill(int(pid), 0)
        except OSError:
            rval['running'] = False
        
        return rval


    def _import_job_params(self, trans, id=None):
        """
        Copied from ToolController.rerun()
        Given a HistoryDatasetAssociation id, find the job and that created
        the dataset, extract the parameters.
        """
        if not id:
            error( "'id' parameter is required" );
        try:
            id = int( id )
        except:
            error( "Invalid value for 'id' parameter" )
        # Get the dataset object
        data = trans.sa_session.query( trans.app.model.HistoryDatasetAssociation ).get( id )
        #only allow rerunning if user is allowed access to the dataset.
        if not trans.app.security_agent.can_access_dataset( trans.get_current_user_roles(), data.dataset ):
            error( "You are not allowed to access this dataset" )
        # Get the associated job, if any. If this hda was copied from another,
        # we need to find the job that created the origial hda
        job_hda = data
        while job_hda.copied_from_history_dataset_association:#should this check library datasets as well?
            job_hda = job_hda.copied_from_history_dataset_association
        if not job_hda.creating_job_associations:
            error( "Could not find the job for this dataset" )
        # Get the job object
        job = None
        for assoc in job_hda.creating_job_associations:
            job = assoc.job
            break   
        if not job:
            raise Exception("Failed to get job information for dataset hid %d" % data.hid)
        ## Get the job's parameters
        try:
            trans.request.rerun_job_params = job.get_param_values( trans.app, ignore_errors = True )
            trans.request.rerun_job_params['tool_id'] = job.tool_id
        except:
            raise Exception( "Failed to get parameters for dataset id %d " % data.id )
