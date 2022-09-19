import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, wait

import requests
from tqdm import tqdm

from ssrspeed import __banner__ as banner


def get_terminal_size(platform):
    if platform == "Windows":
        width, height = shutil.get_terminal_size()
    else:
        try:
            width, height = os.get_terminal_size(sys.stdin.fileno())
        except (AttributeError, ValueError, OSError):
            try:
                width, height = os.get_terminal_size(sys.stdout.fileno())
            except (AttributeError, ValueError, OSError):
                width, height = (80, 25)
    return width, height


def mkdir(data_dir):
    if os.path.exists(data_dir):
        if os.path.isfile(data_dir):
            os.remove(data_dir)
            os.makedirs(data_dir)
    else:
        os.makedirs(data_dir)


def download_resource(url, headers, name, size, position, path, cols):
    current_file_size = 0
    with tqdm(
        desc=name,
        total=size,
        unit="b",
        position=position,
        colour="GREEN",
        ascii=True,
        leave=False,
        unit_scale=True,
        ncols=cols - 10,
    ) as dbar:
        if os.path.exists(path):
            current_file_size = os.path.getsize(path)
            if current_file_size == size:
                return f"已保存至: {path}"
            dbar.update(current_file_size)
        with open(file=path, mode="ab") as f:
            try:
                while True:
                    headers.update({"Range": f"bytes={current_file_size}-{size}"})
                    content = requests.get(
                        url=url, headers=headers, timeout=10, stream=True
                    ).iter_content(chunk_size=1024)
                    for chunk in content:
                        length = f.write(chunk)
                        dbar.update(length)
                        current_file_size += length
                    if current_file_size == size:
                        break
            except requests.exceptions.RequestException:
                print(f"{name} 下载异常，正在重新下载")
    return f"已保存至: {path}"


def download(download_type, platform, download_path=None):
    _ = os.sep
    urls_info = []
    task_list = []
    file_info = []
    proxy = "https://ghproxy.com/"
    if download_path is None:
        download_path = os.getcwd()
    mkdir(download_path)
    work_dir = download_path if download_path.endswith(_) else download_path + _
    terminal_size = get_terminal_size(platform)
    client_resources_url = (
        "https://api.github.com/repos/OreosLab/SSRSpeedN/releases/latest"
    )
    database_resources_url = (
        "https://api.github.com/repos/P3TERX/GeoLite.mmdb/releases/latest"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/64.0.3282.119 Safari/537.36 "
    }
    client_file_info = {
        "Windows": {"url": client_resources_url, "files": ["clients_win_64.zip"]},
        "Linux": {"url": client_resources_url, "files": ["clients_linux_amd64.zip"]},
        "MacOS": {"url": client_resources_url, "files": ["clients_darwin_64.zip"]},
    }
    database_file_info = {
        "url": database_resources_url,
        "files": ["GeoLite2-City.mmdb", "GeoLite2-ASN.mmdb"],
    }

    if download_type == "all":
        urls_info.extend((client_file_info[platform], database_file_info))
    elif download_type == "client":
        urls_info.append(client_file_info[platform])
    elif download_type == "database":
        urls_info.append(database_file_info)
    for url_info in urls_info:
        response = requests.get(url=url_info["url"], headers=headers, timeout=10).json()
        file_info.extend(
            {
                "url": f"{proxy}{each['browser_download_url']}",
                "name": each["name"],
                "size": each["size"],
                "position": index,
                "path": f"{work_dir}{each['name']}",
            }
            for index, each in enumerate(response["assets"], 1)
            if each["name"] in url_info["files"]
        )
    os.system("clear" if os.name == "posix" else "cls")
    print(banner)
    with ThreadPoolExecutor() as pool:
        task_list.extend(
            pool.submit(
                download_resource, **kwargs, headers=headers, cols=terminal_size[0]
            )
            for kwargs in file_info
        )

        done, _ = wait(task_list)
        print("\n")
        for each in done:
            print(each.result())
    sys.exit(0)


if __name__ == "__main__":
    download(download_type="all", platform="Windows")
