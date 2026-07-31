# Third-party dependencies for PodexLang graphics modules

## raylib (canvas + orbit)

Expected layout:

```
third_party/raylib/
  include/raylib.h
  lib/libraylib.a
  lib/raylib.dll
```

Windows MinGW package (used by this repo):
https://github.com/raysan5/raylib/releases/download/5.5/raylib-5.5_win64_mingw-w64.zip

Extract and either rename the folder to `raylib` or keep a junction named `raylib`.
