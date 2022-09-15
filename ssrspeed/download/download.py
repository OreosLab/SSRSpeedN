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


def download_resource(url, headers, name, size, position, path, cols):
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
    ) as bar, open(file=path, mode="wb") as f:
        content = requests.get(url=url, headers=headers, stream=True).iter_content(
            chunk_size=1024
        )
        for chunk in content:
            length = f.write(chunk)
            bar.update(length)
    return f"已保存至: {path}"


def download(download_type, platform, download_path=None):
    _ = os.sep
    urls_info = []
    task_list = []
    file_info = []
    proxy = "https://ghproxy.com/"
    if download_path is None:
        download_path = os.getcwd()
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
        "Chrome/64.0.3282.119 Safari/537.36 ",
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
        urls_info.append(client_file_info[platform])
        urls_info.append(database_file_info)
    elif download_type == "database":
        urls_info.append(database_file_info)
    elif download_type == "client":
        urls_info.append(client_file_info[platform])
    for url_info in urls_info:
        response = requests.get(url=url_info["url"], headers=headers).json()
        for index, each in enumerate(response["assets"], 1):
            if each["name"] in url_info["files"]:
                file_info.append(
                    {
                        "url": proxy + each["browser_download_url"],
                        "name": each["name"],
                        "size": each["size"],
                        "position": index,
                        "path": f"{work_dir}{each['name']}",
                    }
                )
    os.system("clear" if os.name == "posix" else "cls")
    print(banner)
    with ThreadPoolExecutor() as pool:
        for kwargs in file_info:
            task_list.append(
                pool.submit(
                    download_resource,
                    **kwargs,
                    headers=headers,
                    cols=terminal_size[0],
                )
            )
        done, pending = wait(task_list)
        print("\n")
        for each in done:
            print(each.result())
    sys.exit(0)
