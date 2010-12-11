from OCC.Display.SimpleGui import *
from OCC.BRepPrimAPI import *
import OCC.gp
import OCC.GC
import OCC.BRepBuilderAPI
import OCC.Geom
import OCC.BRepPrimAPI
import OCC.BRepAlgoAPI
import OCC.Utils.DataExchange.STEP
import OCC.Utils.DataExchange.STL
import numpy as NP
import math
import time

class Timer():
   def __enter__(self): self.start = time.time()
   def __exit__(self, *args): print 'Time spent: %s' % (time.time() - self.start,)

length = 594.6
width = 136.0
thickness = 5.0
spacing = 2.1
groove_width = 0.175
groove_depth = 0.03
lga = BRepPrimAPI_MakeBox(length,width,thickness).Shape()
# Make the transverse grooves
num_transverse = len(NP.arange(spacing, length, spacing))
for i, x in enumerate(NP.arange(spacing, length, spacing)):
    with Timer():
        print('Working on transverse groove %d of %d' % (i + 1, num_transverse))
        pnt1 = OCC.gp.gp_Pnt(x, 0., thickness - groove_depth)
        pnt2 = OCC.gp.gp_Pnt(x + groove_width/2.0, 0., thickness)
        pnt3 = OCC.gp.gp_Pnt(x - groove_width/2.0, 0., thickness)
        seg1 = OCC.GC.GC_MakeSegment(pnt1, pnt2)
        seg2 = OCC.GC.GC_MakeSegment(pnt2, pnt3)
        seg3 = OCC.GC.GC_MakeSegment(pnt3, pnt1)
        e1 = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(OCC.Geom.Handle_Geom_TrimmedCurve(seg1.Value()))
        e2 = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(OCC.Geom.Handle_Geom_TrimmedCurve(seg2.Value()))
        e3 = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(OCC.Geom.Handle_Geom_TrimmedCurve(seg3.Value()))
        mw = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeWire()
        mw.Add(e1.Edge())
        mw.Add(e2.Edge())
        mw.Add(e3.Edge())
        face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(mw.Wire())
        v = OCC.gp.gp_Vec(0., width, 0.)
        b = OCC.BRepPrimAPI.BRepPrimAPI_MakePrism(face.Face() , v)
        lga = OCC.BRepAlgoAPI.BRepAlgoAPI_Cut(lga, b.Shape()).Shape()
# Make the grooves with an arithmetic progression
a1 = 1.32 # Spacing between first two grooves
an = 0.85 # Spacing between next to the last and the last groove
d1 = 9.0 # Distance from the edge to the center of the first groove
d2 = 9.0 # Distance from the edge to the center of the last groove
sn = width - d1 - d2 # Distance from first groove to last groove
n = int(math.floor(2*sn/(a1+an))) # number of grooves
d = (an-a1)/(n-1) # difference in spacing between grooves
y = d1
for i, k in enumerate(range(1,n+1)):
    with Timer():
        print('Working on longitudinal groove %d of %d' % (i + 1, n))
        pnt1 = OCC.gp.gp_Pnt(0.0, y, thickness - groove_depth)
        pnt2 = OCC.gp.gp_Pnt(0.0, y + groove_width/2.0, thickness)
        pnt3 = OCC.gp.gp_Pnt(0.0, y - groove_width/2.0, thickness)
        seg1 = OCC.GC.GC_MakeSegment(pnt1, pnt2)
        seg2 = OCC.GC.GC_MakeSegment(pnt2, pnt3)
        seg3 = OCC.GC.GC_MakeSegment(pnt3, pnt1)
        e1 = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(OCC.Geom.Handle_Geom_TrimmedCurve(seg1.Value()))
        e2 = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(OCC.Geom.Handle_Geom_TrimmedCurve(seg2.Value()))
        e3 = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(OCC.Geom.Handle_Geom_TrimmedCurve(seg3.Value()))
        mw = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeWire()
        mw.Add(e1.Edge())
        mw.Add(e2.Edge())
        mw.Add(e3.Edge())
        face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(mw.Wire())
        v = OCC.gp.gp_Vec(length, 0., 0.)
        b = OCC.BRepPrimAPI.BRepPrimAPI_MakePrism(face.Face() , v)
        lga = OCC.BRepAlgoAPI.BRepAlgoAPI_Cut(lga, b.Shape()).Shape()
        ak = a1 + (k-1)*d
        y = y + ak

stp_exporter = OCC.Utils.DataExchange.STEP.STEPExporter('lga.stp')
stp_exporter.SetTolerance(tolerance=0.00001)
stp_exporter.AddShape(lga)
stp_exporter.WriteFile()

display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(lga)
start_display()
