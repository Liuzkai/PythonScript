import hou
import json


# Get Parm Dict
def getParmDict(node, txt_path):
    # get parms tuple
    parms = node.parms()
    jsondata = {}
    jsonparamdata = {}
    rootkey = node.name() + ".hda"
    for parm in parms:
        # export visiable parameters only
        if parm.isVisible():
            # get parmTemplate data
            key = parm.name()
            jsontmpdata = {}

            jsontmpdata["Label"] = parm.parmTemplate().label()
            jsontmpdata["Data Type"] = str(parm.parmTemplate().dataType())
            jsontmpdata["Help"] = parm.parmTemplate().help()
            jsontmpdata["Tags"] = parm.parmTemplate().tags()
            jsontmpdata["Value"] = parm.evalAsString()

            parmtype = parm.parmTemplate().type()
            jsontmpdata["Type"] = str(parmtype)

            if parmtype == hou.parmTemplateType.Int:
                jsontmpdata["Default Value"] = str(parm.parmTemplate().defaultValue())
                jsontmpdata["Min Value"] = str(parm.parmTemplate().minValue())
                jsontmpdata["Max Value"] = str(parm.parmTemplate().maxValue())

            if parmtype == hou.parmTemplateType.Float:
                jsontmpdata["Default Value"] = str(parm.parmTemplate().defaultValue())
                jsontmpdata["Min Value"] = str(parm.parmTemplate().minValue())
                jsontmpdata["Max Value"] = str(parm.parmTemplate().maxValue())

            if parmtype == hou.parmTemplateType.String:
                jsontmpdata["String Type"] = str(parm.parmTemplate().stringType())
                jsontmpdata["File Type"] = str(parm.parmTemplate().fileType())
                jsontmpdata["Menu Type"] = str(parm.parmTemplate().menuType())
                jsontmpdata["Menu Items"] = parm.parmTemplate().menuItems()
                jsontmpdata["Menu Labels"] = parm.parmTemplate().menuLabels()

            if parmtype == hou.parmTemplateType.Toggle:
                jsontmpdata["Default Value"] = str(parm.parmTemplate().defaultValue())

            if parmtype == hou.parmTemplateType.Menu:
                jsontmpdata["Menu Items"] = str(parm.parmTemplate().menuItems())
                jsontmpdata["Menu Labels"] = str(parm.parmTemplate().menuLabels())
                jsontmpdata["Default Value"] = str(parm.parmTemplate().defaultValue())
                jsontmpdata["Menu Type"] = str(parm.parmTemplate().menuType())

            if parmtype == hou.parmTemplateType.FolderSet:
                jsontmpdata["Fonder Names"] = str(parm.parmTemplate().folderNames())
                jsontmpdata["Fonder Type"] = str(parm.parmTemplate().folderType())
                jsontmpdata["Fonder Style"] = str(parm.parmTemplate().folderStyle())

            if parmtype == hou.parmTemplateType.Label:
                jsontmpdata["Column Labels"] = str(parm.parmTemplate().columnLabels())

            if parmtype == hou.parmTemplateType.Ramp:
                jsontmpdata["Default Value"] = str(parm.parmTemplate().defaultValue())
                jsontmpdata["Default Basis"] = str(parm.parmTemplate().defaultBasis())
                jsontmpdata["Parm Type"] = str(parm.parmTemplate().parmType())

            # for each param data
            jsonparamdata[str(key)] = jsontmpdata
        # for each .hda data
        jsondata[rootkey] = jsonparamdata

    with open(txt_path, 'w') as json_file:
        json.dump(jsondata, json_file)


self = hou.pwd()
node = self.parm("node").evalAsNode()
txt_path = self.parm("txt").evalAsString()

getParmDict(node, txt_path)