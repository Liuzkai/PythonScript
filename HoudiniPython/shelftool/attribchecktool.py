import hou


class AttribCheckTool:
    """
        Document:
        If the number of selected node is only one, and the node type is merge, then do merge attribute check mode( mode one ).
        If the number of selected node is two, then compare both node, and create an attribute delete node to the first node( mode two ).
        If the number of selected node is more than two, just report the result as node comments( mode three ).
    """
    def __init__(self, selection):
        if len(selection) == 1 and selection[0].type().name() == 'merge':
            self.mode = 1 # merge mode
        elif len(selection) == 2 :
            self.mode = 2 # compare mode
        else:
            self.mode = 3 # comment mode
        self._selection = selection

    def execTool(self):
        if self.mode == 1:
            self.mergeNodeCheck(self._selection[0])
        elif self.mode == 2:
            self.deleteAttributeChanges(self._selection)
        else:
            for sl in self._selection:
                msg = self.checkAttributeChanges(sl)
                sl.setComment(msg)
                sl.setGenericFlag(hou.nodeFlag.DisplayComment, 1)

    def cmpattrib(self, a, b, name):
        out = ""
        if set(a) != set(b):
            out += name + " :"
            for s in set(a).difference(b):
                out += " +{};".format(s)
            for s in set(b).difference(a):
                out += " -{};".format(s)
            out += "\n"
        return out

    def checkAttributeChanges(self, node):
        if node is None or node.inputs()[0] is None:
            return hou.NodeError()

        geo = node.geometry()
        pta = [a.name() for a in geo.pointAttribs()]
        pra = [a.name() for a in geo.primAttribs()]
        va = [a.name() for a in geo.vertexAttribs()]
        ga = [a.name() for a in geo.globalAttribs()]

        geo2 = node.inputs()[0].geometry()
        pta2 = [a.name() for a in geo2.pointAttribs()]
        pra2 = [a.name() for a in geo2.primAttribs()]
        va2 = [a.name() for a in geo2.vertexAttribs()]
        ga2 = [a.name() for a in geo2.globalAttribs()]

        Com = node.comment()
        end = "--end--\n"
        if len(Com) > 0:
            pos = Com.find("--end--")
            if pos > -1:
                end = Com[pos:]
            else:
                end += Com

        Com = self.cmpattrib(pta, pta2, "point")
        Com += self.cmpattrib(pra, pra2, "prim")
        Com += self.cmpattrib(va, va2, "vertex")
        Com += self.cmpattrib(ga, ga2, "detail")
        if len(Com) == 0:
            Com = 'no different\n'
        Com += end

        return Com

    def deleteAttributeChanges(self, nodes):
        node_now = nodes[0] # current node
        node_tgt = nodes[1] # target node

        geo = node_now.geometry()
        pta = [a.name() for a in geo.pointAttribs()]
        pra = [a.name() for a in geo.primAttribs()]
        va = [a.name() for a in geo.vertexAttribs()]
        ga = [a.name() for a in geo.globalAttribs()]

        geo2 = node_tgt.geometry()
        pta2 = [a.name() for a in geo2.pointAttribs()]
        pra2 = [a.name() for a in geo2.primAttribs()]
        va2 = [a.name() for a in geo2.vertexAttribs()]
        ga2 = [a.name() for a in geo2.globalAttribs()]

        ptd = self.getChanges(pta, pta2)
        vad = self.getChanges(va, va2)
        prd = self.getChanges(pra, pra2)
        gad = self.getChanges(ga, ga2)

        if any(ptd + vad + prd + gad):
            parent = node_now.parent()
            node_ad = parent.createNode('attribdelete', "Attribute_Clean")
            node_ad.parm("ptdel").set(ptd)
            node_ad.parm("vtxdel").set(vad)
            node_ad.parm("primdel").set(prd)
            node_ad.parm("dtldel").set(gad)
            node_ad.setFirstInput(node_now)
            node_ad.moveToGoodPosition(True, False, False, False)

    def getChanges(self, a, b):
        out = ""
        if set(a) != set(b):
            for s in set(a).difference(b):
                out += "{} ".format(s)

        return out

    def getNodeAttribs(self, node):
        geo = node.geometry()
        pta = [a.name() for a in geo.pointAttribs()]
        va = [a.name() for a in geo.vertexAttribs()]
        pra = [a.name() for a in geo.primAttribs()]
        ga = [a.name() for a in geo.globalAttribs()]
        return pta, va, pra, ga

    def getInterList(self, nodes):
        nas = []
        for node in nodes:
            pta, va, pra, ga = self.getNodeAttribs(node)
            na = pta + va + pra + ga
            nas.append(na)
        i = 0
        result = set(nas[i])
        while i < (len(nas) - 1):
            i += 1
            result = set(result).intersection(set(nas[i]))
        return list(result)

    def mergeNodeCheck(self, node):
        """
        node is considered as merge node by default
        """
        nodes = node.inputs()
        attribs = self.getInterList(nodes)
        nas = []
        for index, innode in enumerate(nodes):
            pta, va, pra, ga = self.getNodeAttribs(innode)
            ptd = self.getChanges(pta,  attribs)
            vad = self.getChanges(va,   attribs)
            prd = self.getChanges(pra,  attribs)
            gad = self.getChanges(ga,   attribs)
            if any(ptd + vad + prd + gad):
                parent = innode.parent()
                node_ad = parent.createNode('attribdelete')
                node_ad.parm("ptdel").set(ptd)
                node_ad.parm("vtxdel").set(vad)
                node_ad.parm("primdel").set(prd)
                node_ad.parm("dtldel").set(gad)
                node_ad.setFirstInput(innode)
                node_ad.moveToGoodPosition(True, False, False, False)
                node.setInput(index, node_ad)


# Run Script!
sls = hou.selectedNodes()
attribtool = AttribCheckTool(sls)
attribtool.execTool()