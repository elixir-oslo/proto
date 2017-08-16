<%!
import sys
from cgi import escape
from urllib import quote, unquote
import galaxy.tools.actions.upload as upload

import proto.hyperbrowser.hyper_gui as gui

class Tool:
    id = 'hb_define_test'
    inputs = {}

%>
<%
#reload(gui)

galaxy = gui.GalaxyWrapper(trans)

params = galaxy.params

genomes = hyper.getAllGenomes(galaxy.getUserName())
genome = params.get('dbkey', genomes[0][1])
genomeElement = gui.SelectElement('dbkey', genomes, genome)

tool_id = params.get('tool_id', 'hb_define_test')

url_paste_box = params.get('url_paste_box', '')
# = params.get('')
#  = params.get('')
#   = params.get('')
   
formAction = ''

tool = Tool()

if params.get('start') != None:
    action = upload.UploadToolAction()
    action.execute(tool, trans, params)

%>
<%namespace name="functions" file="functions.mako" />

<%inherit file="base.mako"/>

<%def name="title()">Define statistical test</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
        
        function validate(form) {
            return true;
        }
    </script>
      <script type="text/javascript">
        // NB: uses jQuery
        $('form').bind('submit', function (ev) {
          var code = $(this.url_paste_box).val();
          var f1 = '#format1: ' + $('#_format_1').val() + '\n';
          var f2 = '#format2: ' + $('#_format_2').val() + '\n';
          var mc = $('#_monte_carlo').attr('checked') ? '#Use in Monte Carlo\n' : '';
          $(this.url_paste).val(f1 + f2 + mc + code);
          //alert($(this.url_paste).val());
          return true;
        });
      </script>

</%def>

<form method="post" action="${formAction}" onsubmit="return validate(this)">

%if hyper.userHasFullAccess(galaxy.getUserName()):    

<p>
    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}    
</p>

      <div class="form-row">
        <label>Define R function</label>
        <code>customFunc &lt;- function(track1, track2) {<br /> 
          result = 0;<br /></code>
      
      <textarea cols="80" rows="20" name="url_paste_box">${url_paste_box}</textarea>
      <br />
      <code>return (result)<br />
      }</code>
      </div>

      <div class="form-row">
      <b>Format of track 1:</b>
      <select id="_format_1">
        <option value=""> - Select format - </option>
        <option>Points</option>
        <option>Segments</option>
        <option>Valued points</option>
        <option>Valued segments</option>
        <option>Function</option>
      </select>
      </div>
      <div class="form-row">
      <b>Format of track 2:</b>
      <select id="_format_2">
        <option value=""> - Select format - </option>
        <option>Points</option>
        <option>Segments</option>
        <option>Valued points</option>
        <option>Valued segments</option>
        <option>Function</option>
      </select>
      </div>
      <div class="form-row">
      <b>Embed in Monte Carlo simulation:</b> <input type="checkbox" id="_monte_carlo" value="#Use in Monte Carlo" />
      </div>
      <div class="form-row"><input name="file_data" type="file" size="30" label="File"/> </div>

    <input type="hidden" name="url_paste" value="" />
    <input type="hidden" name="file_type" value="R" />

    <p><input id="start" type="submit" name="start" value="Execute"></p>
%else:
        <p>You must be one of us to use tool</p>

%endif


    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="${tool_id}">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>
