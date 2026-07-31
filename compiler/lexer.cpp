#include "lexer.hpp"

#include <cctype>
#include <stdexcept>
#include <unordered_map>

Lexer::Lexer(std::string source) : src_(std::move(source)) {}

char Lexer::peek_char() const {
    if (pos_ >= src_.size()) return '\0';
    return src_[pos_];
}

char Lexer::get_char() {
    if (pos_ >= src_.size()) return '\0';
    char c = src_[pos_++];
    if (c == '\n') {
        ++line_;
        col_ = 1;
    } else {
        ++col_;
    }
    return c;
}

Token Lexer::make(TokenKind kind, std::string text, int line, int col) {
    return Token{kind, std::move(text), line, col};
}

void Lexer::skip_ws_and_comments() {
    while (true) {
        char c = peek_char();
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            get_char();
            continue;
        }
        if (c == '/' && pos_ + 1 < src_.size() && src_[pos_ + 1] == '/') {
            while (peek_char() != '\0' && peek_char() != '\n') get_char();
            continue;
        }
        // '#' line comments are handled in next() so #profit stays a directive
        break;
    }
}

Token Lexer::ident_or_kw(int line, int col) {
    std::string s;
    while (std::isalnum(static_cast<unsigned char>(peek_char())) || peek_char() == '_') {
        s.push_back(get_char());
    }

    static const std::unordered_map<std::string, TokenKind> kws = {
        {"fn", TokenKind::KwFn}, {"let", TokenKind::KwLet}, {"mut", TokenKind::KwMut},
        {"if", TokenKind::KwIf}, {"else", TokenKind::KwElse}, {"while", TokenKind::KwWhile},
        {"for", TokenKind::KwFor}, {"in", TokenKind::KwIn},
        {"return", TokenKind::KwReturn}, {"break", TokenKind::KwBreak}, {"continue", TokenKind::KwContinue},
        {"true", TokenKind::KwTrue}, {"false", TokenKind::KwFalse},
        {"and", TokenKind::KwAnd}, {"or", TokenKind::KwOr}, {"not", TokenKind::KwNot},
        {"int", TokenKind::KwInt}, {"float", TokenKind::KwFloat}, {"bool", TokenKind::KwBool},
        {"string", TokenKind::KwString}, {"void", TokenKind::KwVoid},
    };

    auto it = kws.find(s);
    if (it != kws.end()) return make(it->second, s, line, col);
    return make(TokenKind::Ident, s, line, col);
}

Token Lexer::number(int line, int col) {
    std::string s;
    while (std::isdigit(static_cast<unsigned char>(peek_char()))) s.push_back(get_char());
    if (peek_char() == '.' && pos_ + 1 < src_.size() &&
        std::isdigit(static_cast<unsigned char>(src_[pos_ + 1]))) {
        s.push_back(get_char());
        while (std::isdigit(static_cast<unsigned char>(peek_char()))) s.push_back(get_char());
        return make(TokenKind::FloatLit, s, line, col);
    }
    return make(TokenKind::IntLit, s, line, col);
}

Token Lexer::string_lit(int line, int col) {
    get_char(); // "
    std::string s;
    while (peek_char() != '\0' && peek_char() != '"') {
        char c = get_char();
        if (c == '\\') {
            char n = get_char();
            switch (n) {
                case 'n': s.push_back('\n'); break;
                case 't': s.push_back('\t'); break;
                case 'r': s.push_back('\r'); break;
                case '\\': s.push_back('\\'); break;
                case '"': s.push_back('"'); break;
                default: s.push_back(n); break;
            }
        } else {
            s.push_back(c);
        }
    }
    if (peek_char() != '"') {
        throw std::runtime_error("Unterminated string at " + std::to_string(line) + ":" + std::to_string(col));
    }
    get_char();
    return make(TokenKind::StringLit, s, line, col);
}

Token Lexer::next() {
    if (has_peek_) {
        has_peek_ = false;
        return peek_tok_;
    }

    skip_ws_and_comments();
    int line = line_;
    int col = col_;
    char c = peek_char();
    if (c == '\0') return make(TokenKind::End, "", line, col);

    if (c == '#') {
        // Only #profit is a directive; any other # starts a line comment
        // (so "# note" is fine, "#include" is rejected on purpose).
        size_t save_pos = pos_;
        int save_line = line_;
        int save_col = col_;
        get_char(); // #
        std::string word;
        while (std::isalpha(static_cast<unsigned char>(peek_char()))) word.push_back(get_char());
        if (word == "profit") return make(TokenKind::Profit, "#profit", line, col);
        if (word == "include") {
            throw std::runtime_error(
                "#include is not PodexLang — use #profit <module> at " +
                std::to_string(line) + ":" + std::to_string(col));
        }
        // Line comment: rewind to '#' then skip to EOL via skip path
        pos_ = save_pos;
        line_ = save_line;
        col_ = save_col;
        while (peek_char() != '\0' && peek_char() != '\n') get_char();
        return next();
    }

    if (std::isalpha(static_cast<unsigned char>(c)) || c == '_') return ident_or_kw(line, col);
    if (std::isdigit(static_cast<unsigned char>(c))) return number(line, col);
    if (c == '"') return string_lit(line, col);

    get_char();
    auto two = [&](char second, TokenKind both, TokenKind one) -> Token {
        if (peek_char() == second) {
            get_char();
            return make(both, std::string{c, second}, line, col);
        }
        return make(one, std::string{c}, line, col);
    };

    switch (c) {
        case '(': return make(TokenKind::LParen, "(", line, col);
        case ')': return make(TokenKind::RParen, ")", line, col);
        case '{': return make(TokenKind::LBrace, "{", line, col);
        case '}': return make(TokenKind::RBrace, "}", line, col);
        case '[': return make(TokenKind::LBracket, "[", line, col);
        case ']': return make(TokenKind::RBracket, "]", line, col);
        case '<': return two('=', TokenKind::Le, TokenKind::LAngle);
        case '>': return two('=', TokenKind::Ge, TokenKind::RAngle);
        case ',': return make(TokenKind::Comma, ",", line, col);
        case ':': return make(TokenKind::Colon, ":", line, col);
        case ';': return make(TokenKind::Semicolon, ";", line, col);
        case '+': return make(TokenKind::Plus, "+", line, col);
        case '-':
            if (peek_char() == '>') {
                get_char();
                return make(TokenKind::Arrow, "->", line, col);
            }
            return make(TokenKind::Minus, "-", line, col);
        case '*': return make(TokenKind::Star, "*", line, col);
        case '/': return make(TokenKind::Slash, "/", line, col);
        case '%': return make(TokenKind::Percent, "%", line, col);
        case '=': return two('=', TokenKind::Eq, TokenKind::Assign);
        case '!': return two('=', TokenKind::Ne, TokenKind::KwNot);
        case '.':
            if (peek_char() == '.') {
                get_char();
                if (peek_char() == '=') {
                    get_char();
                    return make(TokenKind::DotDotEq, "..=", line, col);
                }
                return make(TokenKind::DotDot, "..", line, col);
            }
            throw std::runtime_error("Unexpected '.' at " + std::to_string(line) + ":" + std::to_string(col));
        default:
            throw std::runtime_error(std::string("Unexpected character '") + c + "' at " +
                                     std::to_string(line) + ":" + std::to_string(col));
    }
}

Token Lexer::peek() {
    if (!has_peek_) {
        peek_tok_ = next();
        has_peek_ = true;
    }
    return peek_tok_;
}
