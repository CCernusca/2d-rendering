
"""
Utility module
Provides miscellaneous additional functionality
"""

import pygame as pg

def blit_aspect(target_surface: pg.Surface, source_surface: pg.Surface, 
                left_margin_percent: float = 0.05, top_margin_percent: float = 0.05, 
                right_margin_percent: float = 0.05, bottom_margin_percent: float = 0.05) -> None:
    """
    Blits a source_surface onto a target_surface while preserving its aspect ratio and 
    respecting margins defined as percentages of the target_surface size.

    :param target_surface: The surface to draw on.
    :param source_surface: The surface to be scaled and blitted.
    :param left_margin_percent: Margin on the left side as a percentage of target surface width.
    :param top_margin_percent: Margin on the top side as a percentage of target surface height.
    :param right_margin_percent: Margin on the right side as a percentage of target surface width.
    :param bottom_margin_percent: Margin on the bottom side as a percentage of target surface height.
    """
    # Calculate the margins in pixels
    width, height = target_surface.get_size()
    left_margin = int(width * left_margin_percent)
    top_margin = int(height * top_margin_percent)
    right_margin = int(width * right_margin_percent)
    bottom_margin = int(height * bottom_margin_percent)

    # Calculate the available area after applying margins
    available_width = width - left_margin - right_margin
    available_height = height - top_margin - bottom_margin

    # Get the original dimensions of the source surface
    src_width, src_height = source_surface.get_size()

    # Calculate the scaled dimensions preserving the aspect ratio
    scale_width = available_width
    scale_height = int(src_height * (available_width / src_width))

    if scale_height > available_height:
        scale_height = available_height
        scale_width = int(src_width * (available_height / src_height))

    # Scale the source surface
    scaled_surface = pg.transform.scale(source_surface, (scale_width, scale_height))

    # Calculate the position to center the scaled surface within the available area
    x_pos = left_margin + (available_width - scale_width) // 2
    y_pos = top_margin + (available_height - scale_height) // 2

    # Blit the scaled surface onto the target surface
    target_surface.blit(scaled_surface, (x_pos, y_pos))

