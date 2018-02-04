# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
# https://github.com/Korchy/1d_np

import bpy
from mathutils import Vector


class Np1d:
    __localenvironment = {
        'use_snap': True,
        'snap_element': 'VERTEX',
        'snap_target': 'ACTIVE',
        'pivot_point': 'MEDIAN_POINT',
        'transform_orientation': 'GLOBAL'
    }
    __environment = {}
    __anchorname = '1D_NP_Place'
    __cursor3d_location = None
    __anchor = None
    __anchoroffset = None
    __selection = []
    __selectionlocation = None
    __mode = []   # list: SELECT, TRANSLATE, NAVIGATE
    __replicationpoints = []

    @staticmethod
    def saveenvironment():
        __class__.__environment['use_snap'] = bpy.context.tool_settings.use_snap
        __class__.__environment['snap_element'] = bpy.context.tool_settings.snap_element
        __class__.__environment['snap_target'] = bpy.context.tool_settings.snap_target
        __class__.__environment['pivot_point'] = bpy.context.space_data.pivot_point
        __class__.__environment['transform_orientation'] = bpy.context.space_data.transform_orientation

    @staticmethod
    def setenvironment():
        if __class__.__environment:
            bpy.context.tool_settings.use_snap = __class__.__environment['use_snap']
            bpy.context.tool_settings.snap_element = __class__.__environment['snap_element']
            bpy.context.tool_settings.snap_target = __class__.__environment['snap_target']
            bpy.context.space_data.pivot_point = __class__.__environment['pivot_point']
            bpy.context.space_data.transform_orientation = __class__.__environment['transform_orientation']

    @staticmethod
    def setlocalenvironment():
        bpy.context.tool_settings.use_snap = __class__.__localenvironment['use_snap']
        bpy.context.tool_settings.snap_element = __class__.__localenvironment['snap_element']
        bpy.context.tool_settings.snap_target = __class__.__localenvironment['snap_target']
        bpy.context.space_data.pivot_point = __class__.__localenvironment['pivot_point']
        bpy.context.space_data.transform_orientation = __class__.__localenvironment['transform_orientation']

    @staticmethod
    def anchor():
        if __class__.__anchorname not in bpy.data.objects:
            bpy.ops.mesh.primitive_cube_add(enter_editmode=True)
            bpy.ops.mesh.select_all
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.object.mode_set(mode='OBJECT')
            __class__.__anchor = bpy.context.object
            __class__.__anchor.name = __class__.__anchorname
            __class__.__anchor.hide_render = True
        else:
            __class__.__anchor = bpy.data.objects[__class__.__anchorname]
        if __class__.__anchor.hide:
            __class__.__anchor.hide = False
        if not __class__.__anchor.layers[bpy.context.screen.scene.active_layer]:
            __class__.__anchor.layers[bpy.context.screen.scene.active_layer] = True
        return __class__.__anchor

    @staticmethod
    def anchortomousecursor():
        __class__.savecursor3dposition()
        bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')
        selections = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        __class__.anchor().select = True
        bpy.ops.view3d.snap_selected_to_cursor()
        for obj in selections:
            obj.select = True
        __class__.restorecursor3dposition()

    @staticmethod
    def removeanchor(type='SOFT'):
        anchor = __class__.anchor()
        if anchor and anchor.name == __class__.__anchorname:
            if type == 'SOFT':
                anchor.hide = True
            elif type == 'HARD':
                selections = bpy.context.selected_objects
                bpy.ops.object.select_all(action='DESELECT')
                anchor.select = True
                bpy.ops.object.delete('EXEC_DEFAULT')
                for obj in selections:
                    obj.select = True

    @staticmethod
    def savecursor3dposition():
        __class__.__cursor3d_location = list(bpy.context.area.spaces.active.cursor_location)

    @staticmethod
    def restorecursor3dposition():
        if __class__.__cursor3d_location:
            bpy.context.area.spaces.active.cursor_location = __class__.__cursor3d_location
            __class__.__cursor3d_location = None

    @staticmethod
    def saveanchorselectionoffset():
        # offset between selections and anchor
        anchor = __class__.anchor()
        __class__.__anchoroffset = anchor.location - __class__.__selectionlocation

    @staticmethod
    def saveselection():
        __class__.__selection = bpy.context.selected_objects[:]
        __class__.savecursor3dposition()
        bpy.ops.view3d.snap_cursor_to_selected()
        __class__.__selectionlocation = Vector(bpy.context.area.spaces.active.cursor_location)
        __class__.restorecursor3dposition()

    @staticmethod
    def restoreselection():
        bpy.ops.object.select_all(action='DESELECT')
        for obj in __class__.__selection:
            obj.select = True

    @staticmethod
    def selectiontoanchor():
        __class__.savecursor3dposition()
        anchor = __class__.anchor()
        bpy.context.area.spaces.active.cursor_location = list(anchor.location - __class__.__anchoroffset)
        anchor.select = False
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        anchor.select = True
        __class__.restorecursor3dposition()

    @staticmethod
    def selectiontostartlocation():
        __class__.savecursor3dposition()
        bpy.context.area.spaces.active.cursor_location = list(__class__.__selectionlocation)
        __class__.restoreselection()
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        __class__.restorecursor3dposition()

    @staticmethod
    def getmode(offset=0):
        return __class__.__mode[-1 + offset]

    @staticmethod
    def setmode(mode):
        __class__.__mode.append(mode)

    @staticmethod
    def addreplicationpoint(instance = False):
        __class__.__replicationpoints.append((__class__.anchor().location.copy(), instance))

    @staticmethod
    def replicateonpoints():
        __class__.savecursor3dposition()
        __class__.restoreselection()
        __class__.anchor().select = False
        for point in __class__.__replicationpoints:
            bpy.ops.object.duplicate(linked=point[1])
            bpy.context.area.spaces.active.cursor_location = point[0] - __class__.__anchoroffset
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        __class__.restoreselection()
        __class__.restorecursor3dposition()

    @staticmethod
    def clear():
        __class__.__mode = []
        __class__.setenvironment()
        __class__.anchor().select = False
        __class__.__replicationpoints = []


class Np1dCCCopy(bpy.types.Operator):
    bl_idname = 'np1d.cccopy'
    bl_label = 'NP_1D_CCCopy'
    bl_description = 'NP_1D_CCCopy'
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            if Np1d.getmode() == 'SELECT':
                Np1d.restoreselection()
                Np1d.anchor().select = True
                Np1d.saveanchorselectionoffset()
                Np1d.setmode('TRANSLATE')
                bpy.ops.transform.translate('INVOKE_DEFAULT')
            elif Np1d.getmode() == 'TRANSLATE':
                Np1d.addreplicationpoint(not event.alt)
                bpy.ops.transform.translate('INVOKE_DEFAULT')
        elif event.type in ('RET', 'NUMPAD_ENTER'):
            if Np1d.getmode() == 'SELECT':
                bpy.ops.transform.translate('INVOKE_DEFAULT')
            elif Np1d.getmode() == 'TRANSLATE':
                Np1d.selectiontostartlocation()
                Np1d.replicateonpoints()
                Np1d.clear()
                return {'FINISHED'}
        elif event.type == 'SPACE':
            if event.value == 'RELEASE':
                Np1d.setmode('NAVIGATE')
                Np1d.selectiontostartlocation()
                Np1d.setenvironment()
            elif event.value == 'PRESS':
                Np1d.setmode(Np1d.getmode(-1))
                Np1d.setlocalenvironment()
                Np1d.restoreselection()
                anchor = Np1d.anchor()
                anchor.select = True
                bpy.context.scene.objects.active = anchor
                Np1d.anchortomousecursor()
                Np1d.selectiontoanchor()
                bpy.ops.transform.translate('INVOKE_DEFAULT')
                return {'INTERFACE'}
        elif event.type == 'RIGHTMOUSE':
            if Np1d.getmode() != 'NAVIGATE':
                bpy.ops.transform.translate('INVOKE_DEFAULT')
        elif event.type == 'ESC':
            Np1d.selectiontostartlocation()
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        Np1d.saveenvironment()
        Np1d.saveselection()
        Np1d.setlocalenvironment()
        bpy.ops.object.select_all(action='DESELECT')
        Np1d.anchor().select = True
        Np1d.anchortomousecursor()
        Np1d.setmode('SELECT')
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        Np1d.clear()
        return None


class Np1dZZMove(bpy.types.Operator):
    bl_idname = 'np1d.zzmove'
    bl_label = 'NP_1D_ZZMove'
    bl_description = 'NP_1D_ZZMove'
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            if Np1d.getmode() == 'SELECT':
                Np1d.restoreselection()
                Np1d.anchor().select = True
                Np1d.saveanchorselectionoffset()
                Np1d.setmode('TRANSLATE')
                bpy.ops.transform.translate('INVOKE_DEFAULT')
            elif Np1d.getmode() == 'TRANSLATE':
                Np1d.clear()
                return {'FINISHED'}
        elif event.type in ('RET', 'NUMPAD_ENTER'):
            if Np1d.getmode() == 'SELECT':
                bpy.ops.transform.translate('INVOKE_DEFAULT')
            elif Np1d.getmode() == 'TRANSLATE':
                Np1d.clear()
                return {'FINISHED'}
        elif event.type == 'SPACE':
            if event.value == 'RELEASE':
                Np1d.setmode('NAVIGATE')
                Np1d.selectiontostartlocation()
                Np1d.setenvironment()
            elif event.value == 'PRESS':
                Np1d.setmode(Np1d.getmode(-1))
                Np1d.setlocalenvironment()
                Np1d.restoreselection()
                anchor = Np1d.anchor()
                anchor.select = True
                bpy.context.scene.objects.active = anchor
                Np1d.anchortomousecursor()
                Np1d.selectiontoanchor()
                bpy.ops.transform.translate('INVOKE_DEFAULT')
                return {'INTERFACE'}
        elif event.type == 'RIGHTMOUSE':
            if Np1d.getmode() != 'NAVIGATE':
                bpy.ops.transform.translate('INVOKE_DEFAULT')
        elif event.type == 'ESC':
            Np1d.selectiontostartlocation()
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        Np1d.saveenvironment()
        Np1d.saveselection()
        Np1d.setlocalenvironment()
        bpy.ops.object.select_all(action='DESELECT')
        Np1d.anchor().select = True
        Np1d.anchortomousecursor()
        Np1d.setmode('SELECT')
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        Np1d.clear()
        return None


def register():
    bpy.utils.register_class(Np1dZZMove)
    bpy.utils.register_class(Np1dCCCopy)


def unregister():
    bpy.utils.unregister_class(Np1dCCCopy)
    bpy.utils.unregister_class(Np1dZZMove)
