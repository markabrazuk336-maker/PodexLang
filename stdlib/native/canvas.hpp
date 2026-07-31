#pragma once
// PodexLang #profit <canvas> — 2D graphics (raylib)
#include "raylib.h"
#include <string>

inline Color canvas_rgb(int r, int g, int b) {
    return Color{
        static_cast<unsigned char>(r < 0 ? 0 : (r > 255 ? 255 : r)),
        static_cast<unsigned char>(g < 0 ? 0 : (g > 255 ? 255 : g)),
        static_cast<unsigned char>(b < 0 ? 0 : (b > 255 ? 255 : b)),
        255};
}

inline void canvas_open(int w, int h, const char* title) {
    InitWindow(w, h, title);
    SetTargetFPS(60);
}
inline void canvas_open(int w, int h, const std::string& title) {
    canvas_open(w, h, title.c_str());
}
inline void canvas_close() { CloseWindow(); }
inline bool canvas_should_close() { return WindowShouldClose(); }
inline void canvas_fps(int fps) { SetTargetFPS(fps); }

inline void canvas_begin() { BeginDrawing(); }
inline void canvas_end() { EndDrawing(); }
inline void canvas_clear(int r, int g, int b) { ClearBackground(canvas_rgb(r, g, b)); }

inline void canvas_circle(int x, int y, int radius, int r, int g, int b) {
    DrawCircle(x, y, static_cast<float>(radius), canvas_rgb(r, g, b));
}
inline void canvas_rect(int x, int y, int w, int h, int r, int g, int b) {
    DrawRectangle(x, y, w, h, canvas_rgb(r, g, b));
}
inline void canvas_line(int x1, int y1, int x2, int y2, int r, int g, int b) {
    DrawLine(x1, y1, x2, y2, canvas_rgb(r, g, b));
}
inline void canvas_text(int x, int y, const char* text, int size, int r, int g, int b) {
    DrawText(text, x, y, size, canvas_rgb(r, g, b));
}
inline void canvas_text(int x, int y, const std::string& text, int size, int r, int g, int b) {
    canvas_text(x, y, text.c_str(), size, r, g, b);
}

// Input — raylib key codes: LEFT=263 RIGHT=262 UP=265 DOWN=264 W=87 A=65 S=83 D=68 SPACE=32
#ifndef PODEX_CANVAS_INPUT
#define PODEX_CANVAS_INPUT
inline bool canvas_key_down(int key) { return IsKeyDown(key); }
inline bool canvas_key_pressed(int key) { return IsKeyPressed(key); }
inline int canvas_mouse_x() { return GetMouseX(); }
inline int canvas_mouse_y() { return GetMouseY(); }
#endif
