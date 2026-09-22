
import omni.kit.app
import omni.timeline

from pxr import Usd, UsdGeom, UsdSkel, Gf
import omni.usd
import omni.anim.graph.core as ag

import sys
import math

import carb
import carb.input as i
import omni.appwindow


class Character:

    def __init__(self):
        pass

    def on_update(self, character_name, dt):
        print("update")
        
global character
def main(args):
    global character
    if "character" not in globals():
        character = Character()

    if len(args)> 1:
        character.on_update(args[0], float(args[1]))
    else:
        character.on_update(args[0], 0.025)
    
if __name__ == "__main__":
   main(sys.argv[1:])