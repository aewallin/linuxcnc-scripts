import ttt                   # https://github.com/aewallin/truetype-tracer
import time

# get segments from ttt
def ttt2ngc(text,scale):
    wr = ttt.NGC_Writer()
    wr.arc   = False   # if False, approximate arcs with lines.
    wr.conic = False   # if False, approximate conic with arc/line 
    wr.cubic = False   # if False, approximate cubic with arc/line 
    
    wr.scale = float(1)/float(scale)
    # set the font
    wr.setFont(0) # FreeSerif
    #wr.setFont(1) # FreeSerifBold
    #wr.setFont(2) # FreeSerifItalic
    #wr.setFont(3) # FreeSerifBoldItalic
    #wr.setFont(4) # FreeMono
    #wr.setFont(5) # FreeMonoBold
    #wr.setFont(6) # FreeMonoBoldOblique
    #wr.setFont(7) # FreeMonoOblique
    #wr.setFont(8) # FreeSans
    #wr.setFont(9) # FreeSansBold
    #wr.setFont(10) # FreeSansBoldOblique
    #wr.setFont(11) # FreeSansOblique

    
    return ttt.ttt(text,wr)

if __name__ == "__main__":  
    print "( TTT++",ttt.version()," )"
    ngc = ttt2ngc(  "TTT++ LinuxCNC", 1000) # (text, scale) all coordinates are divided by scale
    print ngc

