cmake_minimum_required(VERSION 2.8)

project(fix_label)

find_package(OpenCV REQUIRED)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
add_compile_options(-Wall -O0 -g -rdynamic)

include_directories(
    ${CMAKE_SOURCE_DIR} 
    ${CMAKE_SOURCE_DIR}/include 
    ${OpenCV_INCLUDE_DIRS})

aux_source_directory(${CMAKE_SOURCE_DIR} SRCS)

add_executable(${PROJECT_NAME} ${SRCS})

target_link_libraries(${PROJECT_NAME} pthread rt ${OpenCV_LIBS})
