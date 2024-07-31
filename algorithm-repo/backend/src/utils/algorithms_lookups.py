import sys, inspect

from src.algorithms import *

def lookup_all_algorithms():
    algorithms = []

    clsmembers = inspect.getmembers(sys.modules["src.algorithms"], inspect.ismodule)
    for algorithm in clsmembers:
        # Get Class
        alg_module = algorithm[1]
        classmembers = inspect.getmembers(alg_module, inspect.isclass)
        for cls in classmembers:
            #print(f"Class: {cls[1]}")
            if not cls[1].__module__ == "src.models.algorithms":
                # Execute things with algorithm
                try:
                    alg = cls[1]()
                except TypeError:
                    #print("Using input_parameters...")
                    alg = cls[1](input_parameters={})
                algorithms.append(alg)
                del alg

    return algorithms

def lookup_algorithm(name: str, input_parameters: dict = {}):
    clsmembers = inspect.getmembers(sys.modules["src.algorithms"], inspect.ismodule)
    for algorithm in clsmembers:
        # Get Class
        alg_module = algorithm[1]
        classmembers = inspect.getmembers(alg_module, inspect.isclass)
        for cls in classmembers:
            #print(f"Class: {cls[1].__name__}")
            if not cls[1].__module__ == "src.models.algorithms":
                # Execute things with algorithm
                #print(cls[1].__name__)
                if name == cls[1].__name__:
                    try:
                        algorithm = cls[1]()
                    except TypeError:
                        #print("Using input_parameters...")
                        algorithm = cls[1](input_parameters=input_parameters)
                    return algorithm
                
    raise ModuleNotFoundError