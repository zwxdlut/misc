cmake_minimum_required(VERSION 2.8)

project(yaml)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
add_compile_options(-Wall -O0 -g -rdynamic)

include_directories(
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/include
    ${Boost_INCLUDE_DIRS})

aux_source_directory(${CMAKE_SOURCE_DIR} SRCS)

link_directories(${CMAKE_SOURCE_DIR})

add_executable(${PROJECT_NAME} ${SRCS})

target_link_libraries(${PROJECT_NAME} pthread rt yaml-cpp)
