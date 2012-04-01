import openvoronoi as ovd    # https://github.com/aewallin/openvoronoi
import ttt                   # https://github.com/aewallin/truetype-tracer
import time
import ngc_writer            # https://github.com/aewallin/linuxcnc-scripts

ngc_writer.clearance_height=10
ngc_writer.feed_height = 2
ngc_writer.feed = 200
ngc_writer.plunge_feed = 100

scale = 140

def printMedial(vd):
    maw = ovd.MedialAxisWalk(  vd.getGraph() )
    toolpath = maw.walk()
    for chain in toolpath:
        n = 0
        for move in chain:
            for point in move:
                if n==0: # don't draw anything on the first iteration
                    p = point[0]
                    z = point[1]
                    ngc_writer.pen_up();
                    ngc_writer.xy_rapid_to( scale*p.x, scale*p.y );
                    ngc_writer.pen_down()
                    ngc_writer.plunge( -z ) # now we are at the correct height, at the startpoint of the first move
                else:
                    p = point[0]
                    z = point[1]
                    ngc_writer.line_to( scale*p.x, scale*p.y, scale*(-z) )
                n=n+1
    return

# this function inserts point-sites into vd
def insert_polygon_points(vd, polygon):
    pts=[]
    for p in polygon:
        pts.append( ovd.Point( p[0], p[1] ) )
    id_list = []
    #print "inserting ",len(pts)," point-sites:"
    m=0
    for p in pts:
        id_list.append( vd.addVertexSite( p ) )
        #print " ",m," added vertex ", id_list[ len(id_list) -1 ]
        m=m+1    
    return id_list

# this function inserts line-segments into vd
def insert_polygon_segments(vd,id_list):
    j=0
    #print "inserting ",len(id_list)," line-segments:"
    for n in range(len(id_list)):
        n_nxt = n+1
        if n==(len(id_list)-1):
            n_nxt=0
        #print " ",j,"inserting segement ",id_list[n]," - ",id_list[n_nxt]
        vd.addLineSite( id_list[n], id_list[n_nxt])
        j=j+1

# this function takes all segments from ttt and inserts them into vd
def insert_many_polygons(vd,segs):
    polygon_ids =[]
    t_before = time.time()
    for poly in segs:
        poly_id = insert_polygon_points(vd,poly)
        polygon_ids.append(poly_id)
    t_after = time.time()
    pt_time = t_after-t_before
    
    t_before = time.time()
    for ids in polygon_ids:
        insert_polygon_segments(vd,ids)
    
    t_after = time.time()
    seg_time = t_after-t_before
    
    return [pt_time, seg_time]

# this translates segments from ttt
def translate(segs,x,y):
    out = []
    for seg in segs:
        seg2 = []
        for p in seg:
            p2 = []
            p2.append(p[0] + x)
            p2.append(p[1] + y)
            seg2.append(p2)
        out.append(seg2)
    return out
    
# modify by deleting last point (since it is identical to the first point)
def modify_segments(segs):
    segs_mod =[]
    for seg in segs:
        first = seg[0]
        last = seg[ len(seg)-1 ]
        assert( first[0]==last[0] and first[1]==last[1] )
        seg.pop()
        seg.reverse() # to get interior or exterior offsets. Try commenting out this and see what happens.
        segs_mod.append(seg)
    return segs_mod

# get segments from ttt
def ttt_segments(text,scale):
    wr = ttt.SEG_Writer()
    wr.arc = False   # approximate arcs with lines
    wr.conic = False # approximate conic with arc/line
    wr.cubic = False # approximate cubic with arc/line
    wr.conic_biarc_subdivision = 10 # this has no effect?
    wr.conic_line_subdivision = 50 # =10 increasesn nr of points to 366, = 5 gives 729 pts
    wr.cubic_biarc_subdivision = 10 # no effect?
    wr.cubic_line_subdivision = 10 # no effect?
    wr.scale = float(1)/float(scale)
    
    wr.setFont(3)
    # 0  freeserif
    # 1  freeserif bold
    # 2  freeserif italic
    # 3  freeserif bold italic
    # 4  "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf" );
    # 5  "/usr/share/fonts/truetype/freefont/FreeMonoBoldOblique.ttf" ); 
    # 6  "/usr/share/fonts/truetype/freefont/FreeMonoOblique.ttf" )
    # 7  "/usr/share/fonts/truetype/freefont/FreeSans.ttf" );
    # 8  "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" );
    # 9  "/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf" );
    # 10 "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf" );
    
    
    ttt.ttt(text,wr) 
    segs = wr.get_segments()
    return segs
    
if __name__ == "__main__":  
    vd = ovd.VoronoiDiagram(1,120) # parameters: (r,bins)  
    # float r  = radius within which all geometry is located. it is best to use 1 (unit-circle) for now.
    # int bins = number of bins for grid-search (affects performance, should not affect correctness)
    

    
    # get segments from ttt. NOTE: must set scale so all geometry fits within unit-circle!
    segs = ttt_segments(  "LinuxCNC", 20000) # (text, scale) all coordinates are divided by scale
    segs = translate(segs, -0.06, 0.05)
    segs = modify_segments(segs)
    
    times = insert_many_polygons(vd,segs) # insert segments into vd
    print "( ttt2medial.py - experimental v-carving script )"
    print "( TTT++",ttt.version(),"                      )"
    print "( OpenVoronoi",ovd.version(),"                )"
    print "( VD built in %02.3f seconds                     )" % ( sum(times))
    print "( VD check: ", vd.check(), "                              )"
    
    pi = ovd.PolygonInterior( True ) # filter so that only polygon interior remains
    vd.filter_graph(pi)
    ma = ovd.MedialAxis() # filter so that only medial axis remains
    vd.filter_graph(ma)
    
    ngc_writer.preamble()
    printMedial( vd )
    ngc_writer.postamble()
