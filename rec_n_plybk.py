from time import sleep, time
from collections import namedtuple
import mido
import matplotlib.pyplot as plt
import pickle

# print mido.get_input_names()
# print mido.get_output_names()

#dev='MPK mini play'
dev="Roland Digital Piano"

Note=" "*21+"DdE"+"CcDdEFfGgAaB"*8

try:
    inport = mido.open_input(dev+' 0')
except:
    inport.close()
    inport = mido.open_input(dev+' 0')

try:    
    outport = mido.open_output(dev+' 1')
except:
    outport.close()
    outport = mido.open_output(dev+' 1')
    
Midi_Event = namedtuple("Midi_Event", "time event")
        
rec=[]
rec2=[]
volume=127
msg = mido.Message('sysex', data=[0x7F, 0x7F, 0x04, 0x01, 0, volume])
outport.send(msg) 

def playback(rec):
  for n,r in enumerate(rec):
    if n==len(rec):
        break
    if r.time<2:
        sleep(r.time)
    e = r.event
    
    if e.type=='note_on':
        print " "*(e.note-20)+Note[e.note]
    
    outport.send(e)
    for msg in inport.iter_pending():
        if msg.type=="note_on" and msg.note==21:
            print "stop!"
            return    

def plot_playback(rec):
  v=[]
  t=[]
  te=0
  
  for n,r in enumerate(rec):
    if n==len(rec):
        break
    
    if r.time<2:
        sleep(r.time)
    
    e = r.event
    
    te = te + r.time*1000
    
    #print "{}: {}".format(te, e)

    outport.send(r.event)
    
    if e.type=='note_on':
        t.append(te)
        v.append(e.velocity)
        
        if len(v)>20:
            plt.cla()   
            plt.plot(t[-20:], v[-20:], 'x')
        else:
            plt.plot(t, v, 'x')
        plt.pause(0.0001)
    
    for msg in inport.iter_pending():
        if msg.type=="note_on" and msg.note==21:
            print "stop!"
            return  
    
                
def save(rec, filename):
    fd = open(filename, 'w')
    pickle.dump(rec, fd)
    fd.close()

def load(filename):
    fd = open(filename, 'r')
    return pickle.load(fd)
    
try:
    t0=time()
    while True:
        for msg in inport.iter_pending():
            t1 = time()
            rec.append( Midi_Event(t1-t0, msg) )
            t0 = time()
            
            if msg.type=="note_on":
                print "{:.3f}: note={}".format((t1-t0)*1000, msg.note)
                if msg.note==21:
                    rec=[]
                    print "restart!"
                if msg.note==108:
                    for msg in inport.iter_pending(): # flush
                        t1 = time()
                        rec.append((t1-t0, msg))
                        t0 = time()
                    sleep(0.25)
                    print "playback...",
                    if len(rec):
                        rec2=rec
                        save(rec, 'save.ply')
                    playback(rec)    
                    rec=[]
                    print "done!"
                elif msg.note==107:
                    print "replay...",
                    playback(rec2)
                    print "done!"
                elif msg.note==106:
                    print "replay...",
                    plot_playback(rec2)
                    print "done!"
                     
                    
            elif msg.type=="control_change" and msg.control==64:
                print "{:.3f}:         pedal={}".format((t1-t0)*1000, msg.value)
                
except KeyboardInterrupt:
    pass

inport.close()
outport.close()
