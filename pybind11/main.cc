#include <iostream>
#include <memory>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
// #include <pybind11/eigen.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

class Pet 
{
public:
    enum Kind 
    {
        Dog = 0,
        Cat
    };

    struct Attributes 
    {
        Attributes() = default;
        Attributes(const float _age) : age(_age) {}

        float age = 0;
    };

    Pet() = default;
    Pet(const std::string &_name, const Kind _kind, const Attributes &_attrs) : 
        name(_name), kind(_kind), attrs(_attrs) {}

    const std::string& getName() const { return name; }
    Kind getKind() const { return kind; }
    const Attributes& getAttributes() const { return attrs; }

    void set(const std::string &_name) { name = _name; }
    void set(const Kind _kind) { kind = _kind; }
    void set(const Attributes &_attrs) { attrs = _attrs; }

private:
    std::string name;
    Kind kind;
    Attributes attrs;
};

struct Dog : Pet 
{
    Dog() = default;
    Dog(const std::string &_name, const Kind _kind, const Pet::Attributes &_attrs) : 
        Pet(_name, _kind, _attrs) {}

    std::string bark() const { return "woof!"; }
};

int add(int i = 1, int j = 2) 
{
    return i + j;
}

template <typename... Args>
using overload_cast_ = pybind11::detail::overload_cast_impl<Args...>;

PYBIND11_MODULE(example, m) 
{
    m.doc() = "pybind11 example plugin"; // optional module docstring

    // // regular notation
    // m.def("add", &add, "A function that adds two numbers", py::arg("i") = 1, py::arg("j") = 2);
    // shorthand
    using namespace pybind11::literals;
    m.def("add", &add, "A function that adds two numbers", "i"_a=1, "j"_a=2);

    m.attr("the_answer") = 42;
    py::object world = py::cast("World");
    m.attr("what") = world;

    py::class_<Pet> pet(m, "Pet", py::dynamic_attr());
    // py::class_<Pet, std::unique_ptr<Pet, py::nodelete>> pet(m, "Pet", py::dynamic_attr()); // not auto destruction
    pet.def(py::init<>())
        .def(py::init<const std::string &, const Pet::Kind, const Pet::Attributes &>())
        .def_property("name", &Pet::getName, overload_cast_<const std::string &>()(&Pet::set))
        .def_property("kind", &Pet::getKind, overload_cast_<const Pet::Kind>()(&Pet::set))
        .def_property("attrs", &Pet::getAttributes, overload_cast_<const Pet::Attributes &>()(&Pet::set))
        .def("getName", &Pet::getName)
        .def("getKind", &Pet::getKind)
        .def("getAttributes", &Pet::getAttributes)
        // .def("set", static_cast<void (Pet::*)(const std::string &)>(&Pet::set), "Set the pet's name")
        // .def("set", static_cast<void (Pet::*)(const Pet::Kind)>(&Pet::set), "Set the pet's kind")
        // .def("set", static_cast<void (Pet::*)(const Pet::Attributes &)>(&Pet::set), "Set the pet's attrs")
        .def("set", overload_cast_<const std::string &>()(&Pet::set), "Set the pet's name")
        .def("set", overload_cast_<const Pet::Kind>()(&Pet::set), "Set the pet's kind")
        .def("set", overload_cast_<const Pet::Attributes &>()(&Pet::set), "Set the pet's attributes")
        // .def("set", py::overload_cast<const std::string &>(&Pet::set), "Set the pet's name") // C++14
        // .def("set", py::overload_cast<const int>(&Pet::set), "Set the pet's age") // C++14
        // .def("set", py::overload_cast<const Pet::Attributes &>(&Pet::set), "Set the pet's attributes") // C++14
        .def("__repr__", [](const Pet &_p) 
        {
             return "<example.Pet named " + _p.getName() + ", kind " + std::to_string((int)_p.getKind()) 
                + ", attrs {'age': " + std::to_string(_p.getAttributes().age) + "}>";
        });

    py::enum_<Pet::Kind>(pet, "Kind")
        .value("Dog", Pet::Kind::Dog)
        .value("Cat", Pet::Kind::Cat)
        .export_values();

    py::class_<Pet::Attributes>(pet, "Attributes")
        .def(py::init<const float>())
        .def_readwrite("age", &Pet::Attributes::age)
        .def("__repr__", [](const Pet::Attributes &_attr)
        {
            return "{'age': " + std::to_string(_attr.age) + "}";
        });

    py::class_<Dog, Pet>(m, "Dog")
        .def(py::init<>())
        .def(py::init<const std::string &, const Pet::Kind, const Pet::Attributes &>())
        .def("bark", &Dog::bark);
}

#if 0
class Animal 
{   
public:       
    virtual ~Animal() {}

    virtual std::string go(int n_times) = 0;
    virtual std::string name() 
    { 
        return "unknown"; 
    }
};      

class Dog : public Animal 
{   
public:       
    std::string go(int n_times) override
    {           
        std::string result;
        for (int i=0; i<n_times; ++i)
            result += bark() + " ";
        return result;
    }

    virtual std::string bark()
    { 
        return "woof!";
    } 
};

class Husky : public Dog {};

class PyAnimal : public Animal 
{   
public:       
    /* Inherit the constructors */
    using Animal::Animal;

    /* Trampoline (need one for each virtual function) */
    std::string go(int n_times) override 
    {           
        PYBIND11_OVERRIDE_PURE(
            std::string, /* Return type */
            Animal,      /* Parent class */
            go,          /* Name of function in C++ (must match Python name) */
            n_times      /* Argument(s) */
        );
    }

    std::string name() override 
    { 
        PYBIND11_OVERRIDE(std::string, Animal, name, ); 
    }   
};

class PyDog : public Dog 
{   
public:       
    using Dog::Dog; // Inherit constructors

    std::string go(int n_times) override
    { 
        PYBIND11_OVERRIDE(std::string, Dog, go, n_times);
    }

    std::string name() override
    { 
        PYBIND11_OVERRIDE(std::string, Dog, name, );
    }

    std::string bark() override
    {
        PYBIND11_OVERRIDE(std::string, Dog, bark, );
    }
};

class PyHusky : public Husky 
{   
public:       
    using Husky::Husky; // Inherit constructors
 
    std::string go(int n_times) override 
    { 
        PYBIND11_OVERRIDE_PURE(std::string, Husky, go, n_times);
    }       
    
    std::string name() override 
    { 
        PYBIND11_OVERRIDE(std::string, Husky, name, );
    }       
    
    std::string bark() override 
    { 
        PYBIND11_OVERRIDE(std::string, Husky, bark, ); 
    }   
};
  
std::string call_go(Animal *animal) 
{       
    return animal->go(3);   
}  

PYBIND11_MODULE(example, m) 
{       
    py::class_<Animal, PyAnimal /* <--- trampoline*/>(m, "Animal")           
        .def(py::init<>())           
        .def("go", &Animal::go);          
    py::class_<Dog, Animal, PyDog>(m, "Dog")
        .def(py::init<>());          
    m.def("call_go", &call_go);
}

from example import *
d = Dog()
call_go(d)   'woof! woof! woof! '
class Cat(Animal):
def go(self, n_times): 
    return "meow! " * n_times
c = Cat()
call_go(c)   'meow! meow! meow! '
class Dachshund(Dog):       
    def __init__(self, name):           
        Dog.__init__(self)  # Without this, a TypeError is raised.           
        self.name = name          
    def bark(self):           
        return "yap!"

// using template trampoline
template <class AnimalBase = Animal> 
class PyAnimal : public AnimalBase 
{   
public:       
    using AnimalBase::AnimalBase; // Inherit constructors
  
    std::string go(int n_times) override
    { 
        PYBIND11_OVERRIDE_PURE(std::string, AnimalBase, go, n_times);
    }
 
    std::string name() override
    { 
        PYBIND11_OVERRIDE(std::string, AnimalBase, name, );
    }
};   

template <class DogBase = Dog>
class PyDog : public PyAnimal<DogBase>
{
public:
    using PyAnimal<DogBase>::PyAnimal; // Inherit constructors
    // Override PyAnimal's pure virtual go() with a non-pure one:
    std::string go(int n_times) override
    { 
        PYBIND11_OVERRIDE(std::string, DogBase, go, n_times); 
    }
     
    std::string bark() override
    { 
        PYBIND11_OVERRIDE(std::string, DogBase, bark, );
    }
};

PYBIND11_MODULE(example, m) 
{
    py::class_<Animal, PyAnimal<>> animal(m, "Animal");   
    py::class_<Dog, Animal, PyDog<>> dog(m, "Dog");   
    py::class_<Husky, Dog, PyDog<Husky>> husky(m, "Husky");   // ... add animal, dog, husky definitions
}

class ShiMin(Dog):
    def bark(self):
        return "yip!"
#endif