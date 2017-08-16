<%!
import traceback
#from cgi import escape
#from urllib import quote, unquote
%>
<%
error = ''
try:
    control.action()
except:
    error = traceback.format_exc()

%>
<html>
    <body>
        
%if error != '':
    ${error}
%else:
    ${control.getInfoText()}
%endif

    </body>
</html>
