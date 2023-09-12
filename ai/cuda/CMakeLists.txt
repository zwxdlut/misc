cmake_minimum_required(VERSION 2.8)

project(cuda LANGUAGES CXX CUDA)
#enable_language(CUDA)

find_package(CUDA REQUIRED)

if (NOT CUDA_FOUND)
    message(STATUS "CUDA not found. Project will not be built.")
endif(NOT CUDA_FOUND)

message(STATUS "CUDA_TOOLKIT_ROOT_DIR: ${CUDA_TOOLKIT_ROOT_DIR}")
message(STATUS "CUDA_INCLUDE_DIRS: ${CUDA_INCLUDE_DIRS}")
message(STATUS "CUDA_LIBRARIES: ${CUDA_LIBRARIES}")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -std=c++11")
set(CUDA_NVCC_FLAGS ${CUDA_NVCC_FLAGS}; -std=c++11; -g;
    -gencode arch=compute_60,code=sm_60
    -gencode arch=compute_61,code=sm_61
    -gencode arch=compute_70,code=sm_70
    -gencode arch=compute_72,code=sm_72
    -gencode arch=compute_75,code=sm_75
    -gencode arch=compute_80,code=sm_80
    -gencode arch=compute_86,code=sm_86)

include_directories(
    ${CMAKE_SOURCE_DIR} 
    ${CMAKE_SOURCE_DIR}/include 
    ${CUDA_INCLUDE_DIRS})

aux_source_directory(${CMAKE_SOURCE_DIR} SRCS)

link_directories(/usr/local/cuda)

cuda_add_executable(${PROJECT_NAME} ${SRCS})

target_link_libraries(${PROJECT_NAME} ${CUDA_LIBRARIES})
