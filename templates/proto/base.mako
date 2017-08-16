<%inherit file="/base.mako"/>

<%def name="title()">
    ${self.title()}
</%def>

<%def name="stylesheets()">
    ${h.css('base')}
    ${h.css('proto')}
</%def>

<%def name="javascripts()">
    ${h.js( "libs/jquery/jquery")}
    ${self.head()}
</%def>

<%def name="javascript_app()"></%def>

<%def name="head()"></%def>
<%def name="action()"></%def>
<%def name="toolHelp()"></%def>
<%def name="help(what)">
    <a href="#help_${what}" title="Help" onclick="getHelp('${what}')" class="help">?</a>
    <div id="help_${what}" class="infomessagesmall help">help</div>
</%def>

    
    <div id="__disabled"></div>
    <div class="toolForm">
    <div class="toolFormTitle">${self.title()}</div>
        <div class="toolFormBody">
            ${self.body()}
        </div>
    </div>
    <div class="toolHelp">
        <div class="toolHelpBody">
            ${self.toolHelp()}
        </div>
    </div>

