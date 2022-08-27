import os
import sys

_ = os.sep
abs_path: list = os.path.abspath(__file__).split(_)
root_path: str = _.join(abs_path[0:-2]) + _


def root():
    os.chdir(root_path)
    sys.path.insert(0, root_path)


if __name__ == "__main__":
    print(root_path)
