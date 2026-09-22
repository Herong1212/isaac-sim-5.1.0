import omni.usd
import carb
from omni.metropolis.utils.mono_b_script_util import MonoBScript

# import omni
from pxr import Gf
import math


class SpillAnimator(MonoBScript):
    def __init__(self, prim_path, target_size: float = 1.0, leak_duration: float = 5.0):
        super().__init__(prim_path)
        self.target_size = target_size
        self.leak_duration = leak_duration
        self.leak_duration_counter = 0.0

        self.current_size = Gf.Vec3f(0.0, 0.0, 0.0)
        self.animation_duration = leak_duration  # Duration in seconds
        self.animation_time = 0.0
        self.is_active = False
        print(f"Initialized {self.prim_path}")

    def on_initialize(self):
        pass

    def on_destroy(self):
        pass

    def reset(self):
        self.is_active = False
        self.animation_time = 0.0
        self.current_size = Gf.Vec3f(0.0, 0.0, 0.0)
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(self.prim_path)
        carb.log_info(f"Trying to reset {self.prim_path} to {self.current_size}")
        if not prim:
            return
        carb.log_info(f"Resetting {self.prim_path} to {self.current_size}")
        prim.GetAttribute("xformOp:scale").Set(self.current_size)

    def activate(self):
        self.is_active = True
        self.animation_time = 0.0
        self.current_size = Gf.Vec3f(0.0, 0.0, 0.0)

    @staticmethod
    def ease_out_expo(t):
        return -math.pow(2, -10 * t) + 1

    def on_update(self):
        if not self.is_active:
            return
        # # Update animation time
        # print(f"Playing {self.prim_path}")
        if self.animation_time < self.animation_duration:
            self.animation_time += 1.0 / self._timeline.get_ticks_per_second()

            # Calculate interpolation factor (0 to 1)
            current_time = self.animation_time / self.animation_duration
            t = min(self.ease_out_expo(current_time), 1.0)

            self.current_size = t * self.target_size * Gf.Vec3f(1, 1, 1)

            # x, y, z = self.current_size[0], self.current_size[1], self.current_size[2]
            # # print(f"Resizing {self.prim_path} to {x}, {y}, {z}")
            # with rep.get.prim_at_path(self.prim_path):
            #     rep.modify.pose(size=(x, y, z))

            stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(self.prim_path)
            if not prim:
                return
            prim.GetAttribute("xformOp:scale").Set(self.current_size)
