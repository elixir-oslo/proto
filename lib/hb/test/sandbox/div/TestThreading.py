from threading import Thread

#def imp():
    #import rpy

for i in range(10):
    t = Thread(target=imp)
    t.start()
    
