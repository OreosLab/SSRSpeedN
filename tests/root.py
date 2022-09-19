import os
import sys

_ = os.sep
file_path: list = os.path.realpath(__file__).split(_)
root_path: str = _.join(file_path[:-2]) + _


def root():
    os.chdir(root_path)
    sys.path.insert(0, root_path)


if __name__ == "__main__":
    print(root_path)
