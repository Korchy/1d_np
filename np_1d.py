# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
# https://github.com/Korchy/1d_np

import bpy
from mathutils import Vector
import bmesh


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
    __cursor3d_location = []
    __anchor = None
    __anchoroffset = Vector((0,0,0))
    __selection = []
    __selectionlocation = Vector((0,0,0))
    __mode = []   # list: NONE, SELECT, TRANSLATE, NAVIGATE
    __replicationpoints = []
    __tempselection = []

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
    def savetempselection():
        if bpy.context.active_object.mode == 'OBJECT':
            __class__.__tempselection.append(bpy.context.selected_objects)
        elif bpy.context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
            __class__.__tempselection.append([vertex.index for vertex in bpy.context.active_object.data.vertices if vertex.select])
            bpy.ops.object.mode_set(mode='EDIT')

    @staticmethod
    def restoretempselection():
        __class__.deselect()
        tempselection = __class__.__tempselection.pop()
        if bpy.context.active_object.mode == 'OBJECT':
            for obj in tempselection:
                obj.select = True
        elif bpy.context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
            for vertexid in tempselection:
                bpy.context.active_object.data.vertices[vertexid].select = True
            bpy.ops.object.mode_set(mode='EDIT')

    @staticmethod
    def anchor():
        if bpy.context.active_object.mode == 'OBJECT':
            # anchor = object
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
        elif bpy.context.active_object.mode == 'EDIT':
            # anchor = vertex.id
            if __class__.__anchor is None or (not isinstance(__class__.__anchor, int)) or (isinstance(__class__.__anchor, int) and __class__.__anchor >= len(bpy.context.active_object.data.vertices)):
                bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
                v = bm.verts.new((0, 0, 0))
                bm.verts.index_update()
                __class__.__anchor = v.index
                bmesh.update_edit_mesh(bpy.context.active_object.data)
        return __class__.__anchor

    @staticmethod
    def selectanchor():
        if bpy.context.active_object.mode == 'OBJECT':
            __class__.anchor().select = True
        elif bpy.context.active_object.mode == 'EDIT':
            anchor = __class__.anchor()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.active_object.data.vertices[anchor].select = True
            bpy.ops.object.mode_set(mode='EDIT')
        __class__.activateanchor()

    @staticmethod
    def deselectanchor():
        if bpy.context.active_object.mode == 'OBJECT':
            __class__.anchor().select = False
        elif bpy.context.active_object.mode == 'EDIT':
            anchor = __class__.anchor()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.active_object.data.vertices[anchor].select = False
            bpy.ops.object.mode_set(mode='EDIT')

    @staticmethod
    def activateanchor():
        if bpy.context.active_object.mode == 'OBJECT':
            bpy.context.scene.objects.active = __class__.anchor()
        elif bpy.context.active_object.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
            bm.verts.ensure_lookup_table()
            bm.select_history.add(bm.verts[__class__.anchor()])

    @staticmethod
    def anchorlocation():
        if bpy.context.active_object.mode == 'OBJECT':
            return __class__.anchor().location
        elif bpy.context.active_object.mode == 'EDIT':
            __class__.savecursor3dposition()
            __class__.activateanchor()
            bpy.ops.view3d.snap_cursor_to_active()
            anchorlocation = bpy.context.area.spaces.active.cursor_location.copy()
            __class__.restorecursor3dposition()
            return anchorlocation

    @staticmethod
    def anchortomousecursor():
        __class__.savecursor3dposition()
        bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')
        __class__.savetempselection()
        __class__.deselect()
        __class__.selectanchor()
        bpy.ops.view3d.snap_selected_to_cursor()
        __class__.restoretempselection()
        __class__.restorecursor3dposition()

    @staticmethod
    def removeanchor():
        if __class__.__anchor is not None:
            __class__.deselectanchor()
            if bpy.context.active_object.mode == 'EDIT':
                __class__.savetempselection()
                __class__.deselect()
                __class__.selectanchor()
                bpy.ops.mesh.delete(type='VERT')
                __class__.__anchor = None
                __class__.restoretempselection()

    @staticmethod
    def savecursor3dposition():
        __class__.__cursor3d_location.append(bpy.context.area.spaces.active.cursor_location.copy())

    @staticmethod
    def restorecursor3dposition():
        if __class__.__cursor3d_location:
            bpy.context.area.spaces.active.cursor_location = __class__.__cursor3d_location.pop()

    @staticmethod
    def saveanchorselectionoffset():
        # offset between selections and anchor
        __class__.__anchoroffset = __class__.anchorlocation() - __class__.__selectionlocation

    @staticmethod
    def saveselection():
        if bpy.context.active_object.mode == 'OBJECT':
            __class__.__selection = bpy.context.selected_objects[:]
        elif bpy.context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
            __class__.__selection = [vertex.index for vertex in bpy.context.active_object.data.vertices if vertex.select]
            bpy.ops.object.mode_set(mode='EDIT')
        __class__.savecursor3dposition()
        bpy.ops.view3d.snap_cursor_to_selected()
        __class__.__selectionlocation = bpy.context.area.spaces.active.cursor_location.copy()
        __class__.restorecursor3dposition()

    @staticmethod
    def restoreselection():
        __class__.deselect()
        if bpy.context.active_object.mode == 'OBJECT':
            for obj in __class__.__selection:
                obj.select = True
        elif bpy.context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
            for vertexid in __class__.__selection:
                bpy.context.active_object.data.vertices[vertexid].select = True
            bpy.ops.object.mode_set(mode='EDIT')

    @staticmethod
    def deselect():
        if bpy.context.active_object.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
        elif bpy.context.active_object.mode == 'EDIT':
            bpy.ops.mesh.select_all(action='DESELECT')

    @staticmethod
    def selectiontoanchor():
        __class__.savecursor3dposition()
        bpy.context.area.spaces.active.cursor_location = __class__.anchorlocation() - __class__.__anchoroffset
        __class__.deselectanchor()
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        __class__.selectanchor()
        __class__.restorecursor3dposition()

    @staticmethod
    def selectiontostartlocation():
        if __class__.__selection:
            __class__.savecursor3dposition()
            bpy.context.area.spaces.active.cursor_location = __class__.__selectionlocation
            __class__.restoreselection()
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
            __class__.restorecursor3dposition()

    @staticmethod
    def getmode(offset=0):
        if __class__.__mode:
            index = -1 + offset if abs(-1 + offset) <= len(__class__.__mode) else -1
            return __class__.__mode[index]
        else:
            return 'NONE'

    @staticmethod
    def setmode(mode):
        __class__.__mode.append(mode)

    @staticmethod
    def addreplicationpoint(instance=False):
        __class__.__replicationpoints.append((__class__.anchorlocation().copy(), instance))

    @staticmethod
    def replicateonpoints():
        __class__.savecursor3dposition()
        __class__.restoreselection()
        __class__.deselectanchor()
        for point in __class__.__replicationpoints:
            if bpy.context.active_object.mode == 'OBJECT':
                bpy.ops.object.duplicate(linked=point[1])
                bpy.context.area.spaces.active.cursor_location = point[0] - __class__.__anchoroffset
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
            elif bpy.context.active_object.mode == 'EDIT':
                bpy.ops.mesh.duplicate()
                bpy.context.area.spaces.active.cursor_location = point[0] - __class__.__anchoroffset
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        __class__.restoreselection()
        __class__.restorecursor3dposition()

    @staticmethod
    def clear():
        __class__.__mode = []
        __class__.__selection = []
        __class__.__cursor3d_location = []
        __class__.setenvironment()
        __class__.__replicationpoints = []
        __class__.removeanchor()
        __class__.__anchoroffset = Vector((0,0,0))
        __class__.__selectionlocation = Vector((0,0,0))


class Np1dCCCopy(bpy.types.Operator):
    bl_idname = 'np1d.cccopy'
    bl_label = 'NP_1D_CCCopy'
    bl_description = 'NP_1D_CCCopy'
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if Np1d.getmode() == 'NONE':
            Np1d.setmode('SELECT')
            Np1d.selectanchor()
            bpy.ops.transform.translate('INVOKE_DEFAULT')
        if event.type == 'LEFTMOUSE':
            if Np1d.getmode() == 'SELECT':
                Np1d.restoreselection()
                Np1d.selectanchor()
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
                if Np1d.getmode() == 'TRANSLATE':
                    Np1d.selectiontostartlocation()
                Np1d.setenvironment()
                Np1d.setmode('NAVIGATE')
            elif event.value == 'PRESS':
                if Np1d.getmode() == 'NAVIGATE':
                    modetoreturn = Np1d.getmode(-1)
                    Np1d.setmode(modetoreturn)
                    Np1d.setlocalenvironment()
                    if modetoreturn == 'TRANSLATE':
                        Np1d.restoreselection()
                    Np1d.anchortomousecursor()
                    if modetoreturn == 'TRANSLATE':
                        Np1d.selectiontoanchor()
                    Np1d.activateanchor()
                    bpy.ops.transform.translate('INVOKE_DEFAULT')
                    return {'INTERFACE'}
        elif event.type == 'RIGHTMOUSE':
            if Np1d.getmode() != 'NAVIGATE':
                bpy.ops.transform.translate('INVOKE_DEFAULT')
        elif event.type == 'ESC':
            Np1d.selectiontostartlocation()
            Np1d.clear()
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        Np1d.saveenvironment()
        Np1d.saveselection()
        Np1d.setlocalenvironment()
        Np1d.deselect()
        Np1d.anchortomousecursor()
        Np1d.setmode('NONE')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        Np1d.clear()   7 8 9 10 11 12 13 14  
        return None


class Np1dZZMove(bpy.types.Operator):
    bl_idname = 'np1d.zzmove'
    bl_label = 'NP_1D_ZZMove'
    bl_description = 'NP_1D_ZZMove'
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if Np1d.getmode() == 'NONE':
            Np1d.setmode('SELECT')
            Np1d.selectanchor()
            bpy.ops.transform.translate('INVOKE_DEFAULT')
        if event.type == 'LEFTMOUSE':
            if Np1d.getmode() == 'SELECT':
                Np1d.restoreselection()
                Np1d.selectanchor()
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
                if Np1d.getmode() == 'TRANSLATE':
                    Np1d.selectiontostartlocation()
                Np1d.setenvironment()
                Np1d.setmode('NAVIGATE')
            elif event.value == 'PRESS':
                if Np1d.getmode() == 'NAVIGATE':
                    modetoreturn = Np1d.getmode(-1)
                    Np1d.setmode(modetoreturn)
                    Np1d.setlocalenvironment()
                    if modetoreturn == 'TRANSLATE':
                        Np1d.restoreselection()
                    Np1d.anchortomousecursor()
                    if modetoreturn == 'TRANSLATE':
                        Np1d.selectiontoanchor()
                    Np1d.activateanchor()
                    bpy.ops.transform.translate('INVOKE_DEFAULT')
                    return {'INTERFACE'}
        elif event.type == 'RIGHTMOUSE':
            if Np1d.getmode() != 'NAVIGATE':
                bpy.ops.transform.translate('INVOKE_DEFAULT')
        elif event.type == 'ESC':
            Np1d.selectiontostartlocation()
            Np1d.clear()
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        Np1d.saveenvironment()
        Np1d.saveselection()
        Np1d.setlocalenvironment()
        Np1d.deselect()
        Np1d.anchortomousecursor()
        Np1d.setmode('NONE')
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
