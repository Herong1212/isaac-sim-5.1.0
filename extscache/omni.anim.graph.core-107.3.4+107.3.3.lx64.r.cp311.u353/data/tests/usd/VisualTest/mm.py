import sys
import carb

import omni.anim.graph.core as ag

def scale(vector, factor):
    return carb.Float3(vector.x * factor, vector.y * factor, vector.z * factor)

class Character:

    def on_update(self, character_name):

        # Retrieve character instance
        c = ag.get_character(character_name)

        # Set control variables in animation graph
        movementDirection = carb.Float3(-0.707107, 0, 0.707107)
        forwardDirection = movementDirection
        c.set_variable("MovementDirection", scale(movementDirection, 250.0))
        c.set_variable("ForwardDirection", forwardDirection)


global character
def main(args):
    global character
    if "character" not in globals():
        character = Character()

    character.on_update(args[0])

if __name__ == "__main__":
   main(sys.argv[1:])
