import hapi
import numpy

# Create an in process HAPI session. It's also possible to
# connect to a remote session, such as a Houdini SessionSync
# session, if one is available. For example:
# session = hapi.createThriftSocketSession("localhost", 9090)
session = hapi.createInProcessSession()

# Init the session with default cook options.
options = hapi.CookOptions()
hapi.initialize(session, options)

# Define vertex positions for our test geometry
vertexPositions = numpy.array([-0.5, -0.5, -0.5,
                                0.5, -0.5, -0.5,
                                0.5, -0.5,  0.5,
                               -0.5, -0.5,  0.5,
                               -0.5,  0.5, -0.5,
                                0.5,  0.5, -0.5,
                                0.5,  0.5,  0.5,
                               -0.5,  0.5,  0.5])

# Face and vert info for our test geometry
vertexIndices = numpy.array([
    1,5,4,0,2,6,5,1,3,7,6,2,0,4,7,3,2,1,0,3,5,6,7,4])
faceCounts = numpy.array([4, 4, 4, 4, 4, 4])
nVerts = len(vertexPositions)//3
nFaces = len(vertexIndices)//4

# Construct an input node to stash our geo into
input_id = hapi.createInputNode(session, "input_node")
geo_info = hapi.getDisplayGeoInfo(session, input_id)

# Build the the part info and store it to our geo info. This is an example
# of what access a HAPI struct in Python looks like. Python provides a
# constructor for the struct that default-initializes all of the fields. Theh
# fields can then be accessed as properties on the object.
part_info = hapi.PartInfo(
    vertexCount = len(vertexIndices),
    faceCount = nFaces,
    pointCount = nVerts,
    type = hapi.partType.Mesh)

hapi.setPartInfo(session, geo_info.nodeId, 0, part_info)

# Define the attribute info for the P attribute
p_info = hapi.AttributeInfo(
    exists = True,
    owner = hapi.attributeOwner.Point,
    count = nVerts,
    tupleSize = 3,
    storage = hapi.storageType.Float,
    originalOwner = hapi.attributeOwner.Invalid)

# P attribute can then be added to the geo
hapi.addAttribute(session, geo_info.nodeId, 0, "P", p_info)

# We still need to tell HAPI how many values to extract from the input array.
# HAPI is able to use less than the total number of values.
hapi.setAttributeFloatData_np(session, geo_info.nodeId, 0, "P", p_info,
    vertexPositions, 0, nVerts)

# Set the face and vert info on the geo itself.
hapi.setFaceCounts_np(session, geo_info.nodeId, 0, faceCounts, 0,
    len(faceCounts))
hapi.setVertexList_np(session, geo_info.nodeId, 0, vertexIndices, 0,
    len(vertexIndices))

# Submit all of the geometry changes we've made so they're added to Houdini.
hapi.commitGeo(session, geo_info.nodeId)

# We can then ask the node to save it's geometry to disk.
hapi.saveGeoToFile(session, geo_info.nodeId, "hapi_createmesh.bgeo.sc")