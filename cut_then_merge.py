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
import OCC.TopoDS
import OCC.BRep
import OCC.GarbageCollector
import numpy as NP
import math
import multiprocessing as processing

gc = OCC.GarbageCollector.GarbageCollector()

length = 594.6
width = 136.0
thickness = 5.0
spacing = 2.1
groove_width = 0.175
groove_depth = 0.03
number_of_slices = int(math.floor(length/spacing))
box = BRepPrimAPI_MakeBox(spacing,width,thickness).Shape()
# Make the transverse groove
print('Adding transverse groove')
pnt1 = OCC.gp.gp_Pnt(spacing/2.0, 0., thickness - groove_depth)
pnt2 = OCC.gp.gp_Pnt(spacing/2.0 + groove_width/2.0, 0., thickness)
pnt3 = OCC.gp.gp_Pnt(spacing/2.0 - groove_width/2.0, 0., thickness)
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
b = OCC.BRepPrimAPI.BRepPrimAPI_MakePrism(face.Face() , v).Shape()
print('Making transverse cut')
lga = OCC.BRepAlgoAPI.BRepAlgoAPI_Cut(box, b).Shape()
# Make the grooves with an arithmetic progression
a1 = 1.32 # Spacing between first two grooves
an = 0.85 # Spacing between next to the last and the last groove
d1 = 9.0 # Distance from the edge to the center of the first groove
d2 = 9.0 # Distance from the edge to the center of the last groove
sn = width - d1 - d2 # Distance from first groove to last groove
n = int(math.floor(2*sn/(a1+an))) # number of grooves
d = (an-a1)/(n-1) # difference in spacing between grooves
y = d1
print('number of grooves %d' % (n,))
for i, k in enumerate(range(1,n+1)):
    print('Adding longitudinal groove %d of %d' % (i+1, n))
    print('y %s' % (y,))
    pnt1 = OCC.gp.gp_Pnt(0.0, y, thickness - groove_depth)
    pnt2 = OCC.gp.gp_Pnt(0.0, y + groove_width/2.0, thickness)
    pnt3 = OCC.gp.gp_Pnt(0.0, y - groove_width/2.0, thickness)
    seg1 = OCC.GC.GC_MakeSegment(pnt1, pnt2)
    seg2 = OCC.GC.GC_MakeSegment(pnt2, pnt3)
    seg3 = OCC.GC.GC_MakeSegment(pnt3, pnt1)
    del pnt1
    del pnt2
    del pnt3
    gc.purge()
    e1 = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(OCC.Geom.Handle_Geom_TrimmedCurve(seg1.Value()))
    e2 = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(OCC.Geom.Handle_Geom_TrimmedCurve(seg2.Value()))
    e3 = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeEdge(OCC.Geom.Handle_Geom_TrimmedCurve(seg3.Value()))
    mw = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeWire()
    del seg1
    del seg2
    del seg3
    gc.purge()
    mw.Add(e1.Edge())
    mw.Add(e2.Edge())
    mw.Add(e3.Edge())
    face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(mw.Wire())
    del e1
    del e2
    del e3
    gc.purge()
    v = OCC.gp.gp_Vec(spacing, 0., 0.)
    b = OCC.BRepPrimAPI.BRepPrimAPI_MakePrism(face.Face() , v).Shape()
    del face
    gc.purge()
    ak = a1 + (k-1)*d
    y = y + ak
    print('Making longitudinal cut')
    lga = OCC.BRepAlgoAPI.BRepAlgoAPI_Cut(lga, b).Shape()
    del b
    gc.purge()
# Transform the slices
slices = [lga,]
v = OCC.gp.gp_Vec(spacing, 0., 0.)
for i in range(1, number_of_slices): 
    print('Translating %s' % (i,))
    trans = OCC.gp.gp_Trsf()
    trans.SetTranslation(v)
    brep_trns = OCC.BRepBuilderAPI.BRepBuilderAPI_Transform(slices[i - 1], trans, True)
    brep_trns.Build()
    slices.append(brep_trns.Shape())

def fuser(two_shapes):
    slice_id, shape1, shape2 = two_shapes
    print('Slices being fused: %s' % (slice_id,))
    fused = OCC.BRepAlgoAPI.BRepAlgoAPI_Fuse(shape1, shape2).Shape()
    return fused

P = processing.Pool(4)
results_1 = P.map(fuser, [(1,slices[0], slices[1]),
                          (2, slices[2], slices[3]),
                          (3, slices[4], slices[5]),
                          (4, slices[6],slices[7])])
P.close()
P.join()
del slices
gc.purge()
P = processing.Pool(2)
results_2 = P.map(fuser, [(5, results_1[0], results_1[1]),(6, results_1[2], results_1[3])])
P.close()
P.join()
del results_1
gc.purge()
results_3 = fuser((7, results_2[0], results_2[1]))

display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(results_3)
start_display()

stp_exporter = OCC.Utils.DataExchange.STEP.STEPExporter('lga.stp')
stp_exporter.SetTolerance(tolerance=0.00001)
stp_exporter.AddShape(lga)
stp_exporter.WriteFile()
