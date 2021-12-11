cmake_minimum_required(VERSION 2.8)
project(lde)

if ((DEFINED ENV{CROSS_COMPILE}) AND (DEFINED ENV{SYSROOT}))
	#
	# specify the cross compiler toolchain
	#
	message(STATUS "Cross compiler: $ENV{CROSS_COMPILE}")
	message(STATUS "Sysroot: $ENV{SYSROOT}")

	set(CMAKE_CROSSCOMPILING TRUE)
	set(CMAKE_C_COMPILER $ENV{CROSS_COMPILE}gcc)
	set(CMAKE_CXX_COMPILER $ENV{CROSS_COMPILE}g++)
	set(CMAKE_SYSROOT "$ENV{SYSROOT}")
endif()

#
# lde
#
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
add_definitions(-D _UDEBUG)
add_compile_options(-Wall -O0 -g -rdynamic)
include_directories(inc)
aux_source_directory(src SRCS)
add_executable(${PROJECT_NAME} ${SRCS} main.cc)
target_link_libraries(${PROJECT_NAME} pthread)
