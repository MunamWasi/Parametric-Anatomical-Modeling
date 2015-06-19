import mstree
import mst_blender
import numpy as np
import bpy
import mathutils
from pam import pam

def create_uv_tree(obj, quantity, uv_center, mean = [0.0, 0.0], variance = [0.005, 0.005], balancing_factor = 0.0, build_type = 'MESH'):

    # Generate scattered points
    x = np.random.normal(uv_center[0], variance[0], quantity) + mean[0]
    y = np.random.normal(uv_center[1], variance[1], quantity) + mean[1]

    points = np.dstack((x, y))
    np.clip(points, 0., 1., out = points)

    # Run mstree
    root_point = mstree.mstree(points[0], balancing_factor)
    print(len(points[0]))
    # Convert node positions from uv to 3d
    nodes = mstree.tree_to_list(root_point)
    print(len(nodes))
    # print(root_point.pos)
    node_uv_points = [mathutils.Vector((node.pos[0], node.pos[1])) for node in nodes]

    node_3d_points = pam.mapUVPointTo3d(obj, node_uv_points)
    print(len(node_3d_points))

    for i, node in enumerate(node_3d_points):
        node.pos = node_3d_points[i]

    if build_type == 'CURVE':
        curve_obj = mst_blender.buildTreeCurve(root_point)
        curve_obj.data.bevel_depth = 0.1
    elif build_type == 'MESH':
        mesh_obj = mst_blender.buildTreeMesh(root_point)

def export_swc(root_node, outfilename, structure_identifier = 2):
    nodes = mstree.tree_to_list(root_node)
    f = open(outfilename, 'w')
    index = 0
    for node in nodes:
        node.index = index
        index += 1

        if node.parent is not None:
            parent_index = node.parent.index
        else:
            parent_index = -1

        f.write(' '.join((str(node.index), str(structure_identifier), str(node.pos[0]), str(node.pos[1]), str(node.pos[2]), str(0), str(parent_index))))
        f.write('\n')
    f.close()
    
def createAxons(p_obj, s_obj, quantity, mean, variance):
    for p in p_obj.particle_systems[0].particles:
        uv = pam.map3dPointToUV(p_obj, s_obj, p.location)
        create_uv_tree(s_obj, quantity, uv, mean, variance)

if __name__ == '__main__':
    create_uv_tree(bpy.data.objects['CA3_sp_axons_all'], 100, (0.1, 0.2))