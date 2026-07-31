#include "codegen.hpp"

#include <sstream>

Codegen::Codegen(ModuleResolver& resolver) : resolver_(resolver) {}

std::string Codegen::indent_str(int n) const { return std::string(n * 4, ' '); }

std::string Codegen::emit_type(TypeName t) {
    switch (t.kind) {
        case TypeName::Int: return "int";
        case TypeName::Float: return "double";
        case TypeName::Bool: return "bool";
        case TypeName::String: return "std::string";
        case TypeName::Void: return "void";
    }
    return "int";
}

std::string Codegen::emit_expr(const Expr& e) {
    switch (e.kind) {
        case Expr::IntLit:
        case Expr::FloatLit:
        case Expr::BoolLit:
        case Expr::Ident:
            return e.text;
        case Expr::StringLit: {
            std::ostringstream o;
            o << '"';
            for (char c : e.text) {
                switch (c) {
                    case '\\': o << "\\\\"; break;
                    case '"': o << "\\\""; break;
                    case '\n': o << "\\n"; break;
                    case '\t': o << "\\t"; break;
                    case '\r': o << "\\r"; break;
                    default: o << c; break;
                }
            }
            o << '"';
            return o.str();
        }
        case Expr::Unary:
            return "(" + e.text + emit_expr(*e.left) + ")";
        case Expr::Binary:
            return "(" + emit_expr(*e.left) + " " + e.text + " " + emit_expr(*e.right) + ")";
        case Expr::Call: {
            std::ostringstream o;
            o << e.text << "(";
            for (size_t i = 0; i < e.args.size(); ++i) {
                if (i) o << ", ";
                o << emit_expr(*e.args[i]);
            }
            o << ")";
            return o.str();
        }
        case Expr::ArrayLit: {
            // C++17 CTAD: std::vector{...}
            std::ostringstream o;
            o << "std::vector{";
            for (size_t i = 0; i < e.args.size(); ++i) {
                if (i) o << ", ";
                o << emit_expr(*e.args[i]);
            }
            o << "}";
            return o.str();
        }
        case Expr::Index:
            return "(" + emit_expr(*e.left) + "[" + emit_expr(*e.right) + "])";
        case Expr::Range:
            return "/*range " + emit_expr(*e.left) + e.text + emit_expr(*e.right) + "*/";
    }
    return "/*expr*/";
}

std::string Codegen::emit_stmt(const Stmt& s, int indent) {
    std::ostringstream o;
    const std::string pad = indent_str(indent);

    auto emit_body = [&](const Stmt* body) {
        if (!body) return;
        if (body->kind == Stmt::Block) {
            for (const auto& st : body->stmts) o << emit_stmt(*st, indent + 1);
        } else {
            o << emit_stmt(*body, indent + 1);
        }
    };

    switch (s.kind) {
        case Stmt::Let: {
            o << pad;
            if (!s.is_mut) o << "const ";
            if (s.has_type) o << emit_type(s.type);
            else o << "auto";
            o << " " << s.name;
            if (s.expr) o << " = " << emit_expr(*s.expr);
            o << ";\n";
            break;
        }
        case Stmt::Assign:
            o << pad << s.name << " = " << emit_expr(*s.rhs) << ";\n";
            break;
        case Stmt::IndexAssign:
            o << pad << emit_expr(*s.expr) << " = " << emit_expr(*s.rhs) << ";\n";
            break;
        case Stmt::ExprStmt:
            o << pad << emit_expr(*s.expr) << ";\n";
            break;
        case Stmt::Return:
            o << pad << "return";
            if (s.expr) o << " " << emit_expr(*s.expr);
            o << ";\n";
            break;
        case Stmt::Break:
            o << pad << "break;\n";
            break;
        case Stmt::Continue:
            o << pad << "continue;\n";
            break;
        case Stmt::If:
            o << pad << "if (" << emit_expr(*s.expr) << ") {\n";
            emit_body(s.then_branch.get());
            o << pad << "}";
            if (s.else_branch) {
                o << " else ";
                if (s.else_branch->kind == Stmt::If) {
                    std::string nested = emit_stmt(*s.else_branch, indent);
                    if (nested.rfind(pad, 0) == 0) nested = nested.substr(pad.size());
                    o << nested;
                    return o.str();
                }
                o << "{\n";
                emit_body(s.else_branch.get());
                o << pad << "}\n";
            } else {
                o << "\n";
            }
            break;
        case Stmt::While:
            o << pad << "while (" << emit_expr(*s.expr) << ") {\n";
            emit_body(s.body.get());
            o << pad << "}\n";
            break;
        case Stmt::For: {
            // for i in 0..n / 0..=n  OR  for x in arr
            if (s.expr && s.expr->kind == Expr::Range) {
                const Expr& r = *s.expr;
                std::string start = emit_expr(*r.left);
                std::string end = emit_expr(*r.right);
                if (r.text == "..=") {
                    o << pad << "for (int " << s.name << " = static_cast<int>(" << start
                      << "); " << s.name << " <= static_cast<int>(" << end << "); ++" << s.name
                      << ") {\n";
                } else {
                    o << pad << "for (int " << s.name << " = static_cast<int>(" << start
                      << "); " << s.name << " < static_cast<int>(" << end << "); ++" << s.name
                      << ") {\n";
                }
            } else {
                o << pad << "for (const auto& " << s.name << " : " << emit_expr(*s.expr) << ") {\n";
            }
            emit_body(s.body.get());
            o << pad << "}\n";
            break;
        }
        case Stmt::Block:
            o << pad << "{\n";
            for (const auto& st : s.stmts) o << emit_stmt(*st, indent + 1);
            o << pad << "}\n";
            break;
        case Stmt::Fn: {
            o << pad << emit_type(s.ret_type) << " " << s.name << "(";
            for (size_t i = 0; i < s.params.size(); ++i) {
                if (i) o << ", ";
                o << emit_type(s.params[i].second) << " " << s.params[i].first;
            }
            o << ") {\n";
            emit_body(s.body.get());
            o << pad << "}\n";
            break;
        }
    }
    return o.str();
}

std::string Codegen::generate(const Program& program, const std::string& source_name) {
    std::ostringstream out;
    out << "// Generated by PodexLang compiler from " << source_name << "\n";
    out << "// Do not edit by hand — edit the .pdx source instead.\n\n";

    std::vector<std::string> includes;
    auto add_inc = [&](const std::string& inc) {
        for (const auto& e : includes) if (e == inc) return;
        includes.push_back(inc);
    };
    add_inc("<string>");
    add_inc("<vector>");

    std::ostringstream prelude;
    prelude << "// PodexLang runtime helpers\n"
            << "template <typename T>\n"
            << "inline int len(const std::vector<T>& v) { return static_cast<int>(v.size()); }\n"
            << "template <typename T>\n"
            << "inline void push(std::vector<T>& v, const T& x) { v.push_back(x); }\n\n";

    for (const auto& d : program.profits) {
        if (loaded_.count(d.name)) continue;
        loaded_.insert(d.name);
        ResolvedModule m = resolver_.resolve(d);
        for (const auto& inc : m.cpp_includes) add_inc(inc);
        prelude << m.prelude_cpp;
        if (!m.body_cpp.empty()) prelude << m.body_cpp;
    }

    for (const auto& inc : includes) out << "#include " << inc << "\n";
    out << "\n";
    out << prelude.str();
    if (!prelude.str().empty()) out << "\n";

    for (const auto& item : program.items) {
        out << emit_stmt(*item, 0);
        out << "\n";
    }

    return out.str();
}
