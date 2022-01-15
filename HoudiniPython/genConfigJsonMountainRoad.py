import hou
import json


def genConfigJson():
    HipPath = hou.getenv("HIP")
    JsonPath = HipPath + "/MountainRoad.Json"
    JsonTemp = {}

    JsonTemp["readme"] = "In every list, the index is corresponding to hierarchy." \
                         "The every key of dict is corresponding to type. Do Not Modify The Key!"

    decalTemp = {}
    decalTemp["decal_type"] = "patch or crack"
    decalTemp["decal_mat"] = "The unreal decal material path"
    JsonTemp["decal"] = [decalTemp, decalTemp, decalTemp]

    roadTemp = {}
    roadTemp["Road_Mat"] = "The unreal road material Path"
    roadTemp["Cross_Mat"] = "The unreal cross material Path"
    roadTemp["End_Cross_Mat"] = "The unreal end cross material Path"
    JsonTemp["road"] = [roadTemp, roadTemp, roadTemp]

    edgeTemp = {}
    edgeTemp["Edge_Road_Mat"] = "The unreal road edge material Path"
    edgeTemp["Edge_Cross_Mat"] = "The unreal cross edge material Path"
    edgeTemp["Edge_End_Cross_Mat"] = "The unreal end cross edge material Path"
    JsonTemp["edge_road"] = [edgeTemp, edgeTemp, edgeTemp]

    with open(JsonPath, "w") as JsonFile:
        json.dump(JsonTemp, JsonFile)


def loadRoadMatJson():
    import json
    import os

    node = hou.pwd()
    geo = node.geometry()

    jsonPath = node.parm("path").evalAsString()
    if os.path.exists(jsonPath):
        # json content
        with open(jsonPath, "r") as jsonFile:
            content = json.loads(jsonFile.read())
        # get material path
        if "road" in content:
            road_mats = content["road"]
            edge_mats = content["edge_road"]
            # create the attribute
            if not geo.findPrimAttrib("unreal_material"):
                geo.addAttrib(hou.attribType.Prim, "unreal_material", "")

            # primitives iteration
            for prim in geo.prims():
                for group in prim.groups():
                    # get hierarchy and mats
                    h = prim.intAttribValue("hierarchy")
                    h = min(h, len(road_mats) - 1)
                    mats = road_mats[h]
                    # road or cross or end_cross
                    if group.name() == "road":
                        prim.setAttribValue("unreal_material", mats["Road_Mat"])
                        break
                    elif group.name() == "road_edge":
                        prim.setAttribValue("unreal_material", edge_mats["End_Cross_Mat"])
                    elif group.name() == "cross":
                        prim.setAttribValue("unreal_material", mats["Cross_Mat"])
                        break
                    elif group.name() == "cross_edge":
                        prim.setAttribValue("unreal_material", edge_mats["Edge_Cross_Mat"])
                        break
                    elif group.name() == "end_cross":
                        prim.setAttribValue("unreal_material", mats["End_Cross_Mat"])
                        break
                    elif group.name() == "end_cross_edge":
                        prim.setAttribValue("unreal_material", edge_mats["Edge_End_Cross_Mat"])
                        break
