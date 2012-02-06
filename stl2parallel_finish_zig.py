import ocl
import pyocl
import camvtk
import time
#import vtk
#import datetime       
import math
import os 
import Tkinter,tkFileDialog

import ngc_writer


ngc_writer.clearance_height= 4
ngc_writer.feed_height = 0.3
ngc_writer.feed = 200
ngc_writer.plunge_feed = 100
ngc_writer.metric = False

def printCLPoints(cl_filtered_paths):
    ngc_writer.preamble()
    
    for path in cl_filtered_paths:
        ngc_writer.pen_up()
        first_pt = path[0]
        ngc_writer.xy_rapid_to( first_pt.x, first_pt.y )
        ngc_writer.pen_down( first_pt.z )
        for p in path[1:]:
            ngc_writer.line_to(p.x,p.y,p.z)

    ngc_writer.postamble()

def filter_path(path,tol):
    f = ocl.LineCLFilter()
    f.setTolerance(tol)
    for p in path:
        p2 = ocl.CLPoint(p.x,p.y,p.z)
        f.addCLPoint(p2)
    f.run()
    return  f.getCLPoints()

def adaptive_path_drop_cutter(s, cutter, path):
    apdc = ocl.AdaptivePathDropCutter()
    apdc.setSTL(s)
    apdc.setCutter(cutter)
    # set the minimum Z-coordinate, or "floor" for drop-cutter
    #apdc.minimumZ = -1 
    apdc.setSampling(0.04)
    apdc.setMinSampling(0.0008)
    apdc.setPath( path )
    apdc.run()
    return apdc.getCLPoints()
    
if __name__ == "__main__": 
    root = Tkinter.Tk()
    filename = tkFileDialog.askopenfilename(title='Choose an STL file')
    #filename = "data/gnu_tux_mod.stl"
    
    print "( OpenCAMLib ",ocl.version()," )"
    #print os.getcwd()
    #filename="gnu_tux_mod.stl"
    #exit()
    stl = camvtk.STLSurf(filename)
    
    polydata = stl.src.GetOutput()
    s = ocl.STLSurf()
    camvtk.vtkPolyData2OCLSTL(polydata, s)
    print "( STL surface: read ", s.size(), "triangles from ",filename," )"
    
    angle = math.pi/4
    diameter=0.25
    length=5
    
    # choose a cutter for the operation:
    #cutter = ocl.BallCutter(diameter, length)
    cutter = ocl.CylCutter(diameter, length)
    #cutter = ocl.BullCutter(diameter, 0.2, length)
    #cutter = ocl.ConeCutter(diameter, angle, length)
    #cutter = cutter.offsetCutter( 0.4 )
    

    #print "( Cutter: ",cutter, " )"  # LinuxCNC does not allow nested comments!

 
    ymin=0
    ymax=12
    Ny=40  # number of lines in the y-direction
    dy = float(ymax-ymin)/(Ny-1)  # the y step-over
    
    # create a simple "Zig" pattern where we cut only in one direction.
    paths = []
    # create a list of paths
    for n in xrange(0,Ny):
        path = ocl.Path() 
        y = ymin+n*dy           # current y-coordinate
        p1 = ocl.Point(0,y,0)   # start-point of line
        p2 = ocl.Point(10,y,0)   # end-point of line
        l = ocl.Line(p1,p2)     # line-object
        path.append( l )        # add the line to the path
        paths.append(path)
    
    cl_paths=[]
    
    # we now have a list of paths to run through apdc
    t_before = time.time()
    n_aclp=0
    for p in paths:
        aclp = adaptive_path_drop_cutter(s,cutter,p) # the output is a list of Cutter-Locations
        n_aclp = n_aclp + len(aclp)
        cl_paths.append(aclp)
    
    t_after = time.time()
    print "( OpenCamLib::AdaptivePathDropCutter run took %.2f s )" % ( t_after-t_before )
    print "( got %d raw CL-points )" % ( n_aclp )
    
    
    # to reduce the G-code size we filter here. (this is not strictly required and could be omitted)
    # we could potentially detect G2/G3 arcs here, if there was a filter for that.
    
    tol = 0.001    
    print "( filtering to tolerance %.4f )" % ( tol ) 
    cl_filtered_paths = []
    t_before = time.time()
    n_filtered=0
    for cl_path in cl_paths:
        cl_filtered = filter_path(cl_path,tol)
        n_filtered = n_filtered + len(cl_filtered)
        cl_filtered_paths.append(cl_filtered)
    t_after = time.time()
    calctime = t_after-t_before
    print "( got %d filtered CL-points. Filter done in %.3f s )" % ( n_filtered , calctime )
    
    # output the toolpath (see above)
    printCLPoints(cl_filtered_paths)
    #printCLPoints(cl_paths)  # comment out the line above, and uncomment this one, to get unfiltered CL-points

    
