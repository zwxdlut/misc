cmake_minimum_required(VERSION 2.8)

project(yaml)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
add_compile_options(-Wall -O0 -g -rdynamic)
add_definitions(-D _UDEBUG)

include_directories(. include)

aux_source_directory(. SRCS)

link_directories(${CMAKE_HOME_DIRECTORY})

add_executable(${PROJECT_NAME} ${SRCS})

target_link_libraries(${PROJECT_NAME} pthread rt yaml-cpp)
