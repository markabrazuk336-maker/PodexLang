#pragma once

#include "parser.hpp"

#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

struct ResolvedModule {
    std::string name;
    std::vector<std::string> cpp_includes;
    std::string prelude_cpp; // helpers / using
    std::string body_cpp;    // from .pdx module body (already C++ snippets / decls)
    bool from_file = false;
    std::string source_path;
};

class ModuleResolver {
public:
    ModuleResolver();

    void add_search_path(std::string path);
    void set_stdlib_path(std::string path);

    ResolvedModule resolve(const ProfitDirective& d);

    const std::vector<std::string>& search_paths() const { return search_paths_; }

private:
    std::string stdlib_;
    std::vector<std::string> search_paths_;
    std::unordered_map<std::string, ResolvedModule> builtins_;

    void register_builtins();
    ResolvedModule load_pdx_module(const std::string& name, const std::string& path);
    std::string find_module_file(const std::string& name) const;
};
