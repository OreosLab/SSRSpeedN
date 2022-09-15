from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def download_resource(url, headers, path):
    print(f"正在下载: {url}")
    with open(file=path, mode="wb") as f:
        data = requests.get(url=url, headers=headers).content
        f.write(data)
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
        for each in response["assets"]:
            if each["name"] in url_info["files"]:
                file_info.append(
                    {
                        "url": proxy + each["browser_download_url"],
                        "path": f"{work_dir}{each['name']}",
                    }
                )
    with ThreadPoolExecutor() as pool:
        for each in file_info:
            task_list.append(
                pool.submit(
                    download_resource,
                    url=each["url"],
                    headers=headers,
                    path=each["path"],
                )
            )
    for each in as_completed(task_list):
        print(each.result())
    sys.exit(0)
