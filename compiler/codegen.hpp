#pragma once

#include "modules.hpp"
#include "parser.hpp"

#include <string>
#include <unordered_set>
#include <vector>

class Codegen {
public:
    Codegen(ModuleResolver& resolver);

    std::string generate(const Program& program, const std::string& source_name);

private:
    ModuleResolver& resolver_;
    std::unordered_set<std::string> loaded_;

    std::string emit_stmt(const Stmt& s, int indent);
    std::string emit_expr(const Expr& e);
    std::string emit_type(TypeName t);
    std::string indent_str(int n) const;
};
