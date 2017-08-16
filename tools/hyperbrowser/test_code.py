from galaxy import datatypes
import os,urllib

# save the tool form parameters in the output file for the job script
def exec_before_job(app, inp_data, out_data, param_dict, tool=None):
    for name, data in out_data.items():
        data.dbkey = param_dict.get('dbkey', '?')
        ext = param_dict.get('datatype')
        if ext:
            data = app.datatypes_registry.change_datatype(data, ext)

        job_name = param_dict.get('job_name')
        if job_name:
            if data.name == tool.name:
                data.name = urllib.unquote(job_name)
#        job_info = param_dict.get('job_info')
#        if job_info:
#            data.info = urllib.unquote(job_info)

        out = open(data.file_name, 'w')
        #print >> out, "tool_id\t" + tool
        print >> out, "file_path\t" + os.path.abspath(os.getcwd() + "/" + app.config.file_path)
        for key, value in param_dict.items():
            value = urllib.quote(value)
            print >> out, "%s\t%s" % (key,value)
        out.close()

        out_data[name] = data


def exec_after_process(app, inp_data, out_data, param_dict, tool, stdout, stderr):
#    job_name = param_dict.get('job_name')
    job_info = param_dict.get('job_info')
    if job_info:
        for name, data in out_data.items():
#            data.name = job_name
            data.info = urllib.unquote(job_info)
#            out_data[name] = data
#    
        app.model.context.flush()
