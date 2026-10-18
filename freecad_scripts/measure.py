"""Факты о детали. Запускать через FreeCAD MCP execute_code."""

import FreeCAD as App

DOC_NAME = ""   # пусто = активный документ
OBJ_NAME = ""   # пусто = первый объект с Shape

doc = App.getDocument(DOC_NAME) if DOC_NAME else App.ActiveDocument
if doc is None:
    raise RuntimeError("Нет активного документа FreeCAD")

if OBJ_NAME:
    obj = doc.getObject(OBJ_NAME)
else:
    obj = next(o for o in doc.Objects if hasattr(o, "Shape"))

shape = obj.Shape
b = shape.BoundBox

facts = {
    "document": doc.Name,
    "object": obj.Name,
    "bbox_mm": [round(b.XLength, 3), round(b.YLength, 3), round(b.ZLength, 3)],
    "bbox_min": [round(b.XMin, 3), round(b.YMin, 3), round(b.ZMin, 3)],
    "bbox_max": [round(b.XMax, 3), round(b.YMax, 3), round(b.ZMax, 3)],
    "volume_mm3": round(shape.Volume, 3),
    "area_mm2": round(shape.Area, 3),
    "faces": len(shape.Faces),
    "edges": len(shape.Edges),
    "vertices": len(shape.Vertexes),
    "solids": len(shape.Solids),
    "shells": len(shape.Shells),
    "valid": shape.isValid(),
}
print(facts)
