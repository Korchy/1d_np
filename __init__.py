# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
# https://github.com/Korchy/1d_np


bl_info = {
    'name': '1D_NP',
    'category': 'Mesh',
    'author': 'Nikita Akimov',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': '3DView window - T-panel - 1D',
    'wiki_url': '',
    'tracker_url': '',
    'description': 'Mesh tools'
}

from . import np_1d
from . import np_1d_panel


def register():
    np_1d.register()
    np_1d_panel.register()


def unregister():
    np_1d.unregister()
    np_1d_panel.unregister()


if __name__ == '__main__':
    register()
