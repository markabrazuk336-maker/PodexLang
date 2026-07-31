#pragma once
// PodexLang #profit <orbit> — 3D graphics (raylib)
#include "raylib.h"
#include <string>

inline Color orbit_rgb(int r, int g, int b) {
    return Color{
        static_cast<unsigned char>(r < 0 ? 0 : (r > 255 ? 255 : r)),
        static_cast<unsigned char>(g < 0 ? 0 : (g > 255 ? 255 : g)),
        static_cast<unsigned char>(b < 0 ? 0 : (b > 255 ? 255 : b)),
        255};
}

inline Camera3D& orbit_cam() {
    static Camera3D cam{};
    static bool ready = false;
    if (!ready) {
        cam.position = Vector3{4.0f, 4.0f, 4.0f};
        cam.target = Vector3{0.0f, 0.0f, 0.0f};
        cam.up = Vector3{0.0f, 1.0f, 0.0f};
        cam.fovy = 45.0f;
        cam.projection = CAMERA_PERSPECTIVE;
        ready = true;
    }
    return cam;
}

inline void orbit_open(int w, int h, const char* title) {
    InitWindow(w, h, title);
    SetTargetFPS(60);
}
inline void orbit_open(int w, int h, const std::string& title) {
    orbit_open(w, h, title.c_str());
}
inline void orbit_close() { CloseWindow(); }
inline bool orbit_should_close() { return WindowShouldClose(); }
inline void orbit_fps(int fps) { SetTargetFPS(fps); }

inline void orbit_begin() { BeginDrawing(); }
inline void orbit_end() { EndDrawing(); }
inline void orbit_clear(int r, int g, int b) { ClearBackground(orbit_rgb(r, g, b)); }

inline void orbit_begin_3d() {
    UpdateCamera(&orbit_cam(), CAMERA_ORBITAL);
    BeginMode3D(orbit_cam());
}
inline void orbit_end_3d() { EndMode3D(); }

inline void orbit_cube(float x, float y, float z, float size, int r, int g, int b) {
    DrawCube(Vector3{x, y, z}, size, size, size, orbit_rgb(r, g, b));
    DrawCubeWires(Vector3{x, y, z}, size, size, size, orbit_rgb(255, 255, 255));
}
inline void orbit_sphere(float x, float y, float z, float radius, int r, int g, int b) {
    DrawSphere(Vector3{x, y, z}, radius, orbit_rgb(r, g, b));
}
inline void orbit_grid(int slices, float spacing) {
    DrawGrid(slices, spacing);
}
inline void orbit_text(int x, int y, const char* text, int size, int r, int g, int b) {
    DrawText(text, x, y, size, orbit_rgb(r, g, b));
}
inline void orbit_text(int x, int y, const std::string& text, int size, int r, int g, int b) {
    orbit_text(x, y, text.c_str(), size, r, g, b);
}
