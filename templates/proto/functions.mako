<%!
import sys
from cgi import escape
from urllib import quote, unquote
import json
from string import lower

import proto.hyper_gui as gui
%>

<%def name="staticInfoBox(name, info)">
    %if info:
        <img class="showInfo" onclick="$('#infobox_${name}').toggle()" title="Information" alt="(i)" src="${h.url_for('/static/style/info_small.png')}">
        <div class="infomessage" id="infobox_${name}" style="display:none">${info}</div>
    %endif
</%def>

<%def name="select(name, opts, value, label = None, info = None)">
    <p><label>${label if label is not None else name}
    <select name="${name}" onchange="reloadForm(form, this)">
        %for o in range(len(opts)):
            <option value="${opts[o]}" ${'selected' if value == opts[o] else ''}>${opts[o]}</option>
        %endfor
    </select>
    </label>
    ${staticInfoBox(name, info)}
    </p>
</%def>

<%def name="history_select(control, name, opts, value, label = None, info = None)">
    <p><label>${label if label is not None else name}
    <select name="${name}" onchange="reloadForm(form, this)">
        ${opts[0]}
    </select>
    </label>
        ${staticInfoBox(name, info)}
    </p>
</%def>

<%def name="checkbox(name, opts, value, label = None, info = None)">
    <p id="${name}"><label><input onchange="reloadForm(form, this)" name="${name}" type="checkbox" value="True" ${'checked=checked' if value else ''}> ${label}</label>
    ${staticInfoBox(name, info)}
    </p>
</%def>


<%def name="multihistory(name, opts, values, label = None, info = None)">
    ${multichoice(name, opts, values, label, info, history=True)}
</%def>


<%def name="multichoice(name, opts, values, label = None, info = None, history = False)">
    <fieldset><legend>${label}</legend>
        <a href="javascript:;" id="${name}_check" onclick="$('input.${name}').attr('checked','checked');reloadForm(null, this);">Check all</a>
        <a href="javascript:;" id="${name}_uncheck" onclick="$('input.${name}').removeAttr('checked');reloadForm(null, this)">Uncheck all</a><br/>
        %for key,value in opts.items():            
            <label><input onchange="updateMultiChoice(this, '${name}', '${key}', ${history|lower});reloadForm(form, this)" class="${name}" id="${name + '|' + key}" name="${name + '|' + key}" type="checkbox" value="${value if history else 'True'}" ${'checked=checked' if values and values[key] else 'checked=checked' if value and not values else ''}> ${unquote(value.split(':')[3]) if history else key}</label><br/>
        %endfor
        <input type="hidden" name="${name}" id="${name}" value="${escape(json.dumps(values), True)}">
    </fieldset>
</%def>


<%def name="rawStr(name, value = '', label = None)">
    <div>${value}</div>
</%def>

<%def name="text(name, value = '', label = None, rows = 5, readonly = False, reload = False, info = None)">
    <div style="margin: 1em 0px"><label>${label if label is not None else name} ${'<br>' if label else ''}
        %if rows > 1:
            <textarea ${"onchange=\"reloadForm(form, this)\"" if reload else ''} rows="${rows}" name="${name}" id="${name}" wrap="off"
                style="max-width:100%;width:100%;overflow:auto;" ${"readonly=\"readonly\"" if readonly else ""}>${value}</textarea>
        %else:
            <input type="text" ${"onchange=\"reloadForm(form, this)\"" if reload else ''} name="${name}" id="${name}"
                style="max-width:100%;width:100%;overflow:auto;" ${"readonly=\"readonly\"" if readonly else ""} value="${value}">
        %endif
    </label>
    ${staticInfoBox(name, info)}
    </div>
</%def>

<!-- <textarea ${"" if not value else "onchange=\"reloadForm(form, this)\""} rows="${rows}" name="${name}" id="${name}" wrap="off" -->

<%def name="password(name, value='', label=None, reload=False, info = None)">
    <p><label>${label if label is not None else name} ${'<br>' if label else ''}
        <input type="password" name="${name}" value="${value}" autocomplete="off" style="max-width:100%;width:100%" ${"onchange=\"reloadForm(form, this)\"" if reload else ''}>
    </label></p>
</%def>


<%def name="help(what, text)">
    <div style="text-align:right">
            <a href="#help_${what}" title="Help" onclick="getHelp('${what}')">${text}</a>
    </div>
    <div id="help_${what}" class="infomessagesmall help">help</div>
</%def>


<%def name="genomeChooser(control, genomeElement = None, genome = None, id='dbkey')">
    <%
    if genomeElement == None:
        genomeElement = control.getGenomeElement(id)
    if genome == None:
        genome = control.getGenome()

    if id != 'dbkey':
        genomeElement.onChange = '$("#dbkey").val($(this).val());' + genomeElement.onChange
    %>

    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}
    %if id != 'dbkey':
        <input type="hidden" id="dbkey" name="dbkey" value="${genome}">
    %endif

    ${self.genomeInfo(control.params, genome)}

</%def>


<%def name="genomeInfo(params, genome)" />


<%def name="accessDenied()">
    <div class="warningmessage">This functionality is only available to specific users. <br>Contact us if you need access.</div>
</%def>

