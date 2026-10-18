"""Фланец 100×100×5 с 4 отверстиями Ø4 и зенковкой Ø7×1.

Запуск:
  freecadcmd examples/flange/flange.py
или через FreeCAD MCP execute_code.
"""

import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector

# --- параметры ---------------------------------------------------------------
PLATE_W = 100.0
PLATE_D = 100.0
PLATE_H = 5.0
HOLE_D = 4.0
HOLE_OFFSET = 40.0
CHAMFER_D = 7.0
CHAMFER_H = 1.0

DOC_NAME = "flange"
OBJ_NAME = "Flange"

try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    HERE = os.getcwd()
OUT_PATH = os.path.join(HERE, "flange.fcstd")

# --- документ ----------------------------------------------------------------
doc = App.newDocument(DOC_NAME)

shape = Part.makeBox(PLATE_W, PLATE_D, PLATE_H)
shape.translate(Vector(-PLATE_W / 2, -PLATE_D / 2, 0))

hole_r = HOLE_D / 2
chamfer_r = CHAMFER_D / 2

for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * HOLE_OFFSET, sy * HOLE_OFFSET

        hole = Part.makeCylinder(hole_r, PLATE_H + 2)
        hole.translate(Vector(x, y, -1))
        shape = shape.cut(hole)

        # Конус шире сверху: r1 внизу, r2 вверху
        cone = Part.makeCone(hole_r, chamfer_r, CHAMFER_H)
        cone.translate(Vector(x, y, PLATE_H - CHAMFER_H))
        shape = shape.cut(cone)

obj = doc.addObject("Part::Feature", OBJ_NAME)
obj.Shape = shape
doc.recompute()
doc.saveAs(OUT_PATH)

# --- аналитическая проверка --------------------------------------------------
plate_v = PLATE_W * PLATE_D * PLATE_H
hole_v = math.pi * hole_r**2 * PLATE_H
cone_v = math.pi * CHAMFER_H / 3 * (
    hole_r**2 + hole_r * chamfer_r + chamfer_r**2
)
cylinder_inside_cone_v = math.pi * hole_r**2 * CHAMFER_H
expected_v = plate_v - 4 * hole_v - 4 * (cone_v - cylinder_inside_cone_v)

b = shape.BoundBox
print({
    "path": OUT_PATH,
    "bbox_mm": [round(b.XLength, 3), round(b.YLength, 3), round(b.ZLength, 3)],
    "volume_mm3": round(shape.Volume, 3),
    "expected_volume_mm3": round(expected_v, 3),
    "volume_error_pct": round(abs(shape.Volume - expected_v) / expected_v * 100, 4),
    "solids": len(shape.Solids),
    "valid": shape.isValid(),
})
