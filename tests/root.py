import os
import sys

abs_path: list = os.path.abspath(__file__).split(os.sep)
root_path: str = (
    abs_path[0] + os.sep + abs_path[1] + os.sep
    if len(abs_path) >= 2
    else abs_path[0] + os.sep
)


def root():
    os.chdir(root_path)
    sys.path.insert(0, root_path)


if __name__ == "__main__":
    print(root_path)
