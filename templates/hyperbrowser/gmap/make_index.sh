#!/bin/sh

echo "<html><body>" >index.html; 
for d in *; do if [ $d != "common" -a $d != "index.html" ]; then 
  echo "<a href=\"$d\">$d</a><br>" >>index.html; 
fi done; 
echo "</body></html>" >>index.html
