#pragma once

#include <string>
#include <vector>

enum class TokenKind {
    End,
    Ident,
    IntLit,
    FloatLit,
    StringLit,
    // keywords
    KwFn, KwLet, KwMut, KwIf, KwElse, KwWhile, KwFor, KwIn,
    KwReturn, KwBreak, KwContinue,
    KwTrue, KwFalse, KwAnd, KwOr, KwNot,
    KwInt, KwFloat, KwBool, KwString, KwVoid,
    // symbols
    LParen, RParen, LBrace, RBrace, LBracket, RBracket,
    LAngle, RAngle,
    Comma, Colon, Semicolon, Arrow, Assign,
    Plus, Minus, Star, Slash, Percent,
    Eq, Ne, Lt, Gt, Le, Ge,
    DotDot, DotDotEq,  // ..  ..=
    // directive
    Profit,  // #profit
};

struct Token {
    TokenKind kind{};
    std::string text;
    int line = 1;
    int col = 1;
};

class Lexer {
public:
    explicit Lexer(std::string source);

    Token next();
    Token peek();

private:
    std::string src_;
    size_t pos_ = 0;
    int line_ = 1;
    int col_ = 1;
    bool has_peek_ = false;
    Token peek_tok_;

    char peek_char() const;
    char get_char();
    void skip_ws_and_comments();
    Token make(TokenKind kind, std::string text, int line, int col);
    Token ident_or_kw(int line, int col);
    Token number(int line, int col);
    Token string_lit(int line, int col);
};
