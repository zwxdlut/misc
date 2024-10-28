
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"))

import example
from example import Pet
from example import Dog


def main():
    print("=====================================")

    print(f"add: {example.add(3, 4)}")
    print(f"the_answer = {example.the_answer}")
    print(f"what = {example.what}")

    print("=====================================")

    print(f"Pet.Kind members: {Pet.Kind.__members__}")
    pet = Pet("Molly", Pet.Dog, Pet.Attributes(18))
    print(f"Pet: {pet}")
    print(f"Pet::getName: {pet.getName()}")
    print(f"Pet::getKind: {pet.getKind()}")
    print(f"Pet::getAttributes: {pet.getAttributes()}")
    pet.set("Charly")
    print(f"Pet::set: name = {pet.name}")
    pet.set(Pet.Cat)
    print(f"Pet::set: kind = {pet.kind}")
    pet.set(Pet.Attributes(20))
    print(f"Pet::set attributes = {pet.attrs}")
    print(f"Pet::getName: {pet.getName()}")
    print(f"Pet::getKind: {pet.getKind()}")
    print(f"Pet::getAttributes: {pet.getAttributes()}")
    pet.what = 18
    print(f"Pet::what = {pet.what}")
    print(f"Pet.__dict__ = {pet.__dict__}")

    print("=====================================")

    dog = Dog("Molly", Pet.Dog, Pet.Attributes(20))
    print(f"Dog::bark: {dog.bark()}")


if "__main__" == __name__:
    main()
