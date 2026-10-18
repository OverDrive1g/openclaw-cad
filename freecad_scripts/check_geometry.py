"""Проверка топологии B-rep. Запускать через FreeCAD MCP execute_code."""

import FreeCAD as App

DOC_NAME = ""
OBJ_NAME = ""

doc = App.getDocument(DOC_NAME) if DOC_NAME else App.ActiveDocument
obj = doc.getObject(OBJ_NAME) if OBJ_NAME else next(
    o for o in doc.Objects if hasattr(o, "Shape")
)
shape = obj.Shape

report = {
    "valid": shape.isValid(),
    "solids": len(shape.Solids),
    "shells": len(shape.Shells),
    "faces": len(shape.Faces),
    "is_closed": shape.isClosed() if hasattr(shape, "isClosed") else None,
}

if not report["valid"]:
    # Подробный вывод BRepCheck_Analyzer уходит в консоль FreeCAD
    try:
        shape.check(True)
    except Exception as exc:  # noqa: BLE001 - диагностика важнее типа
        report["check_error"] = str(exc)

print(report)
