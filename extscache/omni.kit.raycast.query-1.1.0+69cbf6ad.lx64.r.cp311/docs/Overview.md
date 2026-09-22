# Overview

An extension wraps around RTX Raycast Query to provide simpler raycast interface into the stage.

## Class List
- **IRaycastQuery**:  Interface class for Raycast Query operations. This class represents the interface for performing Raycast Query operations in the current scene. This class is thread-safe and can be called from any thread. There are several sets of functions to do raycast query:

    - **submit_raycast_query** as a single call that casts one Ray into the scene and returns hit result via callback.

    - The combination of **add_raycast_sequence**/**remove_raycast_sequence**, **submit_ray_to_raycast_sequence**, **get_latest_result_from_raycast_sequence** as a way to cast one ray into the scene and get result by polling.

    - The combination of **add_raycast_sequence**/**remove_raycast_sequence**, **submit_ray_to_raycast_sequence_array**, **get_latest_result_from_raycast_sequence_array** as a way to cast multiple rays into the scene and get result by polling.

- **Result**:  An enumeration class called "Result" which represents the possible error codes for a raycast query system. 

- **RayQueryResult**:  Alias of the struct rtx::raytracing::RaycastQueryResult, represents the result of a raycast query. Inclued whether this query is valid, the hit position, normal and so on.

- **Ray**:  Alias of the struct rtx::raytracing::RaycastQueryRay, defines a ray that is used as input for a raycast query.

## Example Usage
### Using `submit_raycast_query` for single raycast
```python
import omni.kit.raycast.query
from pxr import Gf

# assuming a stage is already opened and has geometry that the ray will hit
# ...

# get raycast interface
raycast = omni.kit.raycast.query.acquire_raycast_query_interface()

# generate a ray
ray = omni.kit.raycast.query.Ray((1000, 0, 0), (-1, 0, 0))

def callback(ray, result):
    if result.valid:
        # Got the raycast result in the callback
        print(Gf.Vec3d(*result.hit_position)
        print(result.hit_t)
        print(Gf.Vec3d(*result.normal))
        print(result.get_target_usd_path())

raycast.submit_raycast_query(ray, callback)
```

### Using `submit_ray_to_raycast_sequence/get_latest_result_from_raycast_sequence` for single raycast

- Setup raycast sequence
```python
import omni.kit.raycast.query
from pxr import Gf

# assuming a stage is already opened and has geometry that the ray will hit
# ...

# get raycast interface
raycast = omni.kit.raycast.query.acquire_raycast_query_interface()

# generate a ray
ray = omni.kit.raycast.query.Ray((1000, 0, 0), (-1, 0, 0))

seq_id = raycast.add_raycast_sequence()
result = raycast.submit_ray_to_raycast_sequence(seq_id, ray)
```
- Poll for result
```python
async def poll_for_result():
    while True:
        (error, seq_ray, result) = (
            raycast.get_latest_result_from_raycast_sequence(seq_id)
        )
        if error == omni.kit.raycast.query.Result.SUCCESS:
            if result.valid:
                # Got the raycast result in the callback
                print(Gf.Vec3d(*result.hit_position)
                print(result.hit_t)
                print(Gf.Vec3d(*result.normal))
                print(result.get_target_usd_path())
                break

        await self._app.next_update_async()

# You can also put get_latest_result_from_raycast_sequence in some `update` function that's ticked periodically without using async function.
```
- Remove raycast sequence
```
result = raycast.remove_raycast_sequence(seq_id)
```

### Using `submit_ray_to_raycast_sequence_array/get_latest_result_from_raycast_sequence_array` for multiple raycasts
- Setup raycast sequence array
```python
import omni.kit.raycast.query
from pxr import Gf

# assuming a stage is already opened and has geometry that the ray will hit
# ...

# get raycast interface
raycast = omni.kit.raycast.query.acquire_raycast_query_interface()

# generate ray array
ray1 = omni.kit.raycast.query.Ray(
    (-1, 0, -3), (0, 0, 1), 0, 4
)
ray2 = omni.kit.raycast.query.Ray(
    (-1, 0, 1), (1, 0, 0)
)
ray3 = omni.kit.raycast.query.Ray(
    (1, 0, 3), (-1, 0, 0)
)
ray4 = omni.kit.raycast.query.Ray(
    (1, 0, -1), (1, 0, 0)
)
ray_array = [ray1, ray2, ray3, ray4]

# Optional. The python API submit_ray_to_raycast_sequence_array will set the size automatically.
# In C++ API, the size needs to be set explicitly.
# result = raycast.set_raycast_sequence_array_size(seq_id, len(ray_array))

seq_id = raycast.add_raycast_sequence()
result = raycast.submit_ray_to_raycast_sequence_array(seq_id, ray_array)
```
- Poll for result
```python
async def poll_for_result():
    while True:
        (error, seq_rays, results) = (
            raycast.get_latest_result_from_raycast_sequence_array(seq_id)
        )
        if error == omni.kit.raycast.query.Result.SUCCESS:

            for i, ray in enumerate(ray_array):
                seq_ray = seq_rays[i]
                result = results[i]
                if result.valid:
                    # Got the raycast result in the callback
                    print(Gf.Vec3d(*result.hit_position)
                    print(result.hit_t)
                    print(Gf.Vec3d(*result.normal))
                    print(result.get_target_usd_path())

        # have some exit criteria to break the loop
        # break

        await self._app.next_update_async()

# You can also put get_latest_result_from_raycast_sequence in some `update` function that's ticked periodically without using async function.
```
- Remove raycast sequence
```
result = raycast.remove_raycast_sequence(seq_id)
```