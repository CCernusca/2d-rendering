
"""
Graphics module
Deals with graphical representation of geometry, including cameras
"""

try:
    import scripts.geometry as geometry
except ModuleNotFoundError:
    import geometry

# Dictionary of colors for groups, indexed by group index
group_colors = {}

def color_group(group_index: int|geometry.GeoGroup, color: tuple[int, int, int, int]) -> None:
    """
    Sets the color of a group.

    Args:
        group_index (int|geometry.GeoGroup): The index of the group or the group object.
        color (tuple[int, int, int, int]): The RGBA color to set.
    """
    if type(group_index) == geometry.GeoGroup:
        group_index = geometry.groups.index(group_index)
    group_colors[group_index] = (color[0], color[1], color[2], color[3])

def uncolor_group(group_index: int|geometry.GeoGroup) -> None:
    """
    Removes the color of a group.

    Args:
        group_index (int|geometry.GeoGroup): The index of the group or the group object.
    """
    if type(group_index) == geometry.GeoGroup:
        group_index = geometry.groups.index(group_index)
    if group_index in group_colors:
        del group_colors[group_index]

def get_uncolored() -> list[int]:
    """
    Returns a list of indices of uncolored groups.

    Returns:
        list[int]: A list of indices of uncolored groups.
    """
    return [i for i in range(len(geometry.groups)) if i not in group_colors]

if __name__ == "__main__":
    geometry.GeoGroup(0, 0, geometry.GeoCircle(0, 0, 1))
    print(get_uncolored(), group_colors)
    color_group(0, (255, 0, 0, 255))
    print(get_uncolored(), group_colors)
    uncolor_group(0)
    print(get_uncolored(), group_colors)
