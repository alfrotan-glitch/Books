"""Shared geometry helpers (no project imports)."""
import math

# regions printed at an angle (a postcard pasted on the page): page -> [(clip in pt, angle in degrees)].
# All stages work in the "straightened" frame for these regions: tesseract runs on the de-rotated crop, embedded
# words and image rules found inside the clip are rotated by the same angle about the clip centre.
ROTATED = {
    26: [((55, 105, 345, 335), -2.5), ((340, 175, 470, 250), -2.5)],
}


def rot_xy(x, y, clip, ang):
    """rotate point (x, y) [pt] about the centre of `clip` by `ang` degrees, using the same convention as
    cv2.getRotationMatrix2D / warpAffine (positive angle = counter-clockwise on the screen, y pointing down)."""
    cx = (clip[0] + clip[2]) / 2; cy = (clip[1] + clip[3]) / 2
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    dx, dy = x - cx, y - cy
    return cx + ca * dx + sa * dy, cy - sa * dx + ca * dy


def rot_box(b, clip, ang):
    """rotate a box dict (x0,y0,x1,y1) about the clip centre: the centre moves, width/height are kept."""
    xc, yc = rot_xy((b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2, clip, ang)
    w = b["x1"] - b["x0"]; h = b["y1"] - b["y0"]
    return dict(b, x0=round(xc - w / 2, 2), y0=round(yc - h / 2, 2), x1=round(xc + w / 2, 2), y1=round(yc + h / 2, 2))


def inside(b, clip):
    xc = (b["x0"] + b["x1"]) / 2; yc = (b["y0"] + b["y1"]) / 2
    return clip[0] <= xc <= clip[2] and clip[1] <= yc <= clip[3]
