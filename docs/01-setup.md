# 01. Установка и подключение

Пайплайн работает, когда одновременно запущены три вещи:

1. **FreeCAD GUI** с открытым документом;
2. **Robust MCP Bridge** внутри FreeCAD — XML-RPC на `localhost:9875`;
3. **MCP-клиент** (OpenClaw или Codex), который запускает `freecad-mcp`.

Если хотя бы одного звена нет, первый же вызов вернёт `Connection refused`.
Проверяйте связь до начала моделирования — это дешевле, чем потерять раунд.

## 1. FreeCAD

Нужен **FreeCAD 1.1.x** (GUI). AppImage — нормальный вариант для Linux:
распаковать/сделать исполняемым и запускать с обычным `DISPLAY`.

```bash
chmod +x FreeCAD_1.1.4-Linux-x86_64-py311.AppImage
./FreeCAD_1.1.4-Linux-x86_64-py311.AppImage
```

Python внутри FreeCAD — 3.11; MCP-серверу нужен Python ≥ 3.11.

## 2. Аддон Robust MCP Bridge

Репозиторий: <https://github.com/spkane/freecad-addon-robust-mcp-server>

```bash
git clone https://github.com/spkane/freecad-addon-robust-mcp-server.git
```

Скопируйте каталог `freecad/RobustMCPBridge` в папку Mod вашего FreeCAD:

```bash
# Linux, FreeCAD 1.1.x
mkdir -p ~/.local/share/FreeCAD/v1-1/Mod
cp -r freecad-addon-robust-mcp-server/freecad/RobustMCPBridge \
      ~/.local/share/FreeCAD/v1-1/Mod/
```

Для других версий путь может быть `~/.local/share/FreeCAD/Mod/` — ориентируйтесь
на каталог, который FreeCAD реально создал у вас. На macOS:
`~/Library/Application Support/FreeCAD/Mod/`, на Windows: `%APPDATA%/FreeCAD/Mod/`.

Перезапустите FreeCAD. В списке верстаков появится **Robust MCP Bridge**.

### Запуск моста

1. Откройте FreeCAD.
2. Выберите верстак **Robust MCP Bridge**.
3. Нажмите **Start MCP Bridge**.
4. В консоли FreeCAD должно появиться `XML-RPC: localhost:9875`.

Для автозапуска включите **AutoStart** в настройках аддона: тогда мост
поднимается вместе с FreeCAD, и отдельный клик не нужен.

Проверка «мост жив»:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:9875
```

`501` — **нормальный** ответ: это XML-RPC-сервер, который не понимает GET.
`Connection refused` — мост не запущен.

## 3. MCP-сервер freecad-mcp

Два равнозначных варианта.

### Вариант A: из исходников через uv (рекомендуется для разработки)

```bash
git clone https://github.com/spkane/freecad-addon-robust-mcp-server.git
cd freecad-addon-robust-mcp-server
uv sync
uv run --project . freecad-mcp
```

MCP-клиент запускает сервер сам — вручную держать процесс не нужно.

### Вариант B: pip/pipx

```bash
pipx install freecad-robust-mcp
freecad-mcp
```

Проверьте, что `freecad-mcp` есть в `PATH` у того процесса, который запускает
MCP-клиент.

## 4. Конфиг OpenClaw

В `openclaw.json`:

```json
{
  "mcp": {
    "servers": {
      "freecad": {
        "command": "uv",
        "args": [
          "run",
          "--project",
          "/path/to/freecad-addon-robust-mcp-server",
          "freecad-mcp"
        ],
        "env": {
          "FREECAD_MODE": "xmlrpc"
        }
      }
    }
  }
}
```

Если установлено через pipx, вместо `uv`/`args`:

```json
{
  "mcp": {
    "servers": {
      "freecad": {
        "command": "freecad-mcp",
        "env": { "FREECAD_MODE": "xmlrpc" }
      }
    }
  }
}
```

После изменения конфига **перезапустите OpenClaw**: runtime держит снимок
MCP-серверов, новые тулы без рестарта не появятся.

## 5. Конфиг Codex CLI

Codex подхватывает проектный `.codex/config.toml` из рабочей директории:

```toml
[mcp_servers.freecad]
command = "uv"
args = ["run", "--project", "/path/to/freecad-addon-robust-mcp-server", "freecad-mcp"]

[mcp_servers.freecad.env]
FREECAD_MODE = "xmlrpc"
```

Для не-git каталога добавьте флаг `--skip-git-repo-check` при запуске.
MCP-тулы требуют approval, поэтому вместо `-s` используйте
`--approve-for-me` (см. [07-codex-delegation.md](07-codex-delegation.md)).

## 6. Смоук-тест

Первый вызов в любой сессии — проверка статуса:

```
get_connection_status
```

Ожидаемо: `connected`, режим `xmlrpc`. Дальше можно вызывать `execute_code`.

Минимальный тест геометрии:

```python
import FreeCAD as App
import Part

doc = App.newDocument("smoke")
box = Part.makeBox(10, 10, 10)
obj = doc.addObject("Part::Feature", "Box")
obj.Shape = box
doc.recompute()
print({"volume": box.Volume, "valid": box.isValid()})
```

Ожидаемо: `volume = 1000.0`, `valid = True`. Документ `smoke` потом закройте
без сохранения.

## 7. Безопасность

Мост слушает `localhost` и не имеет аутентификации. Не выставляйте порт 9875
наружу и не запускайте FreeCAD с мостом на машине, к которой есть недоверенный
доступ. Это локальный инструмент, а не сетевой сервис.

## Частые проблемы

| Симптом | Причина | Решение |
|---|---|---|
| `Connection refused` | FreeCAD закрыт или мост не стартовал | Открыть FreeCAD → Start MCP Bridge |
| Тулы FreeCAD не появились | клиент не перезапущен после правки конфига | Перезапустить OpenClaw/Codex |
| `no Qt platform plugin could be initialized` | попытка поднять GUI из фонового процесса | Запускать FreeCAD руками, с обычным `DISPLAY` |
| `freecad-mcp: command not found` | pipx/venv не в `PATH` клиента | Указать абсолютный путь или использовать `uv --project` |

Дальше: [02-modeling.md](02-modeling.md).
