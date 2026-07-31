#include "codegen.hpp"
#include "lexer.hpp"
#include "modules.hpp"
#include "parser.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace fs = std::filesystem;

static std::string read_file(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("Cannot open file: " + path);
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

static void write_file(const std::string& path, const std::string& data) {
    if (auto parent = fs::path(path).parent_path(); !parent.empty()) {
        fs::create_directories(parent);
    }
    std::ofstream out(path);
    if (!out) throw std::runtime_error("Cannot write file: " + path);
    out << data;
}

static void usage(const char* argv0) {
    std::cerr
        << "PodexLang compiler (podexc)\n"
        << "Usage: " << argv0 << " [options] <file.pdx>\n\n"
        << "Options:\n"
        << "  -o <file>       Output C++ file (default: <name>.cpp)\n"
        << "  -I <dir>        Add module search path\n"
        << "  --stdlib <dir>  Stdlib path (default: baked-in or ./stdlib)\n"
        << "  -h, --help      Show help\n\n"
        << "Modules: use  #profit <math>  instead of #include.\n"
        << "Builtins: math, io, str. Custom modules: name.pdx in search paths.\n";
}

int main(int argc, char** argv) {
    std::string input;
    try {
        std::string output;
        std::string stdlib =
#ifdef PODEX_STDLIB_DIR
            PODEX_STDLIB_DIR;
#else
            "stdlib";
#endif
        std::vector<std::string> includes;

        for (int i = 1; i < argc; ++i) {
            std::string a = argv[i];
            if (a == "-h" || a == "--help") {
                usage(argv[0]);
                return 0;
            }
            if (a == "-o") {
                if (i + 1 >= argc) throw std::runtime_error("-o needs a path");
                output = argv[++i];
            } else if (a == "-I") {
                if (i + 1 >= argc) throw std::runtime_error("-I needs a path");
                includes.push_back(argv[++i]);
            } else if (a == "--stdlib") {
                if (i + 1 >= argc) throw std::runtime_error("--stdlib needs a path");
                stdlib = argv[++i];
            } else if (!a.empty() && a[0] == '-') {
                throw std::runtime_error("Unknown option: " + a);
            } else {
                input = a;
            }
        }

        if (input.empty()) {
            usage(argv[0]);
            return 1;
        }

        if (output.empty()) {
            fs::path p(input);
            output = p.replace_extension(".cpp").string();
        }

        ModuleResolver resolver;
        resolver.set_stdlib_path(stdlib);
        for (auto& p : includes) resolver.add_search_path(p);

        // Also search beside the source file
        auto src_dir = fs::path(input).parent_path();
        if (!src_dir.empty()) resolver.add_search_path(src_dir.string());

        std::string source = read_file(input);
        Lexer lexer(std::move(source));
        Parser parser(std::move(lexer));
        Program program = parser.parse();

        bool has_main = false;
        for (const auto& item : program.items) {
            if (item && item->kind == Stmt::Fn && item->name == "main") {
                has_main = true;
                break;
            }
        }
        if (!has_main) {
            throw std::runtime_error(
                "missing entry point: add  fn main() -> int { ... }  at 1:1");
        }

        Codegen gen(resolver);
        std::string cpp = gen.generate(program, input);
        write_file(output, cpp);

        std::cout << "PodexLang: " << input << " -> " << output << "\n";
        for (const auto& d : program.profits) {
            std::cout << "  #profit " << (d.angle ? "<" : "\"") << d.name
                      << (d.angle ? ">" : "\"") << "\n";
        }
        return 0;
    } catch (const std::exception& e) {
        // IDE-friendly: path:line:col: message
        std::string msg = e.what();
        std::string file = input.empty() ? "<input>" : input;
        std::cerr << "podexc error: " << file << ": " << msg << "\n";
        auto at = msg.rfind(" at ");
        if (at != std::string::npos) {
            auto loc = msg.substr(at + 4);
            auto sp = loc.find(' ');
            if (sp != std::string::npos) loc = loc.substr(0, sp);
            if (loc.find(':') != std::string::npos) {
                std::cerr << file << ":" << loc << ": error: " << msg.substr(0, at) << "\n";
            }
        }
        return 1;
    }
}
