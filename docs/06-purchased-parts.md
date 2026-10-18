# 06. Готовые детали из step.parts

Когда в сборке есть покупные компоненты — винты, гайки, подшипники, моторы,
коннекторы, платы — не рисуйте упрощённый «конверт» сразу. Сначала поищите
готовый STEP в каталоге [step.parts](https://www.step.parts). Это дешевле, чем
ловить коллизии по габаритам заглушки.

API: `https://api.step.parts`, сайт: `https://www.step.parts`.

## Скрипт

В репозитории: [scripts/download_step_part.py](../scripts/download_step_part.py).
Чистая stdlib, без зависимостей.

Поиск:

```bash
python scripts/download_step_part.py "M3 socket head 12" --limit 5
python scripts/download_step_part.py "bearing 608zz"
python scripts/download_step_part.py "STS3215" --family feetech
```

Скачивание:

```bash
python scripts/download_step_part.py "M3 socket head 12" \
  --download --out-dir ./purchased
```

Скачивание по id:

```bash
python scripts/download_step_part.py \
  --id iso4762_socket_head_cap_screw_m3x12 \
  --download --out-dir ./purchased
```

Скрипт проверяет `sha256` из записи каталога, если он там есть, и печатает
JSON с путём, id, ссылками и подтверждением чексуммы.

## Фасеты и алиасы

- `q` — нечёткий поиск по токенам, стандартам, размерам;
- `category`, `family`, `standard`, `tag` — точные фильтры;
- модель может называться иначе: `STS3215` ↔ `ST3215` ↔ `3215`;
- если API ответил, но кандидатов нет — это промах каталога;
  сетевой сбой — **не** промах, повторите запрос.

## Импорт STEP в FreeCAD

Через MCP `execute_code`:

```python
import Part

Part.insert("/path/to/downloaded.step", "assembly")
doc = App.getDocument("assembly")
doc.recompute()
```

Или отдельным документом:

```python
import Import

Import.insert("/path/to/downloaded.step", "ImportedParts")
```

После импорта:

- проверьте габариты (`BoundBox`) — метры/дюймы против мм;
- поставьте деталь через `Placement`, не масштабируйте «на глаз»;
- проверьте коллизии с соседями (`common().Volume`);
- сохраните ссылку на id/страницу детали в README сборки.

## Если точного совпадения нет

1. Зафиксируйте промах: что искали, какие алиасы перебрали.
2. Возьмите ближайший типоразмер, если он допускает замену.
3. Иначе — документированная заглушка-конверт с явными размерами и пометкой
   `placeholder`. При первой возможности замените на реальный STEP.

## Что не делать

- Не выдумывать размеры покупной детали по картинке.
- Не считать, что `glb`/`png` совпадает с STEP по геометрии.
- Не терять `sha256`: если файл скачан вручную, проверьте его отдельно.

Дальше: [07-codex-delegation.md](07-codex-delegation.md).
