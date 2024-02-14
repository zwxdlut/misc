cmake_minimum_required(VERSION 2.8)

project(threadpool)

find_package(Boost REQUIRED COMPONENTS 
    system thread)
message(STATUS "Boost_VERSION ${Boost_VERSION}")
message(STATUS "Boost_INCLUDE_DIRS ${Boost_INCLUDE_DIRS}")
message(STATUS "Boost_LIBRARY_DIRS ${Boost_LIBRARY_DIRS}")
message(STATUS "Boost_LIBRARIES ${Boost_LIBRARIES}")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
add_compile_options(-Wall -O0 -g -rdynamic)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${Boost_INCLUDE_DIRS})

aux_source_directory(${CMAKE_CURRENT_SOURCE_DIR} SRCS)

link_directories(${Boost_LIBRARY_DIRS})

add_executable(${PROJECT_NAME} ${SRCS})

target_link_libraries(${PROJECT_NAME} pthread rt ${Boost_LIBRARIES})
