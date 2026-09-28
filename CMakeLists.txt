cmake_minimum_required(VERSION 3.15)
project(FoxRAT)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Ищем твой main.cpp
add_executable(FoxRAT WIN32 main.cpp)

# Линковка WinINet для HTTP запросов
target_link_libraries(FoxRAT PRIVATE wininet)
