<%!
import sys, os, traceback, json, pickle
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui

%>
<%
params = control.params

if control.prototype.isRedirectTool() or not control.prototype.isHistoryTool() or control.hasNextPage():
    formAction = '?'
else:
    formAction = h.url_for('/tool_runner')

%>
<%namespace name="functions" file="functions.mako" />
<%inherit file="base.mako" />
<%def name="title()">${control.prototype.getToolName()}</%def>
<%def name="head()">
    %if control.doRedirect():
        <meta http-equiv="Refresh" content="0; url=${control.getRedirectURL()}" />
    %endif
    <script type="text/javascript">
        <%include file="common.js"/>
    </script>
    ${h.js('sorttable')}
</%def>

%if control.userHasFullAccess():

    <form method="post" action="${formAction}">

    <INPUT TYPE="HIDDEN" NAME="old_values" VALUE="${quote(json.dumps(control.oldValues))}">
    <INPUT TYPE="HIDDEN" NAME="choices_stack" VALUE="${quote(pickle.dumps(control.choicesStack))}">
    <INPUT TYPE="HIDDEN" NAME="datatype" VALUE="${control.prototype.getOutputFormat(control.choices)}">
    <INPUT TYPE="HIDDEN" NAME="mako" VALUE="multigenerictool">
    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="${control.toolId}">
    <INPUT TYPE="HIDDEN" NAME="tool_name" VALUE="${control.toolId}">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

    %if len(control.subClasses) > 0:
        ${functions.select('sub_class_id', control.subClasses.keys(), control.subClassId, 'Select subtool:')}
    %endif

    %for i in control.inputOrder:
        %if control.inputTypes[i] == 'select':
            ${functions.select(control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i])}
        %elif control.inputTypes[i] == 'multi':
            ${functions.multichoice(control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i])}
        %elif control.inputTypes[i] == 'checkbox':
            ${functions.checkbox(control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i])}
        %elif control.inputTypes[i] == 'text':
            ${functions.text(control.inputIds[i], control.displayValues[i], control.inputNames[i], control.options[i][1], readonly=False, reload=control.prototype.isDynamic())}
        %elif control.inputTypes[i] == 'text_readonly':
            ${functions.text(control.inputIds[i], control.displayValues[i], control.inputNames[i], control.options[i][1], readonly=True)}
        %elif control.inputTypes[i] == '__password__':
            ${functions.password(control.inputIds[i], control.displayValues[i], control.inputNames[i], reload=control.prototype.isDynamic())}
        %elif control.inputTypes[i] == '__genome__':
            ${functions.genomeChooser(control)}
        %elif control.inputTypes[i] == '__track__':        
            ${functions.trackChooser(control.trackElements[control.inputIds[i]], i, params, False)}
        %elif control.inputTypes[i] == '__history__':
            ${functions.history_select(control, control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i])}
        %elif control.inputTypes[i] == '__toolhistory__':
            ${functions.history_select(control, control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i])}
        %elif control.inputTypes[i] == '__multihistory__':
            ${functions.multihistory(control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i])}
        %elif control.inputTypes[i] == '__hidden__':
            <input type="hidden" name="${control.inputIds[i]}" value="${control.displayValues[i]}">
        %elif control.inputTypes[i] == 'table':
            ${control.displayValues[i]}
        %endif
    %endfor
    
    <p>
        %if control.hasPrevPage():
            <input id="previous" type="submit" name="previous" value="Previous" onclick="reloadForm(form, this)">
        %endif
        %if control.hasNextPage():
            <input id="next" type="submit" name="next" value="Next" ${'disabled' if not control.isValid() else ''}>
        %else:
            <input id="start" type="submit" name="start" value="Execute" ${'disabled' if not control.isValid() else ''}>
        %endif
    </p>

    </form>

    %if control.hasErrorMessage():
        <div class="errormessage">${control.errorMessage}</div>
    %endif

    %if control.params.get('start') and not control.prototype.isHistoryTool() and control.isValid():
        <p class="infomessage">${control.executeNoHistory()}</p>
    %endif


    %if control.prototype.isBatchTool() and control.isValid() and control.userIsOneOfUs():
    <p class="infomessage" onclick="$('#batchline').toggle()">
        <a href="#batchline" title="Click to show/hide">Corresponding batch command line:</a>
        <span id="batchline" style="display:none"><br>
        ${control.getBatchLine()}
        </span>
    </p>
    %endif

%else:
    ${functions.accessDenied()}
%endif

<%def name="toolHelp()">
    %if control.hasDemoURL():
        <button onclick="location.href='${control.getDemoURL()}'">Fill out demo selections</button>
        <hr>
    %endif

    ${control.prototype.getToolDescription()}

    %if control.getIllustrationImage():
        %if os.path.exists(control.getIllustrationImage().getDiskPath()):
            <p><hr><img width="100%" style="max-width: 640px; width: expression(this.width > 640 ? 640: true);" src="${control.getIllustrationImage().getURL()}"></p>
        %elif control.isDebugging():
            <p class="warningmessage">No imagefile exists at: ${control.getIllustrationImage().getDiskPath()}</p>
        %endif
    %endif

    %if control.hasFullExampleURL():
        %if control.prototype.getToolDescription() not in [None, '']:
            <hr>
        %endif
        <b>Example</b>
        <p><a href="${control.getFullExampleURL()}" target=_top>See full example</a> of how to use this tool.</p>
    %endif
</%def>

${repr(control.choicesStack)}
