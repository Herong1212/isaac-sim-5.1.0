import os

from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../../plugins')
audioSchemaPath = pluginsRoot + '/omniAudioSchema/resources'

Plug.Registry().RegisterPlugins(audioSchemaPath)

from .prim_lists import get_audio_prim_list
