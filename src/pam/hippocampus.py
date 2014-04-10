import bpy
import sys

import pam
import pam_vis
import config
import exporter

import code

import imp

imp.reload(pam)
imp.reload(pam_vis)
imp.reload(config)
imp.reload(exporter)

EXPORT_PATH = '/home/martin/Dropbox/Work/Hippocampus3D/PAM/results/'


# get all important layers
dg = bpy.data.objects['DG_sg']
ca3 = bpy.data.objects['CA3_sp']
ca1 = bpy.data.objects['CA1_sp']
al_dg = bpy.data.objects['DG_sg_axons_all']
al_ca3 = bpy.data.objects['CA3_sp_axons_all']

ec2 = bpy.data.objects['EC_2']
ec2_1_i1 = bpy.data.objects['EC_2_axons.000']
ec2_1_i2 = bpy.data.objects['EC_2_axons.001']
ec2_1_i3 = bpy.data.objects['EC_2_axons.002']
ec2_1_i3 = bpy.data.objects['EC_2_axons.003']
ec2_1_synapses = bpy.data.objects['EC_2_axons.synapse_1']

ec2_2_i1 = bpy.data.objects['EC_2_axons.010']

ec2_3_i1 = bpy.data.objects['EC_2_axons.100']


# get all important neuron groups
dg_neurons = 'Granule Cells'
ca3_neurons = 'CA3_Pyramidal'
ca1_neurons = 'CA1_Pyramidal'

# number of neurons per layer
n_dg = 1200000
n_ca3 = 250000
n_ca1 = 390000

# number of outgoing connections
s_dg_ca3 = 15
s_ca3_ca3 = 6000
s_ca3_ca1 = 8580

f = 0.001     # factor for the neuron numbers

# adjust the number of neurons per layer
ca3.particle_systems[ca3_neurons].settings.count = int(n_ca3 * f)
dg.particle_systems[dg_neurons].settings.count = int(n_dg * f)

pam_vis.visualizeClean()
pam.initialize3D()

dg_params = [2., 0.5, 0., 0.]
ca3_params_dendrites = [0.4, 0.4, 0., 0.0]
ca3_params = [10., 0.1, -7., 0.00]

ca1_params_dendrites = ca3_params_dendrites
sub_params_dendrites = ca1_params_dendrites

###################################################
## measure ratio between real and UV-distances
###################################################
uv_data, layer_names = pam.measureUVs([al_dg, al_ca3])
exporter.export_UVfactors(EXPORT_PATH + 'UVscaling.zip', uv_data, layer_names)

#3 / 0 


pam.addConnection([dg, al_dg, ca3],                      # layers involved in the connection
   dg_neurons, ca3_neurons,       # neuronsets involved
   1,                                      # synaptic layer
   [config.MAP_euclid, config.MAP_euclid],                                 # connection mapping
   [config.DIS_euclidUV, config.DIS_euclid],                                 # distance calculation
   pam.connfunc_gauss_pre, dg_params, pam.connfunc_gauss_post, ca3_params_dendrites,   # kernel function plus parameters
   int(s_dg_ca3))                      # number of synapses for each  pre-synaptic neuron



if True:
    pam.addConnection([ca3, al_ca3, ca3],                      # layers involved in the connection
       ca3_neurons, ca3_neurons,       # neuronsets involved
       1,                                      # synaptic layer
       [config.MAP_normal, config.MAP_normal],                                 # connection mapping
       [config.DIS_normalUV, config.DIS_euclid],                                 # distance calculation
       pam.connfunc_gauss_pre, ca3_params, pam.connfunc_gauss_post, ca3_params_dendrites,   # kernel function plus parameters
       int(s_ca3_ca3 * 0.01))                      # number of synapses for each  pre-synaptic neuron

if True:
    pam.addConnection(
        [ca3, al_ca3, ca1],
        ca3_neurons,
        ca1_neurons,
        1,
        [config.MAP_normal, config.MAP_normal],
        [config.DIS_normalUV, config.DIS_euclid],
        pam.connfunc_gauss_pre,
        ca3_params,
        pam.connfunc_gauss_post,
        ca1_params_dendrites,
        int(s_ca3_ca1 * 0.01)
        )    
#    pam.addConnection(
#        layers=[ca3, al_ca3, ca1],
#        neuronset1=ca3_neurons,
#        neuronset2=ca1_neurons,
#        slayer=1,
#        connections=[config.MAP_normal, config.MAP_normal],
#        distances=[config.DIS_normalUV, config.DIS_euclid],
#        func_pre=pam.connfunc_gauss_pre,
#        args_pre=ca3_params,
#        func_post=pam.connfunc_gauss_post,
#        args_post=ca1_params_dendrites,
#        no_synapses=int(s_ca3_ca1 * 0.01)
#        )
                                               
pam.computeAllConnections()                                               
                                               
#print(pam.pam_connection_counter)
#print(pam.pam_connections)
#print(pam.pam_ng_list)

   
print("Visualization")    

particle = 22

p, n, f = ca3.closest_point_on_mesh(ca3.particle_systems[ca3_neurons].particles[particle].location)
pam_vis.visualizePoint(pam.map3dPointTo3d(
    al_ca3, al_ca3, p, n))

#namespace = globals().copy()
#namespace.update(locals())
#code.interact(local=namespace)
    

pam_vis.setCursor(ca3.particle_systems[ca3_neurons].particles[particle].location)    
pam_vis.visualizePostNeurons(1, particle)
pam_vis.visualizeConnectionsForNeuron(1, particle)

pam_vis.visualizePostNeurons(2, particle)
pam_vis.visualizeConnectionsForNeuron(2, particle)

particle = 22
#pam_vis.setCursor(dg.particle_systems[dg_neurons].particles[particle].location)

pam_vis.visualizePostNeurons(0, particle)
pam_vis.visualizeConnectionsForNeuron(0, particle)

#print(c_dg_ca3[particle])

exporter.export_connections(EXPORT_PATH + 'hippocampus.zip')