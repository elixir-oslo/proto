<%!
#import proto.hyperbrowser.hyper_gui as gui
%>
<%namespace name="hbfunctions" file="functions.mako" />

<%inherit file="/proto/generictool.mako" />

<%def name="stylesheets()">
    ${h.css('base')}
    ${h.css('proto')}
    ${h.css('hb_base')}
</%def>

<%def name="includeScripts()">\
    <script type="text/javascript">
        <%include file="common.js"/>
        <%include file="../proto/common.js"/>
    </script>
</%def>

<%def name="showOptionsBox(control, params, i)">
    %if control.inputTypes[i] == '__track__':
        ${hbfunctions.trackChooser(control.trackElements[control.inputIds[i]], i, params, False)}
    %elif control.inputTypes[i] == '__genome__':
        ${hbfunctions.genomeChooser(control, control.options[i], control.inputValues[i], control.inputIds[i])}
    %else:
        ${parent.showOptionsBox(control, params, i)}
    %endif
</%def>

<%def name="extraGuiContent(control)">
    %if control.prototype.isBatchTool() and control.getBatchLine() and control.isValid() and control.userIsOneOfUs():
    <p class="infomessage" onclick="$('#batchline').toggle()">
        <a href="#batchline" title="Click to show/hide">Corresponding batch command line:</a>
        <span id="batchline" style="display:none"><br>
        ${control.getBatchLine()}
        </span>
    </p>
##     <br/>
##
##     <p class="infomessage" onclick="$('#testform').toggle()">
##         <a href="#testform" title="Click to show/hide">Add run to test sd repository:</a>
##         <!--<button id="testsubmit" type="button" style="display:none" >Click Me!</button>-->
##         <form id="testform" style="display:none">
##         set test name: <input type="text" name="testname"><br>
##         <input type="submit" name="testsubmit" value="Add test">
##         </form>
##     </p>
##     <script type="text/javascript">
##         $( "#testform" ).bind( "submit", function( event ) {
##         //$( "#testsubmit" ).click(function() {
##         //var c = $("[name='add_test']:checked").val();
##         if(1)
##         	 {var datastring = $("form").serialize();
##             var lastChar = datastring.indexOf('&testname=');
##             var b = datastring.slice (0,lastChar).replace(/&/g,"\n").replace(/=/g, ":");
##             var c = '&box2='+ $("[name='testname']").val();
##             var testData = "old_values=%7B%7D&datatype=html&mako=generictool&tool_id=hb_add_test_tool&tool_name=hb_add_test_tool&URL=http://dummy&start=Execute&box1=" + b + c
##
##             $.post("/dev2/tool_runner",  testData);
##             alert('Added test to test-repository..');
##             event.preventDefault();
##             }});
##     </script>
    %endif
</%def>

${parent.body()}
