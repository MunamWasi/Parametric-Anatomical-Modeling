import bpy


vis_objects = 0

def setCursor(loc):
    """Just a more convenient way to set the location of the cursor"""

    bpy.data.screens['Default'].scene.cursor_location = loc


def getCursor():
    """Just returns the cursor location. A bit shorter to type ;)"""

    return bpy.data.screens['Default'].scene.cursor_location


def visualizePostNeurons(layer, neuronset, connectivity):
    """visualizes the post-synaptic neurons that are connected with a given
    neuron from the presynaptic layer
    layer       : post-synaptic layer
    neuronset   : name of the particlesystem
    connectivity: connectivity-vector """
    
    global vis_objects
    
    for i in range(0, len(connectivity)):
        if connectivity[i] > 0.7:
             bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=layer.particle_systems[neuronset].particles[i].location, layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
             bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
             bpy.context.selected_objects[0].name = "visualization.%03d" % vis_objects
             vis_objects = vis_objects + 1
             
def visualizePoint(point):
    """ visualizes a point in 3d by creating a small sphere """
    global vis_objects    
    bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=point, layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
    bpy.context.selected_objects[0].name = "visualization.%03d" % vis_objects
    vis_objects = vis_objects + 1
    
    
def visualizePath(pointlist):
    """ Create path for a given point list 
    
    This code is taken and modified from the bTrace-Addon for Blender
    http://blenderartists.org/forum/showthread.php?214872  """
    
    global vis_objects
    
     # trace the origins
    tracer = bpy.data.curves.new('tracer','CURVE')
    tracer.dimensions = '3D'
    spline = tracer.splines.new('BEZIER')
    spline.bezier_points.add(len(pointlist)-1)
    curve = bpy.data.objects.new('curve',tracer)
    bpy.context.scene.objects.link(curve)
    
    # render ready curve
    tracer.resolution_u = 8
    tracer.bevel_resolution = 8 # Set bevel resolution from Panel options
    tracer.fill_mode = 'FULL'
    tracer.bevel_depth = 0.01 # Set bevel depth from Panel options
    
    # move nodes to objects
    for i in range(0, len(pointlist)):
        p = spline.bezier_points[i]
        p.co = pointlist[i]
        p.handle_right_type='VECTOR'
        p.handle_left_type='VECTOR'

    bpy.context.scene.objects.active = curve
    bpy.ops.object.mode_set()    
    curve.name = "visualization.%03d" % vis_objects
    
    vis_objects = vis_objects + 1
    
    
def visualizeClean():
    """delete all visualization objects"""

    # delete all previous spheres
    global vis_objects    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="visualization*")
    bpy.ops.object.delete(use_global=False)   
    vis_objects = 0 

