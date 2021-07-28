##import math
import hou


def update_index(kwargs):
    index = int(kwargs['script_value0'])
    node = kwargs['node']
    parm = kwargs['parm']

    if 'noise' in parm.name():
        length_p = node.parm('length_n')
    else:
        length_p = node.parm('length_l')

    length = length_p.evalAsInt()

    if index == 0 or index <= length:
        length_p.set(index)
        return

    # get all parm templates names
    parent = node.parent().parent()
    parms = parm.multiParmInstances()

    template_count = len(parms) / index
    template_start = template_count * length
    parms_templates = parms[template_start:]

    # get the current index
    pre_index = node.digitsInName()

    # set parm expression
    for n, pt in enumerate(parms_templates):
        sourceparm_name = pt.name()

        if 'ramp' in sourceparm_name:
            # xferLinkParm(destparm, pt, True)
            print "pass"
            continue

        print pt.name()
        # n len
        index_now = int(math.ceil((n + 1) / float(template_count))) + length
        index_len = len(str(index_now))

        if 'noise_' in sourceparm_name:
            parm_name = "%s%d_%d%s" % (sourceparm_name[:-(index_len + 1)], pre_index, index_now, sourceparm_name[-1:])
        else:
            parm_name = "%s%d_%d" % (pt.name()[:-index_len], pre_index, index_now)

        destparm = parent.parm(parm_name)
        pt.set(destparm, None, True)
        print "%s : %s" % (pt.name(), destparm.name())

    length_p.set(index)


def recursive_output_nodes(node):
    result = []
    current = node
    output = node
    while output is not None:
        result.append(output)
        current = output
        try:
            output = current.outputs()[0]
        except Exception:
            output = None
    return result


def create_entity(kwargs):
    index = int(kwargs['script_value0'])
    node = kwargs['node']
    parm = kwargs['parm']
    group = int(kwargs['script_multiparm_index'])
    group_beigin = node.node('./Data_Group/Original')
    data_nodes = recursive_output_nodes(group_beigin)

    if len(data_nodes) - 2 < group :
        kwargs['parm'] = node.parm('data_group')
        kwargs['script_value0'] = str(node.parm('data_group').eval())
        create_data_entity(kwargs)
        data_nodes = recursive_output_nodes(group_beigin)

    group_node = data_nodes[group]

    isAttrib = 0 if 'noise_' in parm.name() else 1

    # Get the node net
    net = group_node.node('Attribute') if isAttrib == 1 else group_node.node('Noise')
    net_begin = net.node('Original')
    net_upper = net.node('Upper')
    net_end = net.node('output0')

    node_list = recursive_output_nodes(net_begin)[1:-1]
    node_num = len(node_list)

    # Syn node and parm
    if 0 <= index <= node_num:
        node_list.reverse()
        for i in range(node_num - index):
            node_list[i].destroy()

        net_end.setInput(0, node_list[node_num - index], 0) if index > 0 else net_end.setInput(0, net_begin, 0)
        return

    # create entity
    for i in range(index-node_num):
        new_entity = net.createNode('xpcg_mask_attribute_entity') if isAttrib == 1 else net.createNode(
            'xpcg_maskcombine_noise_entity')
        new_entity.setInput(0, net_begin, 0)
        senced_input = net_upper if len(node_list) == 0 else node_list[-1]
        new_entity.setInput(1, senced_input, 0)

        net_end.setInput(0, new_entity, 0)
        new_entity.moveToGoodPosition()

        # update node list
        node_list.append(new_entity)

        # group_index and entity_index
        group_index = group_node.digitsInName()
        entity_index = new_entity.digitsInName()

        # set parm
        entity_parms = new_entity.parms()

        for n, pt in enumerate(entity_parms):
            sourceparm_name = pt.name()

            if 'ramp' in sourceparm_name:
                ramp_str = "../../../../../ramp%d_%d" % (
                group_index, entity_index) if isAttrib == 1 else "../../../../../n_ramp%d_%d" % (group_index, entity_index)
                pt.set(ramp_str)
                continue

            if 'noise_' in sourceparm_name:
                parm_name = "%s%d_%d%s" % (sourceparm_name[:-1], group_index, entity_index, sourceparm_name[-1:])
            else:
                parm_name = "%s%d_%d" % (pt.name(), group_index, entity_index)

            destparm = node.parm(parm_name)
            pt.set(destparm, None, True)


def create_data_entity(kwargs):
    index = int(kwargs['script_value0'])
    node = kwargs['node']
    parm = kwargs['parm']
    isAttrib = 1

    # Get the node net
    net = node.node('Data_Group')
    net_begin = net.node('Original')
    net_upper = net.node('Upper')
    net_end = net.node('output0')
    parent = node.parent().parent()

    node_list = recursive_output_nodes(net_begin)[1:-1]
    node_num = len(node_list)

    # Syn node and parm
    if 0 <= index < node_num:
        node_list.reverse()
        for i in range(node_num - index):
            node_list[i].destroy()

        net_end.setInput(0, node_list[node_num - index], 0) if index > 0 else net_end.setInput(0, net_begin, 0)
        return

    # create entity
    for i in range(index-node_num):
        new_entity = net.createNode('xpcg_data_entity')
        new_entity.setInput(1, net_begin, 0)
        senced_input = net_upper if len(node_list) == 0 else node_list[-1]
        new_entity.setInput(0, senced_input, 0)
        net_end.setInput(0, new_entity, 0)
        new_entity.moveToGoodPosition()

        # update node list
        node_list.append(new_entity)


def sync_data(kwargs):
    mode = int(kwargs['script_value0'])
    if mode == 0:
        return

    node = kwargs['node']
    data = node.parm('data_group')
    kwargs['parm'] = data
    kwargs['script_value0'] = data.evalAsString()

    # check the based node:
    upper = node.node('./Data_Group/Upper')
    original = node.node('./Data_Group/Original')
    output = node.node('./Data_Group/output0')
    if upper is None or original is None or output is None:
        initial_data_group(node)

    create_data_entity(kwargs)

    for i in range(1, data.eval() + 1):
        attrib_name = "layer_group%d" % i
        noise_name = "noise_group%d" % i

        attrib_kwargs = {}
        attrib_kwargs['node'] = node
        attrib_kwargs['parm'] = node.parm(attrib_name)
        attrib_kwargs['script_value0'] = node.parm(attrib_name).evalAsString()
        attrib_kwargs['script_multiparm_index'] = str(i)

        noise_kwargs = {}
        noise_kwargs['node'] = node
        noise_kwargs['parm'] = node.parm(noise_name)
        noise_kwargs['script_value0'] = node.parm(noise_name).evalAsString()
        noise_kwargs['script_multiparm_index'] = str(i)

        create_entity(attrib_kwargs)
        create_entity(noise_kwargs)


def initial_data_group(node):
    data_group = node.node('./Data_Group')
    data_children = data_group.children()
    for node in data_children:
        node.destroy()
    upper = data_group.createNode('null', 'Upper')
    original = data_group.createNode('null', 'Original')
    output = data_group.createNode('output','output0')
    upper.setInput(0, data_group.indirectInputs()[0], 0)
    upper.moveToGoodPosition()
    original.setInput(0, data_group.indirectInputs()[0], 0)
    original.moveToGoodPosition()
    output.setInput(0, original)
    output.moveToGooDPosition()
