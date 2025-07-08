from setuptools import find_packages,setup

from typing import List

def get_requirements()->list[str]:
    """
    This function returns a list of required packages for the project.
    """
    requirement_list: List[str]=[]
    try:
        with open("requirements.txt", "r") as file:
            lines = file.readlines()

            for line in lines:
                requirement= line.strip()
                if requirement and requirement!='-e .':
                    requirement_list.append(requirement)
    except FileNotFoundError:
        print("requirements.txt filen not found.")


    return requirement_list
print (get_requirements())

setup(
    name = "AI-TRAVEL-PLANNER",
    version = "0.0.1",
    author = "Sarthak Bhalla",
    author_email = "sarthakbhalla@gmail.com",
    packages = find_packages(),
    install_requires = get_requirements(),

)

                   