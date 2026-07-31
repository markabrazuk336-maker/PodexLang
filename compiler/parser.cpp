#include "parser.hpp"

#include <stdexcept>

Parser::Parser(Lexer lexer) : lex_(std::move(lexer)) {
    advance();
}

void Parser::advance() { cur_ = lex_.next(); }

bool Parser::check(TokenKind k) const { return cur_.kind == k; }

bool Parser::match(TokenKind k) {
    if (!check(k)) return false;
    advance();
    return true;
}

Token Parser::expect(TokenKind k, const char* what) {
    if (!check(k)) error(cur_, std::string("Expected ") + what);
    Token t = cur_;
    advance();
    return t;
}

void Parser::error(const Token& t, const std::string& msg) {
    throw std::runtime_error(msg + " at " + std::to_string(t.line) + ":" + std::to_string(t.col) +
                             " (got '" + t.text + "')");
}

Program Parser::parse() {
    Program prog;
    while (check(TokenKind::Profit)) parse_profit(prog);
    while (!check(TokenKind::End)) {
        if (check(TokenKind::KwFn)) prog.items.push_back(parse_fn());
        else prog.items.push_back(parse_stmt());
    }
    return prog;
}

void Parser::parse_profit(Program& prog) {
    Token at = expect(TokenKind::Profit, "#profit");
    ProfitDirective d;
    d.line = at.line;

    if (match(TokenKind::LAngle)) {
        d.angle = true;
        Token name = expect(TokenKind::Ident, "module name");
        d.name = name.text;
        expect(TokenKind::RAngle, ">");
    } else if (check(TokenKind::StringLit)) {
        d.angle = false;
        d.name = cur_.text;
        advance();
    } else {
        error(cur_, "Expected <module> or \"module\" after #profit");
    }
    match(TokenKind::Semicolon);
    prog.profits.push_back(std::move(d));
}

TypeName Parser::parse_type() {
    if (match(TokenKind::KwInt)) return {TypeName::Int};
    if (match(TokenKind::KwFloat)) return {TypeName::Float};
    if (match(TokenKind::KwBool)) return {TypeName::Bool};
    if (match(TokenKind::KwString)) return {TypeName::String};
    if (match(TokenKind::KwVoid)) return {TypeName::Void};
    error(cur_, "Expected type name");
}

StmtPtr Parser::parse_fn() {
    auto s = std::make_unique<Stmt>();
    s->kind = Stmt::Fn;
    Token fn = expect(TokenKind::KwFn, "fn");
    s->line = fn.line;
    Token name = expect(TokenKind::Ident, "function name");
    s->name = name.text;
    expect(TokenKind::LParen, "(");
    if (!check(TokenKind::RParen)) {
        do {
            Token pname = expect(TokenKind::Ident, "parameter name");
            expect(TokenKind::Colon, ":");
            TypeName t = parse_type();
            s->params.emplace_back(pname.text, t);
        } while (match(TokenKind::Comma));
    }
    expect(TokenKind::RParen, ")");
    s->ret_type = {TypeName::Void};
    if (match(TokenKind::Arrow)) s->ret_type = parse_type();
    s->body = parse_block();
    return s;
}

StmtPtr Parser::parse_block() {
    auto s = std::make_unique<Stmt>();
    s->kind = Stmt::Block;
    Token b = expect(TokenKind::LBrace, "{");
    s->line = b.line;
    while (!check(TokenKind::RBrace) && !check(TokenKind::End)) {
        s->stmts.push_back(parse_stmt());
    }
    expect(TokenKind::RBrace, "}");
    return s;
}

StmtPtr Parser::parse_let() {
    auto s = std::make_unique<Stmt>();
    s->kind = Stmt::Let;
    Token t = expect(TokenKind::KwLet, "let");
    s->line = t.line;
    s->is_mut = match(TokenKind::KwMut);
    Token name = expect(TokenKind::Ident, "variable name");
    s->name = name.text;
    if (match(TokenKind::Colon)) {
        s->has_type = true;
        s->type = parse_type();
    }
    if (match(TokenKind::Assign)) s->expr = parse_expr();
    match(TokenKind::Semicolon);
    return s;
}

StmtPtr Parser::parse_if() {
    auto s = std::make_unique<Stmt>();
    s->kind = Stmt::If;
    Token t = expect(TokenKind::KwIf, "if");
    s->line = t.line;
    s->expr = parse_expr();
    s->then_branch = parse_block();
    if (match(TokenKind::KwElse)) {
        if (check(TokenKind::KwIf)) s->else_branch = parse_if();
        else s->else_branch = parse_block();
    }
    return s;
}

StmtPtr Parser::parse_while() {
    auto s = std::make_unique<Stmt>();
    s->kind = Stmt::While;
    Token t = expect(TokenKind::KwWhile, "while");
    s->line = t.line;
    s->expr = parse_expr();
    s->body = parse_block();
    return s;
}

StmtPtr Parser::parse_for() {
    auto s = std::make_unique<Stmt>();
    s->kind = Stmt::For;
    Token t = expect(TokenKind::KwFor, "for");
    s->line = t.line;
    Token name = expect(TokenKind::Ident, "loop variable");
    s->name = name.text;
    expect(TokenKind::KwIn, "in");
    s->expr = parse_expr();
    s->body = parse_block();
    return s;
}

StmtPtr Parser::parse_return() {
    auto s = std::make_unique<Stmt>();
    s->kind = Stmt::Return;
    Token t = expect(TokenKind::KwReturn, "return");
    s->line = t.line;
    if (!check(TokenKind::RBrace) && !check(TokenKind::Semicolon) && !check(TokenKind::End)) {
        s->expr = parse_expr();
    }
    match(TokenKind::Semicolon);
    return s;
}

StmtPtr Parser::parse_stmt() {
    if (check(TokenKind::KwLet)) return parse_let();
    if (check(TokenKind::KwIf)) return parse_if();
    if (check(TokenKind::KwWhile)) return parse_while();
    if (check(TokenKind::KwFor)) return parse_for();
    if (check(TokenKind::KwReturn)) return parse_return();
    if (check(TokenKind::LBrace)) return parse_block();

    if (check(TokenKind::KwBreak)) {
        auto s = std::make_unique<Stmt>();
        s->kind = Stmt::Break;
        s->line = cur_.line;
        advance();
        match(TokenKind::Semicolon);
        return s;
    }
    if (check(TokenKind::KwContinue)) {
        auto s = std::make_unique<Stmt>();
        s->kind = Stmt::Continue;
        s->line = cur_.line;
        advance();
        match(TokenKind::Semicolon);
        return s;
    }

    auto s = std::make_unique<Stmt>();
    s->line = cur_.line;
    ExprPtr e = parse_expr();
    if (match(TokenKind::Assign)) {
        if (e->kind == Expr::Ident) {
            s->kind = Stmt::Assign;
            s->name = e->text;
            s->rhs = parse_expr();
        } else if (e->kind == Expr::Index) {
            s->kind = Stmt::IndexAssign;
            s->expr = std::move(e);
            s->rhs = parse_expr();
        } else {
            error(cur_, "Invalid assignment target");
        }
        match(TokenKind::Semicolon);
        return s;
    }

    s->kind = Stmt::ExprStmt;
    s->expr = std::move(e);
    match(TokenKind::Semicolon);
    return s;
}

ExprPtr Parser::parse_expr() { return parse_range(); }

ExprPtr Parser::parse_range() {
    ExprPtr e = parse_or();
    if (match(TokenKind::DotDotEq)) {
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Range;
        n->text = "..=";
        n->line = e->line;
        n->left = std::move(e);
        n->right = parse_or();
        return n;
    }
    if (match(TokenKind::DotDot)) {
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Range;
        n->text = "..";
        n->line = e->line;
        n->left = std::move(e);
        n->right = parse_or();
        return n;
    }
    return e;
}

ExprPtr Parser::parse_or() {
    ExprPtr e = parse_and();
    while (match(TokenKind::KwOr)) {
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Binary;
        n->text = "||";
        n->line = e->line;
        n->left = std::move(e);
        n->right = parse_and();
        e = std::move(n);
    }
    return e;
}

ExprPtr Parser::parse_and() {
    ExprPtr e = parse_equality();
    while (match(TokenKind::KwAnd)) {
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Binary;
        n->text = "&&";
        n->line = e->line;
        n->left = std::move(e);
        n->right = parse_equality();
        e = std::move(n);
    }
    return e;
}

ExprPtr Parser::parse_equality() {
    ExprPtr e = parse_compare();
    while (true) {
        std::string op;
        if (match(TokenKind::Eq)) op = "==";
        else if (match(TokenKind::Ne)) op = "!=";
        else break;
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Binary;
        n->text = op;
        n->line = e->line;
        n->left = std::move(e);
        n->right = parse_compare();
        e = std::move(n);
    }
    return e;
}

ExprPtr Parser::parse_compare() {
    ExprPtr e = parse_term();
    while (true) {
        std::string op;
        if (match(TokenKind::LAngle)) op = "<";
        else if (match(TokenKind::RAngle)) op = ">";
        else if (match(TokenKind::Le)) op = "<=";
        else if (match(TokenKind::Ge)) op = ">=";
        else break;
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Binary;
        n->text = op;
        n->line = e->line;
        n->left = std::move(e);
        n->right = parse_term();
        e = std::move(n);
    }
    return e;
}

ExprPtr Parser::parse_term() {
    ExprPtr e = parse_factor();
    while (true) {
        std::string op;
        if (match(TokenKind::Plus)) op = "+";
        else if (match(TokenKind::Minus)) op = "-";
        else break;
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Binary;
        n->text = op;
        n->line = e->line;
        n->left = std::move(e);
        n->right = parse_factor();
        e = std::move(n);
    }
    return e;
}

ExprPtr Parser::parse_factor() {
    ExprPtr e = parse_unary();
    while (true) {
        std::string op;
        if (match(TokenKind::Star)) op = "*";
        else if (match(TokenKind::Slash)) op = "/";
        else if (match(TokenKind::Percent)) op = "%";
        else break;
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Binary;
        n->text = op;
        n->line = e->line;
        n->left = std::move(e);
        n->right = parse_unary();
        e = std::move(n);
    }
    return e;
}

ExprPtr Parser::parse_unary() {
    if (cur_.kind == TokenKind::Minus || cur_.kind == TokenKind::KwNot) {
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Unary;
        n->line = cur_.line;
        n->text = (cur_.kind == TokenKind::Minus) ? "-" : "!";
        advance();
        n->left = parse_unary();
        return n;
    }
    return parse_primary();
}

ExprPtr Parser::parse_primary() {
    auto make_lit = [&](Expr::Kind k, std::string text) {
        auto e = std::make_unique<Expr>();
        e->kind = k;
        e->text = std::move(text);
        e->line = cur_.line;
        advance();
        return e;
    };

    ExprPtr e;

    if (check(TokenKind::IntLit)) {
        e = make_lit(Expr::IntLit, cur_.text);
    } else if (check(TokenKind::FloatLit)) {
        e = make_lit(Expr::FloatLit, cur_.text);
    } else if (check(TokenKind::StringLit)) {
        e = make_lit(Expr::StringLit, cur_.text);
    } else if (check(TokenKind::KwTrue) || check(TokenKind::KwFalse)) {
        e = std::make_unique<Expr>();
        e->kind = Expr::BoolLit;
        e->text = (cur_.kind == TokenKind::KwTrue) ? "true" : "false";
        e->line = cur_.line;
        advance();
    } else if (check(TokenKind::Ident)) {
        e = std::make_unique<Expr>();
        e->kind = Expr::Ident;
        e->text = cur_.text;
        e->line = cur_.line;
        advance();
        if (match(TokenKind::LParen)) {
            e->kind = Expr::Call;
            if (!check(TokenKind::RParen)) {
                do {
                    e->args.push_back(parse_expr());
                } while (match(TokenKind::Comma));
            }
            expect(TokenKind::RParen, ")");
        }
    } else if (match(TokenKind::LParen)) {
        e = parse_expr();
        expect(TokenKind::RParen, ")");
    } else if (match(TokenKind::LBracket)) {
        e = std::make_unique<Expr>();
        e->kind = Expr::ArrayLit;
        e->line = cur_.line;
        if (!check(TokenKind::RBracket)) {
            do {
                e->args.push_back(parse_expr());
            } while (match(TokenKind::Comma));
        }
        expect(TokenKind::RBracket, "]");
    } else {
        error(cur_, "Expected expression");
    }

    while (match(TokenKind::LBracket)) {
        auto n = std::make_unique<Expr>();
        n->kind = Expr::Index;
        n->line = e->line;
        n->left = std::move(e);
        n->right = parse_expr();
        expect(TokenKind::RBracket, "]");
        e = std::move(n);
    }
    return e;
}
