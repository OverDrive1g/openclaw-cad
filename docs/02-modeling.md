# 02. Моделирование

## 1. Что считается хорошим ТЗ

До генерации выясните и запишите:

- назначение детали: зачем, куда крепится, с чем взаимодействует;
- ключевые размеры и посадки (или «подобрать под стандартный крепёж»);
- материал и технологию: Q1 Pro / CNC 3018 / лазер / только CAD;
- нагрузки: вес, усилие, направление;
- ограничения: масса, время печати, цена, количество.

Если размер спорный — это вопрос до моделирования. Догадка, зашитая в геометрию,
дороже одного уточнения.

## 2. Каркас параметрической детали

Все размеры — переменные сверху. Никаких магических чисел в теле скрипта.

```python
import FreeCAD as App
import Part
from FreeCAD import Vector

# --- параметры ---------------------------------------------------------------
PLATE_W = 100.0      # мм
PLATE_D = 100.0      # мм
PLATE_H = 5.0        # мм
HOLE_D = 4.0         # мм
HOLE_OFFSET = 40.0   # мм от центра
CHAMFER_D = 7.0      # мм
CHAMFER_H = 1.0      # мм

DOC_NAME = "flange"
OUT_PATH = "/home/me/cad/flange/flange.fcstd"

# --- документ ----------------------------------------------------------------
doc = App.newDocument(DOC_NAME)

# --- базовая форма -----------------------------------------------------------
shape = Part.makeBox(PLATE_W, PLATE_D, PLATE_H)
shape.translate(Vector(-PLATE_W / 2, -PLATE_D / 2, 0))

# --- отверстия и фаски -------------------------------------------------------
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * HOLE_OFFSET, sy * HOLE_OFFSET

        hole = Part.makeCylinder(HOLE_D / 2, PLATE_H + 2)
        hole.translate(Vector(x, y, -1))
        shape = shape.cut(hole)

        cone = Part.makeCone(HOLE_D / 2, CHAMFER_D / 2, CHAMFER_H)
        cone.translate(Vector(x, y, PLATE_H - CHAMFER_H))
        shape = shape.cut(cone)

# --- объект и сохранение -----------------------------------------------------
obj = doc.addObject("Part::Feature", "Flange")
obj.Shape = shape
doc.recompute()
doc.saveAs(OUT_PATH)

print({"volume_mm3": round(shape.Volume, 2),
       "valid": shape.isValid(),
       "solids": len(shape.Solids)})
```

Полный рабочий пример — [examples/flange/flange.py](../examples/flange/flange.py).

## 3. Только Part API, только булевы операции

Проверенный набор:

- `Part.makeBox(w, d, h)` — плита;
- `Part.makeCylinder(r, h)` — отверстие, бобышка, стакан;
- `Part.makeCone(r1, r2, h)` — фаска, зенковка, конус;
- `shape.cut(other)` — вычитание;
- `shape.fuse(other)` — объединение;
- `shape.common(other)` — пересечение;
- `shape.translate(Vector(...))`, `shape.rotate(...)` — позиционирование.

Собирайте деталь как дерево: базовая форма, затем по одной операции. Так каждую
операцию можно проверить и откатить.

## 4. Правило мелких транзакций

**Один `execute_code` = 1–3 булевы операции.** После каждого этапа —
`doc.recompute()` и `doc.saveAs()`.

Почему: одна гигантская цепочка (кулачок с дуговым пазом в одном вызове)
убила FreeCAD по памяти на машине с 16 ГБ. Скрипты на десятки операций также
обрывают ответ MCP из-за лимита вывода. Сохранение после каждого этапа — это
страховка: при падении FreeCAD незаписанное исчезает.

Практический цикл:

```
execute_code (1–3 операции) → recompute → saveAs → скриншот/числа
повторить для следующего элемента
```

## 5. Проверенные идиомы FreeCAD 1.1.x

### Профильная призма

`Part.makePrism` **не существует** (AttributeError). Вместо него:

```python
pts = [Vector(0, 0, 0), Vector(10, 0, 0), Vector(10, 5, 0), Vector(0, 5, 0)]
wire = Part.makePolygon(pts + [pts[0]])
face = Part.Face(wire)
solid = face.extrude(Vector(0, 0, 8))
```

### Кольцевой сектор (дуговой паз, зуб)

```python
outer = Part.makeCylinder(r_out, h, Vector(0, 0, 0), Vector(0, 0, 1), angle)
inner = Part.makeCylinder(r_in, h, Vector(0, 0, 0), Vector(0, 0, 1), angle)
sector = outer.cut(inner)
sector.rotate(Vector(0, 0, 0), Vector(0, 0, 1), start_angle)
shape = shape.cut(sector)
```

### Точный наружный диаметр кольца

Тор даёт наружный диаметр `2 × (R + r)`, а не `2 × R`. Для точного диаметра
берите разность цилиндров:

```python
ring = Part.makeCylinder(25, 8).cut(Part.makeCylinder(17, 8))
# наружный Ø50, внутренний Ø34, высота 8
```

### Босс под вал

Не делайте цельный цилиндр-босс, если сквозь него проходит отверстие большего
диаметра: получите два несвязанных тела. Босс должен быть кольцом/стенкой вокруг
отверстия, либо отверстие не должно проходить сквозь босс.

```python
boss = Part.makeCylinder(outer_r, h).cut(Part.makeCylinder(bore_r, h + 2))
```

### Фаска/зенковка

`makeChamfer` на стенке отверстия ненадёжен. Рабочий идиом — вырезать конусом:

```python
cone = Part.makeCone(hole_r, chamfer_r, chamfer_h)
cone.translate(Vector(x, y, top_z - chamfer_h))
shape = shape.cut(cone)
```

### Объединение тел

`fuse` не склеивает тела, которые касаются ровно по границе. Нужен нахлёст
хотя бы 0.1–0.2 мм, иначе останутся два solids. После `fuse` проверяйте
`len(shape.Solids)`.

## 6. Сборка

Детали — отдельные документы. Сборка — это размещение деталей через
`Placement`/`Vector`, а не слияние всего в один solid.

- Посадки задаются зазором, а не «в ноль»: скользящая 0.2–0.4 мм, тугая 0.05 мм.
- Проверяйте пересечения: `shape.common(other).Volume` должен быть 0 для
  сопрягаемых деталей (кроме специальных натягов).
- После изменения одной детали пересоберите сборку и заново проверьте зазоры.

## 7. Именование и файлы

```
project/
  part_name/
    part_name.fcstd      # исходник, всегда
    part_name.step       # обмен/CAM
    part_name.stl        # печать
    preview.png          # скриншот
    README.md            # назначение, материал, технология
```

Одна деталь — один документ. Имя — по функции (`spring_housing`), а не `part1`.

## 8. Экспорт

- `.fcstd` — параметрический исходник, сохраняется всегда;
- `.step` — обмен и CAM;
- `.stl` — печать (производный файл);
- `.dxf`/`.svg` — лазер и 2D-контуры.

Готовые скрипты: [freecad_scripts/export.py](../freecad_scripts/export.py).

Дальше: [03-verification.md](03-verification.md).
