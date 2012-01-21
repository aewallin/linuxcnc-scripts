import ttt                   # https://github.com/aewallin/truetype-tracer
import time

# get segments from ttt
def ttt2ngc(text,scale):
    wr = ttt.NGC_Writer()
    wr.arc   = False   # if False, approximate arcs with lines.
    wr.conic = False   # if False, approximate conic with arc/line 
    wr.cubic = False   # if False, approximate cubic with arc/line 
    
    wr.scale = float(1)/float(scale)
    return ttt.ttt(text,wr)

if __name__ == "__main__":  
    print "( TTT++",ttt.version()," )"
    ngc = ttt2ngc(  "TTT++ EMC2", 1000) # (text, scale) all coordinates are divided by scale
    print ngc

