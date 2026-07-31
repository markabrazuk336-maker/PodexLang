# PodexLang

Свой язык, свой компилятор. Цель — **C++**, без чужих `#include` в исходниках PodexLang.

**License:** [MIT](LICENSE)

## Установщик (Windows)

```powershell
cd D:\Cursor_Projects\PodexLang
.\installer\build_installer.bat
```

Готовый файл: `dist\PodexLang-Setup-0.2.0.exe`

Установщик (Inno Setup 6):
- ставит Podex Studio + `podexc` + examples/stdlib
- иконка для `.pdx`
- ПКМ → **Open with Podex Studio** / **Edit with Podex Studio**
- ярлыки в меню Пуск (и опционально на рабочий стол)

Нужен установленный **Python 3** (для Studio). Для Build/Run программ — **g++** (MinGW).

### Если Windows блокирует установщик (SmartScreen)

Установщик без платной цифровой подписи — Windows пишет «защитила компьютер» / «приложение заблокировано».

1. В окне нажми **Подробнее** (More info)
2. Затем **Выполнить в любом случае** (Run anyway)

Или ПКМ по `PodexLang-Setup-0.2.0.exe` → **Свойства** → внизу галка **Разблокировать** → ОК → запусти снова.

## Идея

Вместо `#include` — директива модулей:

```podex
#profit <math>
#profit <io>
#profit "mylib"
```

Компилятор сам ищет модуль в stdlib и путях `-I`, и генерирует нужный C++.

## Podex Studio (IDE)

Приложение в духе Visual Studio: редактор, Solution Explorer, Build / Run, Output.

```powershell
cd D:\Cursor_Projects\PodexLang
.\PodexStudio.bat
```

Или:

```powershell
python studio\app.py
```

Горячие клавиши: `Ctrl+S` сохранить · `Ctrl+B` / `F7` сборка · `F5` запуск · `Ctrl+W` закрыть вкладку · `Ctrl+Shift+N` новый проект.

Вкладки, **Error List** (двойной клик → переход к строке), шаблон **New Project**.

## Быстрый старт (CLI)

```powershell
cmake -S . -B build
cmake --build build
.\build\Debug\podexc.exe examples\hello.pdx -o build\hello.cpp
# или Release:
# .\build\Release\podexc.exe ...
```

Дальше обычный C++ компилятор:

```powershell
cl /EHsc /std:c++17 build\hello.cpp /Fe:build\hello.exe
# или g++ / clang++
```

## Синтаксис (MVP)

```podex
#profit <io>
#profit <math>

fn add(a: int, b: int) -> int {
    return a + b
}

fn main() -> int {
    let x = 10
    let mut y = sqrt(16.0)
    print(add(x, 5))
    if y > 3.0 {
        print("ok")
    } else {
        print("no")
    }
    return 0
}
```

Ключевые слова: `fn`, `let`, `mut`, `if`, `else`, `while`, `for`, `in`, `return`, `break`, `continue`, `and`, `or`, `not`  
Типы: `int`, `float`, `bool`, `string`, `void`

### Новое (v2)

```podex
for i in 0..5 { }      # 0,1,2,3,4
for i in 1..=5 { }     # 1..5 включительно
for x in arr { }       # по массиву

let mut a = [10, 20, 30]
a[1] = 99
push(a, 40)
print(len(a))

if cond { break }
if cond { continue }
```

## Модули

| `#profit` | Что даёт |
|-----------|----------|
| `<math>`  | `sqrt`, `sin`, `cos`, `tan`, `pow`, `floor`, `ceil`, `abs` |
| `<io>`    | `print(...)` |
| `<str>`   | `len`, `to_string` |
| `"name"`  | файл `name.pdx` рядом с исходником / в `-I` / в `stdlib` |

Поиск: `stdlib/`, `-I`, папка исходника → `name.pdx` или `name/mod.pdx`.

## Структура

```
PodexLang/
  compiler/     # podexc — лексер, парсер, модули, codegen → C++
  stdlib/       # маркеры стандартных модулей
  examples/     # hello, math_demo, fib
```

## CLI

```
podexc [options] <file.pdx>
  -o <file>       выходной .cpp
  -I <dir>        путь поиска модулей
  --stdlib <dir>  путь к stdlib
```
