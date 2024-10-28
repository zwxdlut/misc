cmake_minimum_required(VERSION 3.5...3.26)
project(example LANGUAGES CXX)

# set(pybind11_DIR "$ENV{HOME}/.local/lib/python3.8/site-packages/pybind11/share/cmake/pybind11")
find_package(pybind11 REQUIRED
    PATHS $ENV{HOME}/.local/lib/python3.8/site-packages/pybind11/share/cmake/pybind11
)

pybind11_add_module(example main.cc)
