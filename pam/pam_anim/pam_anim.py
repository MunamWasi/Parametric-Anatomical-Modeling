import bpy

import math
import heapq
import numpy

from .. import pam_vis
from .. import model
from . import data
from . import anim_spikes
from . import anim_functions
from .helper import *

import logging

logger = logging.getLogger(__package__)

# CONSTANTS
TAU = 20
CURVES = {}
SPIKE_OBJECTS = []
DEFAULT_MAT_NAME = "SpikeMaterial"

PATHS_GROUP_NAME = "PATHS"
SPIKE_GROUP_NAME = "SPIKES"


# TODO(SK): Rephrase docstring, add a `.. note::` or `.. warning::`
def clearVisualization():
    """Clears all created objects by the animation
    The objects are saved in the specified groups and all
    objects in these groups will be deleted!"""

    anim_spikes.deleteNeurons()
    if SPIKE_GROUP_NAME in bpy.data.groups:
        neuronObjects = bpy.data.groups[SPIKE_GROUP_NAME].objects
        for obj in neuronObjects:
            bpy.context.scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)

    if PATHS_GROUP_NAME in bpy.data.groups:
        paths = bpy.data.groups[PATHS_GROUP_NAME].objects
        for curve in paths:
            bpy.context.scene.objects.unlink(curve)
            data = curve.data
            bpy.data.objects.remove(curve)
            bpy.data.curves.remove(data)

    pam_vis.vis_objects = 0

    global CURVES
    global SPIKE_OBJECTS
    CURVES = {}
    SPIKE_OBJECTS = []


# TODO(SK): Rephrase docstring, short 50 character summury and then a next
# TODO(SK): paragraph for further details
# TODO(SK): Parameter types missing
def followCurve(curve, startTime, color, meshData):
    """This function creates a new object with the given mesh and adds
    a `Follow Curve` constraint to it

    To calculate the start time correctly the length of the curve needs to be
    saved in the custom property `timeLength` in the curves data.

    :param (???) curve: curve to apply the constraint to
    :param (???) startTime: start time in frames for when the animation should start playing
    :param (???) color: color to apply to the color property of the object
    :param (???) meshData: mesh data for the object


    :return: spike object
    :rtype:

    """
    op = bpy.context.scene.pam_anim_orientation

    obj = bpy.data.objects.new("Spike", meshData)
    obj.color = color
    bpy.context.scene.objects.link(obj)

    constraint = obj.constraints.new(type="FOLLOW_PATH")
    constraint.offset = startTime / curve.data["timeLength"] * 100
    constraint.target = curve

    startFrame = int(startTime)

    obj.hide = True
    obj.keyframe_insert(data_path="hide", frame=startFrame - 2)
    obj.hide = False
    obj.keyframe_insert(data_path="hide", frame=startFrame - 1)
    obj.hide = True
    obj.keyframe_insert(data_path="hide", frame=math.ceil(startFrame + curve.data["timeLength"]))

    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_render", frame=startFrame - 2)
    obj.hide_render = False
    obj.keyframe_insert(data_path="hide_render", frame=startFrame - 1)
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_render", frame=math.ceil(startFrame + curve.data["timeLength"]))

    if(op.orientationType == 'FOLLOW'):
        constraint.use_curve_follow = True

    if(op.orientationType == 'OBJECT'):
        # For eventual camera tracking
        camConstraint = obj.constraints.new(type="TRACK_TO")
        camConstraint.target = bpy.data.objects[op.orientationObject]
        camConstraint.track_axis = "TRACK_Z"
        camConstraint.up_axis = "UP_Y"

    return obj


# TODO(SK): Rephrase docstring, short 50 character summury and then a next
# TODO(SK): paragraph for further details
# TODO(SK): Parameter types missing
def setAnimationSpeed(curve, animationSpeed):
    """Sets a curves animation speed to the given speed with a linear interpolation. Any object bound to this
    curve with a Follow Curve constraint will have completed its animation along the curve in the given time.

    :param curve:           The curve (bpy.types.Curve)
    :param animationSpeed:  The animation speed in frames
    """
    curve.eval_time = 0
    curve.keyframe_insert(data_path="eval_time", frame=0)
    curve.eval_time = 100
    curve.keyframe_insert(data_path="eval_time", frame=int(animationSpeed))

    # Set all the keyframes to linear interpolation to ensure a constant speed along the curve
    for key in curve.animation_data.action.fcurves[0].keyframe_points:
        key.interpolation = 'LINEAR'
    # Set the extrapolation of the curve to linear (This is important, without it, neurons with an offset start would not be animated)
    curve.animation_data.action.fcurves[0].extrapolation = 'LINEAR'


# TODO(SK): Missing docstring
def calculateDecay(layerValues, delta, decayFunc):
    newValues = {}
    for key in layerValues:
        newValues[key] = decayFunc(layerValues[key], delta)
        if newValues[key] < 0:
            newValues[key] = 0
    return newValues


# TODO(SK): Rephrase docstring
def createDefaultMaterial():
    """Creates a default material with a white diffuse color and the use object color property set to True.
    The name for this material is defined in the global variable DEFAULT_MAT_NAME"""
    options = bpy.context.scene.pam_anim_material
    if options.material != DEFAULT_MAT_NAME:
        mat = bpy.data.materials.new(DEFAULT_MAT_NAME)
        mat.diffuse_color = (1.0, 1.0, 1.0)
        mat.use_object_color = True
        options.material = mat.name


# TODO(SK): Rephrase docstring
# TODO(SK): max 80 characters per line
def getUsedNeuronGroups():
    """Checks in pam.model which neuron groups are actually be used and return
    the indices of those neurongroups. This routine is used by visualize() in order
    to reduce the number of neurongroups for which neurons should be created """
    inds = []
    for c in model.CONNECTION_INDICES:
        inds.append(c[1])
        inds.append(c[2])
    return numpy.unique(inds)


# TODO(SK): Rephrase docstring, short 50 character summury and then a next
# TODO(SK): paragraph for further details
def visualize(decayFunc=anim_functions.decay,
              initialColorValuesFunc=anim_functions.getInitialColorValues,
              mixValuesFunc=anim_functions.mixLayerValues,
              applyColorFunc=anim_functions.applyColorValues):
    """This function creates the visualization of spikes

    :param function decayFunc: calculates the decay of spikes
    :param function initialColorValuesFunc: sets the initial color of the spikes
    :param function mixValuesFunc: provides mixing of spike colors
    :param function applyColorFunc: applies color to the spikes

    """

    n = data.NEURON_GROUPS
    c = data.CONNECTIONS
    t = data.TIMINGS
    d = data.DELAYS

    # Dictionary for generated curves, so we don't need to generate them twice
    global CURVES

    neuronValues = {}
    neuronUpdateQueue = []

    no_timings = len(t)

    maxConn = bpy.context.scene.pam_anim_animation.connNumber

    for no, timing in enumerate(t):
        # if (no % 10) == 0:
        logger.info(str(no) + "/" + str(no_timings))

        neuronID = timing[0]
        neuronGroupID = timing[1]
        fireTime = timing[2]

        neuronGroup = n[neuronGroupID]

        # Update the color values of all neurons with queued updates
        poppedValues = getQueueValues(neuronUpdateQueue, fireTime)
        for elem in poppedValues:
            updateTime = elem[0]
            key = elem[1]
            newLayerValues = elem[2]

            # If the key already has values, we have to calculate the decay of the values and then mix them with the incoming values
            if key in neuronValues:
                oldLayerValues = neuronValues[key][0]
                lastUpdateTime = neuronValues[key][1]

                oldLayerValuesDecay = calculateDecay(oldLayerValues, updateTime - lastUpdateTime, decayFunc)
                updatedLayerValues = mixValuesFunc(oldLayerValuesDecay, newLayerValues)

                neuronValues[key] = (updatedLayerValues, updateTime)
            # If not, we don't need to mix the colors together, as this would just darken the color
            else:
                neuronValues[key] = (newLayerValues, updateTime)

        if neuronID in neuronValues:
            # Update this neuron
            layerValues = neuronValues[neuronID][0]
            lastUpdateTime = neuronValues[neuronID][1]
            layerValuesDecay = calculateDecay(layerValues, fireTime - lastUpdateTime, decayFunc)

            # Now that the neuron has fired, its values go back down to zero
            del(neuronValues[neuronID])

        else:
            layerValuesDecay = initialColorValuesFunc(neuronGroupID, neuronID, data.NEURON_GROUPS)

        for connectionID in neuronGroup.connections:
            if maxConn == 0:
                conns = len(c[connectionID[0]]["c"][neuronID])
            else:
                conns = min(maxConn, len(c[connectionID[0]]["c"][neuronID]))

            for index, i in enumerate(c[connectionID[0]]["c"][neuronID]):
                if index < conns:
                    if (i == -1) | (d[connectionID[0]][neuronID][index] == 0):
                        continue
                    if (connectionID[0], neuronID, i) not in CURVES.keys():
                        # If we do not have a curve already generated, we generate a new one with PAM and save it in our dictionary
                        # print("Calling visualizeOneConnection with " + str(connectionID[0]) + ", " + str(neuronID)+ ", " + str(i))
                        curve = CURVES[(connectionID[0], neuronID, i)] = pam_vis.visualizeOneConnection(connectionID[0], neuronID, i)

                        # The generated curve needs the right animation speed, so we set the custom property and generate the animation
                        curveLength = timeToFrames(d[connectionID[0]][neuronID][index])
                        # print(curve)
                        setAnimationSpeed(curve.data, curveLength)
                        curve.data["timeLength"] = curveLength
                    else:
                        curve = CURVES[(connectionID[0], neuronID, i)]

                    startFrame = projectTimeToFrames(fireTime)
                    obj = followCurve(curve, startFrame, (0.0, 0.0, 1.0, 1.0), bpy.data.meshes[bpy.context.scene.pam_anim_mesh.mesh])
                    SPIKE_OBJECTS.append(obj)

                    applyColorFunc(obj, layerValuesDecay, neuronID, neuronGroupID, data.NEURON_GROUPS)

                # Queue an update to the connected neuron
                updateTime = fireTime + d[connectionID[0]][neuronID][index]
                heapq.heappush(neuronUpdateQueue, (updateTime, i, layerValuesDecay))


class ClearPamAnimOperator(bpy.types.Operator):
    """Clear Animation"""
    bl_idname = "pam_anim.clear_pamanim"
    bl_label = "Clear Animation"
    bl_description = "Deletes the Spike-Animation"

    def execute(self, context):
        clearVisualization()
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


# TODO(SK): Rephrase docstring, purpose? If this could generate everything I
# TODO(SK): would stop working... right... about ...now!
class GenerateOperator(bpy.types.Operator):
    """Generate everything when PAM model, modeldata and simulationData are provided"""

    bl_idname = "pam_anim.generate"
    bl_label = "Generate"
    bl_description = "Generates the animation"

    @classmethod
    def poll(cls, context):

        # Check if a valid mesh has been selected
        if context.scene.pam_anim_mesh.mesh not in bpy.data.meshes:
            return False

        # Check if a model is loaded into pam
        if not model.NG_LIST:
            return False

        # Check if either spikes or paths are to be animated (would generate nothing if not active)
        if not (context.scene.pam_anim_mesh.animSpikes or context.scene.pam_anim_mesh.animPaths):
            return False

        # Return True if all data is accessible
        return True

    def execute(self, context):
        data.NEURON_GROUPS = []
        data.CONNECTIONS = []
        data.DELAYS = []
        data.TIMINGS = []

        # Clear old objects if available
        clearVisualization()

        # Read data from files
        logger.info('Read model data from csv file')
        data.readModelData(bpy.context.scene.pam_anim_data.modelData)
        logger.info('Read spike-data')
        data.readSimulationData(bpy.context.scene.pam_anim_data.simulationData)
        logger.info('Prepare Visualization')

        if bpy.context.scene.pam_anim_mesh.animPaths:
            # Create a default material if needed
            if bpy.context.scene.pam_anim_material.materialOption == "DEFAULT":
                createDefaultMaterial()

            # Prepare functions
            decayFunc = anim_functions.decay
            getInitialColorValuesFunc = anim_functions.getInitialColorValues
            mixLayerValuesFunc = anim_functions.mixLayerValues
            applyColorValuesFunc = anim_functions.applyColorValues

            # Load any scripts
            script = bpy.context.scene.pam_anim_material.script
            if script in bpy.data.texts:
                localFuncs = {}
                exec(bpy.data.texts[script].as_string(), localFuncs)
                if "decay" in localFuncs:
                    decayFunc = localFuncs['decay']
                if "getInitialColorValues" in localFuncs:
                    getInitialColorValuesFunc = localFuncs['getInitialColorValues']
                if "mixLayerValues" in localFuncs:
                    mixLayerValuesFunc = localFuncs['mixLayerValues']
                if "applyColorValues" in localFuncs:
                    applyColorValuesFunc = localFuncs['applyColorValues']

            # Create the visualization
            logger.info('Visualize spike propagation')
            visualize(decayFunc, getInitialColorValuesFunc, mixLayerValuesFunc, applyColorValuesFunc)

            # Create groups if they do not already exist
            if PATHS_GROUP_NAME not in bpy.data.groups:
                bpy.data.groups.new(PATHS_GROUP_NAME)
            if SPIKE_GROUP_NAME not in bpy.data.groups:
                bpy.data.groups.new(SPIKE_GROUP_NAME)

            # Insert objects into groups
            addObjectsToGroup(bpy.data.groups[PATHS_GROUP_NAME], CURVES)
            addObjectsToGroup(bpy.data.groups[SPIKE_GROUP_NAME], SPIKE_OBJECTS)

            # Apply material to mesh
            mesh = bpy.data.meshes[bpy.context.scene.pam_anim_mesh.mesh]
            mesh.materials.clear()
            mesh.materials.append(bpy.data.materials[bpy.context.scene.pam_anim_material.material])

        # Animate spiking if option is selected
        if bpy.context.scene.pam_anim_mesh.animSpikes is True:
            logger.info("Create neurons")
            neuron_object = bpy.data.objects[bpy.context.scene.pam_anim_mesh.neuron_object]
            ng_inds = getUsedNeuronGroups()
            for ind in ng_inds:
                logger.info("Generate neurons for ng " + str(ind))
                anim_spikes.generateLayerNeurons(bpy.data.objects[data.NEURON_GROUPS[ind].name], data.NEURON_GROUPS[ind].particle_system, neuron_object)
            logger.info("Create spike animation for neurons")
            anim_spikes.animNeuronSpiking(anim_spikes.animNeuronScaling)

        return {'FINISHED'}

    def invoke(self, context, event):

        return self.execute(context)


# TODO(SK): Missing docstring
def register():
    # Custom property for the length of a curve for easy accessibility
    bpy.types.Curve.timeLength = bpy.props.FloatProperty()
    bpy.utils.register_class(GenerateOperator)
    bpy.utils.register_class(ClearPamAnimOperator)


# TODO(SK): Missing docstring
def unregister():
    bpy.utils.unregister_class(GenerateOperator)
    bpy.utils.unregister_class(ClearPamAnimOperator)
