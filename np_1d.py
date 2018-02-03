# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
# https://github.com/Korchy/1d_np

import bpy


class Np1d(bpy.types.Operator):
    bl_idname = 'np1d.np1d'
    bl_label = 'NP_1D'
    bl_description = 'NP_1D'

    status = None

    def modal(self, context, event):
        if self.status:
            return {'PASS_THROUGH'}
        else:
            return {'FINISHED'}

    def execute(self, context):
        if self.status:
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        return None


def register():
    bpy.utils.register_class(Np1d)


def unregister():
    bpy.utils.unregister_class(Np1d)
