import sys, os, getopt,types

from gold.application.GalaxyInterface import *

os.environ['DISPLAY'] = ':9.0'

def main():
    #print "running"
    input = sys.argv[1]
    output = sys.argv[2]
    genome = sys.argv[3]
    sys.stdout = open(output, "w", 0)
    # galaxy separates the lines by XX
    lines = input.split("XX")
    try:
        print '''<script type="text/javascript" src="/static/scripts/jquery.js"></script>
            <script type="text/javascript">
                var done = false;
                var job = { filename: "%s", pid: %d };

                var dead = document.cookie.indexOf("dead=" + job.pid) >= 0 ? true : false;
                                        
                function check_job() {
                    if (!done) {
                        if (!dead) {
                            $.getJSON("/hyper/check_job", job, function (status) {
                                    if (status.running) {
                                        location.reload(true);
                                    } else {
                                        document.cookie = "dead=" + job.pid;
                                        location.reload(true);
                                    }
                                }
                            );
                        } else {
                            alert("This job did not finish successfully: " + job.filename);
                        }
                    }
                }
                
                setTimeout("if (!done) check_job();", 2000);
            </script>
        ''' % (output, os.getpid())

        GalaxyInterface.runBatchLines(lines, output, genome)

    finally:
        print '<script type="text/javascript">done = true;</script>'
    
if __name__ == "__main__":
    main()
