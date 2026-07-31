#include "modules.hpp"

#include <fstream>
#include <sstream>
#include <stdexcept>

#ifdef _WIN32
#include <filesystem>
namespace fs = std::filesystem;
#else
#include <filesystem>
namespace fs = std::filesystem;
#endif

ModuleResolver::ModuleResolver() {
    register_builtins();
}

void ModuleResolver::add_search_path(std::string path) {
    search_paths_.push_back(std::move(path));
}

void ModuleResolver::set_stdlib_path(std::string path) {
    stdlib_ = std::move(path);
    if (!stdlib_.empty()) search_paths_.insert(search_paths_.begin(), stdlib_);
}

void ModuleResolver::register_builtins() {
    {
        ResolvedModule m;
        m.name = "math";
        m.cpp_includes = {"<cmath>", "<cstdlib>"};
        m.prelude_cpp =
            "// PodexLang module: math\n"
            "using std::fabs;\n"
            "using std::sqrt;\n"
            "using std::sin;\n"
            "using std::cos;\n"
            "using std::tan;\n"
            "using std::pow;\n"
            "using std::floor;\n"
            "using std::ceil;\n"
            "using std::abs;\n"
            "inline double abs_f(double x) { return std::fabs(x); }\n";
        builtins_["math"] = std::move(m);
    }
    {
        ResolvedModule m;
        m.name = "io";
        m.cpp_includes = {"<iostream>", "<string>"};
#ifdef _WIN32
        // Always emit Windows UTF-8 console hook in generated C++ (target is often Windows)
#endif
        m.prelude_cpp =
            "// PodexLang module: io\n"
            "#if defined(_WIN32)\n"
            "#ifndef WIN32_LEAN_AND_MEAN\n"
            "#define WIN32_LEAN_AND_MEAN\n"
            "#endif\n"
            "#include <windows.h>\n"
            "namespace {\n"
            "struct PodexUtf8Console {\n"
            "    PodexUtf8Console() {\n"
            "        SetConsoleOutputCP(65001);\n"
            "        SetConsoleCP(65001);\n"
            "    }\n"
            "} _podex_utf8_console;\n"
            "}\n"
            "#endif\n"
            "namespace podex_io {\n"
            "template <typename T>\n"
            "void print(const T& v) { std::cout << v << '\\n'; }\n"
            "inline void print() { std::cout << '\\n'; }\n"
            "}\n"
            "using podex_io::print;\n";
        builtins_["io"] = std::move(m);
    }
    {
        ResolvedModule m;
        m.name = "str";
        m.cpp_includes = {"<string>", "<sstream>"};
        m.prelude_cpp =
            "// PodexLang module: str\n"
            "namespace podex_str {\n"
            "inline int len(const std::string& s) { return static_cast<int>(s.size()); }\n"
            "template <typename T>\n"
            "std::string to_string(const T& v) { std::ostringstream o; o << v; return o.str(); }\n"
            "}\n"
            "using podex_str::len;\n"
            "using podex_str::to_string;\n";
        builtins_["str"] = std::move(m);
    }
    {
        ResolvedModule m;
        m.name = "canvas";
        m.cpp_includes = {"\"canvas.hpp\""};
        m.prelude_cpp =
            "// PodexLang module: canvas (2D via raylib)\n"
            // Fallback if an older canvas.hpp is on the include path
            "#ifndef PODEX_CANVAS_INPUT\n"
            "#define PODEX_CANVAS_INPUT\n"
            "inline bool canvas_key_down(int key) { return IsKeyDown(key); }\n"
            "inline bool canvas_key_pressed(int key) { return IsKeyPressed(key); }\n"
            "inline int canvas_mouse_x() { return GetMouseX(); }\n"
            "inline int canvas_mouse_y() { return GetMouseY(); }\n"
            "#endif\n";
        builtins_["canvas"] = std::move(m);
    }
    {
        ResolvedModule m;
        m.name = "orbit";
        m.cpp_includes = {"\"orbit.hpp\""};
        m.prelude_cpp =
            "// PodexLang module: orbit (3D via raylib)\n"
            "#ifndef PODEX_ORBIT_INPUT\n"
            "#define PODEX_ORBIT_INPUT\n"
            "inline bool orbit_key_down(int key) { return IsKeyDown(key); }\n"
            "inline bool orbit_key_pressed(int key) { return IsKeyPressed(key); }\n"
            "inline int orbit_mouse_x() { return GetMouseX(); }\n"
            "inline int orbit_mouse_y() { return GetMouseY(); }\n"
            "#endif\n";
        builtins_["orbit"] = std::move(m);
    }
}

std::string ModuleResolver::find_module_file(const std::string& name) const {
    const std::vector<std::string> candidates = {
        name + ".pdx",
        name + "/mod.pdx",
    };

    for (const auto& dir : search_paths_) {
        for (const auto& c : candidates) {
            fs::path p = fs::path(dir) / c;
            if (fs::exists(p) && fs::is_regular_file(p)) return p.string();
        }
    }
    // also try cwd
    for (const auto& c : candidates) {
        if (fs::exists(c) && fs::is_regular_file(c)) return fs::absolute(c).string();
    }
    return {};
}

ResolvedModule ModuleResolver::load_pdx_module(const std::string& name, const std::string& path) {
    // For custom .pdx modules we currently emit a marker and expect the module
    // file to contain only #profit + fn declarations — it will be compiled as
    // a separate translation unit by the driver in a later step.
    // MVP: inline the source as a comment + require builtins for now via re-export.
    std::ifstream in(path);
    if (!in) throw std::runtime_error("Cannot open module file: " + path);

    std::ostringstream ss;
    ss << in.rdbuf();
    std::string src = ss.str();

    ResolvedModule m;
    m.name = name;
    m.from_file = true;
    m.source_path = path;
    m.cpp_includes = {"<string>"};
    m.prelude_cpp = "// PodexLang user module: " + name + " (" + path + ")\n";
    m.body_cpp = "/* module source embedded for reference — compile separately in future */\n";

    // Parse #profit lines from module to pull transitive builtins
    std::istringstream lines(src);
    std::string line;
    while (std::getline(lines, line)) {
        auto trim = [](std::string& s) {
            while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) s.erase(s.begin());
        };
        trim(line);
        if (line.rfind("#profit", 0) == 0) {
            auto l = line.find('<');
            auto r = line.find('>');
            if (l != std::string::npos && r != std::string::npos && r > l) {
                std::string dep = line.substr(l + 1, r - l - 1);
                auto it = builtins_.find(dep);
                if (it != builtins_.end()) {
                    for (const auto& inc : it->second.cpp_includes) m.cpp_includes.push_back(inc);
                    m.prelude_cpp += it->second.prelude_cpp;
                }
            }
        }
    }
    return m;
}

ResolvedModule ModuleResolver::resolve(const ProfitDirective& d) {
    if (d.angle) {
        auto it = builtins_.find(d.name);
        if (it != builtins_.end()) return it->second;

        std::string path = find_module_file(d.name);
        if (!path.empty()) return load_pdx_module(d.name, path);

        throw std::runtime_error(
            "Module not found: #profit <" + d.name + "> at line " + std::to_string(d.line) +
            "\n  searched stdlib and -I paths; known builtins: math, io, str, canvas, orbit");
    }

    // #profit "path"
    fs::path p(d.name);
    if (!p.has_extension()) p += ".pdx";
    if (!fs::exists(p)) {
        std::string found = find_module_file(d.name);
        if (found.empty()) {
            throw std::runtime_error("Module file not found: #profit \"" + d.name + "\" at line " +
                                     std::to_string(d.line));
        }
        return load_pdx_module(d.name, found);
    }
    return load_pdx_module(d.name, p.string());
}
