import carb
from pxr import Usd, Gf
from shapely.geometry import LineString
from typing import List, Optional, Union


def _get_looped_time(timecode: float, max_time: float) -> float:
    """
    Calculate the actual time considering looping and bounds.

    Args:
        timecode: The timecode to be looped
        max_time: The maximum time in the timesamples

    Returns: The actual time
    """
    if max_time <= 0:
        return timecode
    return timecode % max_time


def _interpolate_attribute(attr: Usd.Attribute, timecode: float) -> Optional[Union[Gf.Vec3d, Gf.Quatd, Gf.Quatf]]:
    """Get interpolated attribute value at a specific timecode.

    Args:
        attr: The USD attribute to be interpolated
        timecode: The timecode to be interpolated

    Returns: The interpolated attribute value
    """
    time_samples = attr.GetTimeSamples()
    if not time_samples:
        return attr.Get()

    # Get bracketing samples
    lower_time, upper_time = attr.GetBracketingTimeSamples(timecode)
    if lower_time == upper_time:
        return attr.Get(lower_time)

    # Interpolate between samples
    lower_value = attr.Get(lower_time)
    upper_value = attr.Get(upper_time)
    blend_factor = (timecode - lower_time) / (upper_time - lower_time)

    # Use Slerp for quaternions (orientation), Lerp for others (translation)
    if isinstance(lower_value, (Gf.Quatd, Gf.Quatf)):
        return Gf.Slerp(blend_factor, lower_value, upper_value)
    else:
        return Gf.Lerp(blend_factor, lower_value, upper_value)


def _get_attribute_value(
    prim: Usd.Prim, attr_name: str, timecode: float, loop: bool
) -> Optional[Union[Gf.Vec3d, Gf.Quatd, Gf.Quatf]]:
    """Get interpolated attribute value with error handling.

    Args:
        prim: The USD prim to get the attribute from
        attr_name: The name of the attribute to get
        timecode: The timecode to be interpolated
        loop: Whether to loop the animation when timecode exceeds max time

    Returns: The interpolated attribute value
    """
    attr = prim.GetAttribute(attr_name)
    if not attr:
        carb.log_error(f"Attribute '{attr_name}' not found on prim {prim.GetPath()}")
        return None

    # Return the attribute value if there are no time samples
    time_samples = attr.GetTimeSamples()
    if not time_samples:
        return attr.Get()
    if loop:
        actual_time = _get_looped_time(timecode, max(time_samples))
    else:
        actual_time = min(timecode, max(time_samples))
    return _interpolate_attribute(attr, actual_time)


def get_translate_with_timecode(source_prim: Usd.Prim, timecode: float, loop: bool = True) -> Optional[Gf.Vec3d]:
    """Get interpolated translation value.

    Args:
        source_prim: The USD prim to get the translation from
        timecode: The timecode to be interpolated
        loop: Whether to loop the animation when timecode exceeds max time

    Returns: The interpolated translation value
    """
    return _get_attribute_value(source_prim, "xformOp:translate", timecode, loop)


def get_orient_with_timecode(
    source_prim: Usd.Prim, timecode: float, loop: bool = True
) -> Optional[Union[Gf.Quatd, Gf.Quatf]]:
    """Get interpolated orientation value.

    Args:
        source_prim: The USD prim to get the orientation from
        timecode: The timecode to be interpolated
        loop: Whether to loop the animation when timecode exceeds max time

    Returns: The interpolated orientation value
    """
    return _get_attribute_value(source_prim, "xformOp:orient", timecode, loop)


def simplify_3d_points(points: List[carb.Float3], tolerance: float) -> List[carb.Float3]:
    """
    Reduce the complexity of a polyline induced by a list of 3D points with respect to a given tolerance.

    No new points are introduced; only a subsequence of points is produced as a simplification. The resulting
    simplified polyline has the property that any point on it is at most "tolerance" away from the original
    polyline. Only interior points are candidates for removal.
    for removal.

    CAVEAT: The current implementation does this by projecting the polyline onto the z=0 plane, simplying the
    2D polyline, and then lifting it back to the original dimension. Thus, variations in the z-coordinate are not
    considered -- TODO (METROPERF-872): pathpoints simplification should support Z axis

    Args:
        points: List of 3D points to simplify
        tolerance: Maximum distance between the input and output polyline to be ensured

    Returns:
        Simplified list of 3D points
    """
    points_2d = [(p.x, p.y) for p in points]  # WARNING: shapely expects 2D points. Ignore z coordinate.

    line_2d = LineString(points_2d)

    simplified_line_2d = line_2d.simplify(tolerance, preserve_topology=False)

    simplified_points_2d = list(simplified_line_2d.coords)

    simplified_points_3d = []
    # Put the z coordinate back because the resulting points are from among the original points
    # Not a fast way to do this but optimize only if needed
    # TODO (METROPERF-872): pathpoints simplification should support Z axis
    i = 0
    j = 0

    def near_equal(a, b, epsilon=1e-6):
        return abs(a - b) <= epsilon

    while i < len(simplified_points_2d) and j < len(points):
        if near_equal(simplified_points_2d[i][0], points[j].x) and near_equal(simplified_points_2d[i][1], points[j].y):
            simplified_points_3d.append(points[j])
            i += 1
        j += 1

    return simplified_points_3d
