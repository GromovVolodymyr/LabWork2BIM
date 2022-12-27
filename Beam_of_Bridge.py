import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate
from StdReinfShapeBuilder.RotationAngles import RotationAngles
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from HandleService import HandleService

def check_allplan_version(build_unit, version):
    del build_unit
    del version
    return True

def create_new_element(build_unit, doc):
    segment = CreateBridge(doc)
    return segment.create(build_unit)

def move_handle(build_unit, handle_prop, input_pnt, doc):
    build_unit.change_property(handle_prop, input_pnt)

    if (handle_prop.handle_id == "BHeight"):
        build_unit.SecondHeight.value = build_unit.BHeight.value - build_unit.FirstHeight.value - build_unit.ForthHeight.value - build_unit.ThirdHeight.value
        if (build_unit.FifthHeight.value > build_unit.BHeight.value - build_unit.FirstHeight.value - 45.5):
            build_unit.FifthHeight.value = build_unit.BHeight.value - build_unit.FirstHeight.value - 45.5
    return create_new_element(build_unit, doc)

def modify_element(build_unit, name, value):
    if (name == "BHeight"):
        change = value - build_unit.FirstHeight.value - build_unit.SecondHeight.value - build_unit.ThirdHeight.value - build_unit.ForthHeight.value
        print(change)
        if (change < 0):
            change = abs(change)
            if (build_unit.FirstHeight.value > 300.):
                if (build_unit.FirstHeight.value - change < 300.):
                    change -= build_unit.FirstHeight.value - 300.
                    build_unit.FirstHeight.value = 300.
                else:
                    build_unit.FirstHeight.value -= change
                    change = 0.
            if (change != 0) and (build_unit.ThirdHeight.value > 150.):
                if (build_unit.ThirdHeight.value - change < 150.):
                    change -= build_unit.ThirdHeight.value - 150.
                    build_unit.ThirdHeight.value = 150.
                else:
                    build_unit.ThirdHeight.value -= change
                    change = 0.
            if (change != 0) and (build_unit.ForthHeight.value > 145.):
                if (build_unit.ForthHeight.value - change < 145.):
                    change -= build_unit.ForthHeight.value - 145.
                    build_unit.ForthHeight.value = 145.
                else:
                    build_unit.ForthHeight.value -= change
                    change = 0.
            if (change != 0) and (build_unit.SecondHeight.value > 450.):
                if (build_unit.SecondHeight.value - change < 450.):
                    change -= build_unit.SecondHeight.value - 450.
                    build_unit.SecondHeight.value = 450.
                else:
                    build_unit.SecondHeight.value -= change
                    change = 0.
        else:
            build_unit.SecondHeight.value += change
        if (value - build_unit.FirstHeight.value - 45.5 < build_unit.FifthHeight.value):
            build_unit.FifthHeight.value = value - build_unit.FirstHeight.value - 45.5   
    elif (name == "FirstHeight"):
        build_unit.BHeight.value = value + build_unit.SecondHeight.value + build_unit.ThirdHeight.value + build_unit.ForthHeight.value
    elif (name == "SecondHeight"):
        build_unit.BHeight.value = value + build_unit.FirstHeight.value + build_unit.ThirdHeight.value + build_unit.ForthHeight.value
    elif (name == "ThirdHeight"):
        build_unit.BHeight.value = value + build_unit.FirstHeight.value + build_unit.SecondHeight.value + build_unit.ForthHeight.value
        if (value + build_unit.ForthHeight.value + 45.5 > build_unit.FifthHeight.value):
            build_unit.FifthHeight.value = value + build_unit.ForthHeight.value + 45.5
    elif (name == "ForthHeight"):
        build_unit.BHeight.value = value + build_unit.FirstHeight.value + build_unit.SecondHeight.value + build_unit.ThirdHeight.value
        if (build_unit.ThirdHeight.value + value + 45.5 > build_unit.FifthHeight.value):
            build_unit.FifthHeight.value = build_unit.ThirdHeight.value + value + 45.5
    elif (name == "FifthHeight"):
        if (value > build_unit.BHeight.value - build_unit.FirstHeight.value - 45.5):
            build_unit.FifthHeight.value = build_unit.BHeight.value - build_unit.FirstHeight.value - 45.5
        elif (value < build_unit.ForthHeight.value + build_unit.ThirdHeight.value + 45.5):
            build_unit.FifthHeight.value = build_unit.ForthHeight.value + build_unit.ThirdHeight.value + 45.5
    elif (name == "Depth"):
        if (value >= build_unit.FirstLength.value / 2.):
            build_unit.Depth.value = build_unit.FirstLength.value / 2. - 45.5

    return True

class CreateBridge():
    def __init__(self, doc):
        self.model_ele_list = []
        self.handle_list = []
        self.document = doc       
    def create(self, build_unit):       
        self._top_sh_width = build_unit.FirstWidth.value
        self._top_sh_height = build_unit.FirstHeight.value
        self._bot_sh_width = build_unit.SecondWidth.value
        self._bot_sh_up_height = build_unit.ThirdHeight.value
        self._bot_sh_low_height = build_unit.ForthHeight.value
        self._bot_sh_height = self._bot_sh_up_height + self._bot_sh_low_height
        if (build_unit.Thick.value > min(self._top_sh_width, self._bot_sh_width)):
            build_unit.Thick.value = min(self._top_sh_width, self._bot_sh_width)        
        self._rib_thickness = build_unit.Thick.value
        self._rib_height = build_unit.SecondHeight.value
        self._beam_length = build_unit.FirstLength.value
        self._beam_width = max(self._top_sh_width, self._bot_sh_width)
        self._beam_height = build_unit.BHeight.value
        self._hole_depth = build_unit.Depth.value
        self._hole_height = build_unit.FifthHeight.value
        self._angleX = build_unit.RotateX.value
        self._angleY = build_unit.RotateY.value
        self._angleZ = build_unit.RotateZ.value
        self.create_beam(build_unit)
        self.create_handles(build_unit)       
        AllplanBaseElements.ElementTransform(AllplanGeo.Vector3D(), self._angleX, self._angleY, self._angleZ, self.model_ele_list)
        rot_angles = RotationAngles(self._angleX, self._angleY, self._angleZ)
        HandleService.transform_handles(self.handle_list, rot_angles.get_rotation_matrix())        
        return (self.model_ele_list, self.handle_list)
    def create_beam(self, build_unit):
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = build_unit.Color3.value
        com_prop.Stroke = 1
        bottom_shelf = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D((self._beam_width - self._bot_sh_width) / 2., 0., 0.), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), self._bot_sh_width, self._beam_length, self._bot_sh_height)
        edges = AllplanUtil.VecSizeTList()
        edges.append(10)
        edges.append(8)
        err, bottom_shelf = AllplanGeo.ChamferCalculus.Calculate(bottom_shelf, edges, 20., False)
        top_shelf = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D((self._beam_width - self._top_sh_width) / 2., 0., self._beam_height - self._top_sh_height), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), self._top_sh_width, self._beam_length, self._top_sh_height)
        top_shelf_notch = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D((self._beam_width - self._top_sh_width) / 2., 0., self._beam_height - 45.), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), 60., self._beam_length, 45.)
        err, top_shelf = AllplanGeo.MakeSubtraction(top_shelf, top_shelf_notch)
        if not GeometryValidate.polyhedron(err):
            return
        top_shelf_notch = AllplanGeo.Move(top_shelf_notch, AllplanGeo.Vector3D(self._top_sh_width - 60., 0, 0))
        err, top_shelf = AllplanGeo.MakeSubtraction(top_shelf, top_shelf_notch)
        if not GeometryValidate.polyhedron(err):
            return
        err, beam = AllplanGeo.MakeUnion(bottom_shelf, top_shelf)
        if not GeometryValidate.polyhedron(err):
            return
        rib = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0., 0., self._bot_sh_height), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), self._beam_width, self._beam_length, self._rib_height)        
        err, beam = AllplanGeo.MakeUnion(beam, rib)
        if not GeometryValidate.polyhedron(err):
            return
        
        left_notch_pol = AllplanGeo.Polygon2D()
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._rib_thickness) / 2., self._beam_height - self._top_sh_height)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._rib_thickness) / 2., self._bot_sh_height)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._bot_sh_width) / 2., self._bot_sh_low_height)
        left_notch_pol += AllplanGeo.Point2D(0., self._bot_sh_low_height)     
        left_notch_pol += AllplanGeo.Point2D(0., self._beam_height - 100.)
        left_notch_pol += AllplanGeo.Point2D(0., self._beam_height - 100.)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._top_sh_width) / 2., self._beam_height - 100.)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._rib_thickness) / 2., self._beam_height - self._top_sh_height)
        if not GeometryValidate.is_valid(left_notch_pol):
            return        
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, 0, 0)
        path += AllplanGeo.Point3D(0, build_unit.FirstLength.value, 0)
        err, notches = AllplanGeo.CreatePolyhedron(left_notch_pol, AllplanGeo.Point2D(0., 0.), path)
        if GeometryValidate.polyhedron(err):
            edges = AllplanUtil.VecSizeTList()
            if (self._rib_thickness == self._bot_sh_width):
                edges.append(0)
            elif (self._rib_thickness == self._top_sh_width):
                edges.append(1)
            else:
                edges.append(0)
                edges.append(2)
            err, notches = AllplanGeo.FilletCalculus3D.Calculate(notches, edges, 100., False)
            plane = AllplanGeo.Plane3D(AllplanGeo.Point3D(self._beam_width / 2., 0, 0), AllplanGeo.Vector3D(1, 0, 0))
            right_notch = AllplanGeo.Mirror(notches, plane)
            err, notches = AllplanGeo.MakeUnion(notches, right_notch)
            if not GeometryValidate.polyhedron(err):
                return            
            err, beam = AllplanGeo.MakeSubtraction(beam, notches)
            if not GeometryValidate.polyhedron(err):
                return
        sling_holes = AllplanGeo.BRep3D.CreateCylinder(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0,build_unit.Depth.value, build_unit.FifthHeight.value), AllplanGeo.Vector3D(0, 0, 1), AllplanGeo.Vector3D(1, 0, 0)), 45.5, self._beam_width)
        sling_hole_moved = AllplanGeo.Move(sling_holes, AllplanGeo.Vector3D(0., self._beam_length - self._hole_depth * 2, 0))
        err, sling_holes = AllplanGeo.MakeUnion(sling_holes, sling_hole_moved)
        if not GeometryValidate.polyhedron(err):
            return          
        err, beam = AllplanGeo.MakeSubtraction(beam, sling_holes)
        if not GeometryValidate.polyhedron(err):
            return        
        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(com_prop, beam))
        

    def create_handles(self, build_unit):        
        handle1 = HandleProperties("FirstLength",
                                   AllplanGeo.Point3D(0., self._beam_length, 0.),
                                   AllplanGeo.Point3D(0, 0, 0),
                                   [("FirstLength", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle1)

        handle2 = HandleProperties("BHeight",
                                   AllplanGeo.Point3D(0., 0., self._beam_height),
                                   AllplanGeo.Point3D(0, 0, 0),
                                   [("BHeight", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle2)
        
        handle3 = HandleProperties("FirstWidth",
                                   AllplanGeo.Point3D((self._beam_width - self._top_sh_width) / 2. + self._top_sh_width, 0., self._beam_height - 45.),
                                   AllplanGeo.Point3D((self._beam_width - self._top_sh_width) / 2., 0, self._beam_height - 45.),
                                   [("FirstWidth", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle3)

        handle4 = HandleProperties("SecondWidth",
                                   AllplanGeo.Point3D((self._beam_width - self._bot_sh_width) / 2. + self._bot_sh_width, 0., self._bot_sh_low_height),
                                   AllplanGeo.Point3D((self._beam_width - self._bot_sh_width) / 2., 0, self._bot_sh_low_height),
                                   [("SecondWidth", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle4)
        
        handle5 = HandleProperties("Thick",
                                   AllplanGeo.Point3D((self._beam_width - self._rib_thickness) / 2. + self._rib_thickness, 0., self._beam_height / 2.),
                                   AllplanGeo.Point3D((self._beam_width - self._rib_thickness) / 2., 0, self._beam_height / 2.),
                                   [("Thick", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle5)
