#pragma once

#include "lexer.hpp"

#include <memory>
#include <string>
#include <vector>

struct TypeName {
    enum Kind { Int, Float, Bool, String, Void } kind = Int;
};

struct Expr;
struct Stmt;

using ExprPtr = std::unique_ptr<Expr>;
using StmtPtr = std::unique_ptr<Stmt>;

struct Expr {
    enum Kind {
        IntLit, FloatLit, BoolLit, StringLit, Ident,
        Unary, Binary, Call,
        ArrayLit,   // args = elements
        Index,      // left[right]
        Range,      // left..right or left..=right  (text ".." / "..=")
    } kind = Ident;

    int line = 1;
    std::string text;          // literal / ident / op / range marker
    ExprPtr left;
    ExprPtr right;
    std::vector<ExprPtr> args;
};

struct Stmt {
    enum Kind {
        Let, Assign, IndexAssign, ExprStmt, Return,
        If, While, For, Block, Fn, Break, Continue
    } kind = ExprStmt;

    int line = 1;
    std::string name;
    bool is_mut = false;
    TypeName type{};
    bool has_type = false;
    ExprPtr expr;              // let init / return / cond / for-iterable / index-lhs
    ExprPtr rhs;               // assign value
    StmtPtr then_branch;
    StmtPtr else_branch;
    StmtPtr body;
    std::vector<std::pair<std::string, TypeName>> params;
    TypeName ret_type{};
    std::vector<StmtPtr> stmts;
};

struct ProfitDirective {
    std::string name;
    bool angle = true;
    int line = 1;
};

struct Program {
    std::vector<ProfitDirective> profits;
    std::vector<StmtPtr> items;
};

class Parser {
public:
    explicit Parser(Lexer lexer);

    Program parse();

private:
    Lexer lex_;
    Token cur_;

    void advance();
    bool check(TokenKind k) const;
    bool match(TokenKind k);
    Token expect(TokenKind k, const char* what);

    [[noreturn]] void error(const Token& t, const std::string& msg);

    void parse_profit(Program& prog);
    StmtPtr parse_fn();
    StmtPtr parse_stmt();
    StmtPtr parse_block();
    StmtPtr parse_let();
    StmtPtr parse_if();
    StmtPtr parse_while();
    StmtPtr parse_for();
    StmtPtr parse_return();

    TypeName parse_type();
    ExprPtr parse_expr();
    ExprPtr parse_range();
    ExprPtr parse_or();
    ExprPtr parse_and();
    ExprPtr parse_equality();
    ExprPtr parse_compare();
    ExprPtr parse_term();
    ExprPtr parse_factor();
    ExprPtr parse_unary();
    ExprPtr parse_primary();
};
