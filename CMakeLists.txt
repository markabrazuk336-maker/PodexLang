cmake_minimum_required(VERSION 3.16)
project(PodexLang LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(podexc
    compiler/main.cpp
    compiler/lexer.cpp
    compiler/parser.cpp
    compiler/modules.cpp
    compiler/codegen.cpp
)

target_include_directories(podexc PRIVATE compiler)

# Default stdlib path baked in for convenience
target_compile_definitions(podexc PRIVATE
    PODEX_STDLIB_DIR="${CMAKE_SOURCE_DIR}/stdlib"
)
