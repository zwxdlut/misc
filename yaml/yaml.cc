
#include <iostream>
#include <string>

#include "yaml-cpp/yaml.h"

int main(int argc, char *argv[])
{
    YAML::Node config = YAML::LoadFile("../config.yaml");

    std::cout << "name:" << config["name"].as<std::string>() << std::endl;
    std::cout << "sex:" << config["sex"].as<std::string>() << std::endl;
    std::cout << "age:" << config["age"].as<int>() << std::endl;

    std::cout << config << std::endl;

    return 0;
}
