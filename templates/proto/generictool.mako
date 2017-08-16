<%!
import sys, os, traceback, json
from zlib import compress
from base64 import urlsafe_b64encode
from cgi import escape
from urllib import quote, unquote

import proto.hyper_gui as gui

%>
<%
params = control.params

if control.isRedirectTool() or not control.prototype.isHistoryTool():
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
    ${self.includeScripts()}
    ${h.js('proto/sorttable')}
</%def>

<%def name="includeScripts()">\
    <script type="text/javascript">
        <%include file="common.js"/>
    </script>
</%def>

<%def name="showOptionsBox(control, params, i)">
        %if control.inputTypes[i] == 'select':
            ${functions.select(control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == 'multi':
            ${functions.multichoice(control.inputIds[i], control.options[i], control.inputValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == 'checkbox':
            ${functions.checkbox(control.inputIds[i], control.options[i], control.inputValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == 'text':
            ${functions.text(control.inputIds[i], control.displayValues[i], control.inputNames[i], control.options[i][1], readonly=False, reload=control.prototype.isDynamic(), info=control.inputInfo[i])}
        %elif control.inputTypes[i] == 'text_readonly':
            ${functions.text(control.inputIds[i], control.displayValues[i], control.inputNames[i], control.options[i][1], readonly=True)}
        %elif control.inputTypes[i] == 'rawStr':
            ${functions.rawStr(control.inputIds[i], control.displayValues[i], control.inputNames[i])}
        %elif control.inputTypes[i] == '__password__':
            ${functions.password(control.inputIds[i], control.displayValues[i], control.inputNames[i], reload=control.prototype.isDynamic(), info=control.inputInfo[i])}
        %elif control.inputTypes[i] == '__genome__':
            ${functions.genomeChooser(control, control.options[i], control.inputValues[i], control.inputIds[i])}
        %elif control.inputTypes[i] == '__history__':
            ${functions.history_select(control, control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == '__toolhistory__':
            ${functions.history_select(control, control.inputIds[i], control.options[i], control.displayValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == '__multihistory__':
            ${functions.multihistory(control.inputIds[i], control.options[i], control.inputValues[i], control.inputNames[i], info=control.inputInfo[i])}
        %elif control.inputTypes[i] == '__hidden__':
            <input type="hidden" name="${control.inputIds[i]}" id="${control.inputIds[i]}" value="${escape(control.displayValues[i], True)}">
        %elif control.inputTypes[i] == 'table':
            ${control.displayValues[i]}
        %endif
</%def>

%if control.userHasFullAccess():

    <form method="post" action="${formAction}">

    <INPUT TYPE="HIDDEN" NAME="cached_options" VALUE="${control.encodeCache(control.cachedOptions)}">
    <INPUT TYPE="HIDDEN" NAME="cached_params" VALUE="${control.encodeCache(control.cachedParams)}">
    <INPUT TYPE="HIDDEN" NAME="cached_extra" VALUE="${control.encodeCache(control.cachedExtra)}">
    <INPUT TYPE="HIDDEN" NAME="old_values" VALUE="${quote(json.dumps(control.oldValues))}">
    <INPUT TYPE="HIDDEN" NAME="datatype" VALUE="${control.prototype.getOutputFormat(control.choices)}">
    <INPUT TYPE="HIDDEN" NAME="job_name" VALUE="${control.prototype.getOutputName(control.choices)}">
    <INPUT TYPE="HIDDEN" NAME="mako" VALUE="generictool">
    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="${control.toolId}">
    <INPUT TYPE="HIDDEN" NAME="tool_name" VALUE="${control.toolId}">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">
    <INPUT TYPE="HIDDEN" NAME="extra_output" VALUE="${quote(json.dumps(control.extra_output))}">

    %if len(control.subClasses) > 0:
        ${functions.select('sub_class_id', control.subClasses.keys(), control.subClassId, control.subToolSelectionTitle)}
    %endif

    %for i in control.inputOrder:
        %if i in control.inputGroup[0]:
            %for label in control.inputGroup[0][i]:
                <fieldset><legend>${label}</legend>
            %endfor
        %endif

        ${self.showOptionsBox(control, params, i)}

        %if i in control.inputGroup[1]:
            %for j in range(0, control.inputGroup[1].count(i)):
                </fieldset>
            %endfor
        %endif

    %endfor
    
    <p><input id="start" type="submit" name="start" value="Execute" ${'disabled' if not control.isValid() else ''}></p>

    </form>

    %if control.hasErrorMessage():
        <div class="errormessage">${control.errorMessage}</div>
    %endif

    %if control.params.get('start') and not control.prototype.isHistoryTool() and control.isValid():
        <div class="infomessage">${control.executeNoHistory()}</div>
    %endif

    ${self.extraGuiContent(control)}

%else:
    ${functions.accessDenied()}
%endif

<%def name="extraGuiContent(control)"/>

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

