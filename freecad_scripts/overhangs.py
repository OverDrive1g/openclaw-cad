"""Смотрящие вниз грани и углы к горизонтали. Для DfAM на Q1 Pro."""

import math

import FreeCAD as App

DOC_NAME = ""
OBJ_NAME = ""
ANGLE_LIMIT_DEG = 45.0
BED_TOLERANCE_MM = 0.1

doc = App.getDocument(DOC_NAME) if DOC_NAME else App.ActiveDocument
obj = doc.getObject(OBJ_NAME) if OBJ_NAME else next(
    o for o in doc.Objects if hasattr(o, "Shape")
)
shape = obj.Shape
b = shape.BoundBox

findings = []
for face in shape.Faces:
    try:
        normal = face.normalAt(0.5, 0.5)
    except Exception:
        continue

    if normal.z >= -1e-6:
        continue  # грань не смотрит вниз

    # 0° = горизонтальный потолок (худший случай), 90° = вертикальная стенка
    angle_from_horizontal = 90.0 - math.degrees(math.asin(min(1.0, max(0.0, -normal.z))))

    center = face.CenterOfMass
    if center.z <= b.ZMin + BED_TOLERANCE_MM:
        continue  # лежит на столе, поддержка не нужна

    if angle_from_horizontal < ANGLE_LIMIT_DEG:
        findings.append({
            "loc_mm": [round(center.x, 2), round(center.y, 2), round(center.z, 2)],
            "angle_from_horizontal_deg": round(angle_from_horizontal, 1),
            "area_mm2": round(face.Area, 2),
        })

findings.sort(key=lambda item: -item["area_mm2"])

print({
    "object": obj.Name,
    "angle_limit_deg": ANGLE_LIMIT_DEG,
    "bbox_z_mm": [round(b.ZMin, 2), round(b.ZMax, 2)],
    "down_area_mm2": round(sum(item["area_mm2"] for item in findings), 2),
    "findings": findings[:12],
    "truncated": len(findings) > 12,
})
