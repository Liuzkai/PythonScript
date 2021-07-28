"""
State:          Interactive Script
State type:     interactive_Script
Description:    Interactive Script
Author:         zhongkailiu
Date Created:   December 10, 2020 - 19:20:15
"""

import hou
import viewerstate.utils as su


class State(object):
    MSG = "hold shift to change the parm"

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer

    def onEnter(self, kwargs):
        """ Called on node bound states when it starts
        """
        node = kwargs["node"]
        state_parms = kwargs["state_parms"]

        # print kwargs in the viewer state console if "Debug log" is
        # enabled
        self.log("onEnter=", kwargs)

        # viewport
        self.scene_viewer.set

    def onMouseEvent(self, kwargs):
        """ Process mouse events
        """
        ui_event = kwargs["ui_event"]
        dev = ui_event.device()
        self.log("Mouse:", dev.mouseX(), dev.mouseY(), dev.isLeftButton())

        # Must return True to consume the event
        return False

    def onKeyTransitEvent(self, kwargs):
        """ Called for processing a transitory key event
        """
        ui_event = kwargs["ui_event"]
        state_parms = kwargs["state_parms"]

        # Must returns True to consume the event
        return False


def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state
        template to register. """

    state_typename = kwargs["type"].definition().sections()["DefaultState"].contents()
    state_label = "Interactive Script"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon(kwargs["type"].icon())

    return template
