"""Экспорт STEP/STL из выбранного объекта."""

import os

import FreeCAD as App
import Mesh
import Part

DOC_NAME = ""
OBJ_NAME = ""
OUT_DIR = "/path/to/out"
BASENAME = "part"

doc = App.getDocument(DOC_NAME) if DOC_NAME else App.ActiveDocument
obj = doc.getObject(OBJ_NAME) if OBJ_NAME else next(
    o for o in doc.Objects if hasattr(o, "Shape")
)

os.makedirs(OUT_DIR, exist_ok=True)
step_path = os.path.join(OUT_DIR, BASENAME + ".step")
stl_path = os.path.join(OUT_DIR, BASENAME + ".stl")

Part.export([obj], step_path)
Mesh.export([obj], stl_path)

print({
    "step": step_path,
    "step_bytes": os.path.getsize(step_path),
    "stl": stl_path,
    "stl_bytes": os.path.getsize(stl_path),
    "solids": len(obj.Shape.Solids),
    "valid": obj.Shape.isValid(),
})
