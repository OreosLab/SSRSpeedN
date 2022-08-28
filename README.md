<h1 align="center">
<img src="https://i.jpg.dog/file/jpg-dog/9160396e547d9abde7ec3199c571aa47.png" alt="SSRSpeedN" width="240">
</h1>
<p align="center">
Batch speed measuring tool based on Shadowsocks(R) and V2Ray
</p>
<p align="center">
  <a href="https://github.com/Oreomeow/SSRSpeedN/tags"><img src="https://img.shields.io/github/tag/Oreomeow/SSRSpeedN.svg"></a>
  <a href="https://github.com/Oreomeow/SSRSpeedN/releases"><img src="https://img.shields.io/github/release/Oreomeow/SSRSpeedN.svg"></a>
  <a href="https://github.com/Oreomeow/SSRSpeedN/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Oreomeow/SSRSpeedN.svg"></a>
</p>

## 注意事项

* 测速及解锁测试仅供参考，不代表实际使用情况，由于网络情况变化、Netflix 封锁及 ip 更换，测速具有时效性

* 本项目使用 [Python](https://www.python.org/) 编写，使用前请完成环境安装
* 首次运行前请执行 `.\bin\ssrspeed` 安装 pip 及相关依赖，也可使用 `pip install -r requirements.txt` 命令自行安装
* `data/logs` 文件夹用于记录测速日志，包含节点的详细信息及测速订阅，非必要请勿泄露
* 执行 `.\bin\ssrspeed` 批处理命令即可测速，测速结果保存在 `data/results` 文件夹下，不过大佬喜欢用命令行测也可以
* 因为需要依赖 Python 环境，且本项目仍在测试阶段，可能存在部分 bug ，可到 [tg 群组](https://t.me/+muGNhnaZglQ0N2Q1) 进行反馈。
* Netflix 解锁测速结果说明:

```text
Full Native             原生全解锁
Full Dns                DNS 全解锁
Only original           仅解锁自制剧
None                    未解锁
其中原生解锁和 DNS 解锁只是解锁方式有区别，实际体验区别不大，在电视端使用时 DNS 解锁可能会提示使用代理。
```

## 主要特性

本项目在原 SSRSpeed (已跑路) 的基础上，集成了如下特性

* 支持单线程 / 多线程同时测速，可以同时反映视频播放 / 多线程下载等场景的节点速度
* 支持 fast.com / YOUTUBE 码率等多种测速方式（仅限 Windows）
* 支持 Netflix 解锁测试，分为 原生全解锁 / DNS 全解锁 / 仅解锁自制剧 / 无解锁 四档
* 支持 流媒体平台 Abema / Bahamut 动画疯 / Bilibili / Dazn / Disney+ / HBO max / My tvsuper / YouTube premium 解锁测试
* 提供配置文件测速模块控制端，可以自由选择是否测速 / 测 ping / 检测流媒体解锁
* 取消原版的大红配色，默认为彩虹配色，并增加了新配色 (poor)
* 增加节点复用检测功能
* 增加实际流量倍率测试功能

## 相关依赖

Python 第三方库 见 `requirements.txt`

Linux 依赖

* [libsodium](https://github.com/jedisct1/libsodium)
* [Shadowsocks-libev](https://github.com/shadowsocks/shadowsocks-libev)
* [Simple-Obfs](https://github.com/shadowsocks/simple-obfs)

## 支持平台

### 已测试平台

1. Windows 10 x64

放过要饭人士，MacOS 和 Linux 属实没钱测 / 懒得测，期待更多后浪反馈

### 理论支持平台

支持 Python 及 Shadowsocks, ShadowsocksR, V2Ray 的平台

### 一定支持平台

支持 SSRSpeedN 的平台

## 测速技巧

### 命令行测速（建议大佬使用）

安装第三方库:

```bash
pip install -r requirements.txt
```

测速主程序及附加选项：

```powershell
python -m ssrspeed
Usage: ssrspeed [options] arg1 arg2...

附加选项:
  --version             输出版本号并退出
  -h, --help            输出帮助信息并退出
  -c GUICONFIG, --config=GUICONFIG

                        通过节点配置文件加载节点信息.

  -u URL, --url=URL     通过节点订阅链接加载节点信息.
  --include             通过节点标识和组名筛选节点.
  --include-remark      通过节点标识筛选节点.
  --include-group       通过组名筛选节点.
  --exclude             通过节点标识和组名排除节点.
  --exclude-group       通过组名排除节点.
  --exclude-remark      通过节点标识排除节点.
  --use-ssr-cs          替换 SSR 内核 ShadowsocksR-libev --> ShadowsocksR-C# (Only Windows)
  -g GROUP              自定义测速组名.
  -y, --yes             跳过节点信息确认（我嫌那玩意太麻烦设成默认了）.
  -C RESULT_COLOR, --color=RESULT_COLOR

                        设定测速结果展示配色.

  -S SORT_METHOD, --sort=SORT_METHOD

                        选择节点排序方式 按速度排序 / 速度倒序 / 按延迟排序 / 延迟倒序
                        [speed, rspeed, ping, rping]，默认不排序.

  -i IMPORT_FILE, --import=IMPORT_FILE

                        提供给不会 p 图的同学，偷偷改结果的 json 文件后重新输出结果.

  --skip-requirements-check

                        跳过确认.

  --debug               采用 debug 模式.
```

使用样例 :

```powershell
python -m ssrspeed -c gui-config.json --include 韩国 --include-remark Azure --include-group YoYu
python -m ssrspeed -u "https://home.yoyu.dev/subscriptionlink" --include 香港 Azure --include-group YoYu --exclude Azure
```

## 自由配置

* **自定义颜色**

  在 `ssrspeed.json` 文件下第 35 行，采用速度（MB/s）对应输出颜色 （RGB 256）方式

* **自定义字体**

  下载字体文件放入 `resources/custom/` 文件夹下，修改 `ssrspeed.json` 文件下第 34 行，本项目自带两个字体

* **自定义附加信息**

  修改 `ssrspeed.json` 文件下第 31 行为你自己的频道或群组等信息

* **修改测速项目**

  在 `ssrspeed.json` 文件下第 12 行及第 19 行，可以设置是否进行 udp 类型及 Netflix 解锁测试，默认允许。在 13-14 行可以分别设置是否进行 ping / Google ping 测试，默认允许，若不进行测试，对应项在测速图上显示为 0

* **修改测速方式**

  在 `ssrspeed.json` 文件下第 18 行，可以设置采用单/多线程测速方式或均速/最高速测速方式，默认为前者

## 详细使用

* 参见 [SSRSpeed N 使用说明](https://gta5cloud.rip/index.php/2021/08/25/ssrspeedn-%e4%bd%bf%e7%94%a8%e8%af%b4%e6%98%8e/)

## 项目结构

```tree
SSRSpeedN
├── LICENSE
├── README.md
├── bin
│   └── ssrspeed.bat
├── data
│   ├── logs
│   │   ├── 2022-08-28-00-31-30.log
│   │   └── 2022-08-28-08-38-41.log
│   ├── results
│   │   ├── 2022-08-28-00-37-34.json
│   │   ├── 2022-08-28-00-37-34.png
│   │   ├── 2022-08-28-08-43-56.json
│   │   └── 2022-08-28-08-43-56.png
│   ├── ssrspeed.example.json
│   ├── ssrspeed.json
│   └── tmp
│       ├── config.json
│       └── tree.md
├── requirements-dev.txt
├── requirements.txt
├── resources
│   ├── clients
│   │   ├── shadowsocks-libev
│   │   ├── shadowsocks-win
│   │   ├── shadowsocksr-libev
│   │   ├── shadowsocksr-win
│   │   ├── trojan
│   │   └── v2ray-core
│   ├── static
│   │   ├── custom
│   │   ├── fonts
│   │   └── logos
│   └── templates
│       ├── 535877f50039c0cb49a6196a5b7517cd.woff
│       ├── 732389ded34cb9c52dd88271f1345af9.ttf
│       ├── index.html
│       ├── index.js
│       ├── manifest.js
│       └── vendor.js
├── ssrspeed
│   ├── __init__.py
│   ├── __main__.py
│   ├── colorlog
│   │   ├── __init__.py
│   │   └── colorlog.py
│   ├── config
│   │   ├── __init__.py
│   │   └── config.py
│   ├── core
│   │   ├── __init__.py
│   │   └── core.py
│   ├── launchers
│   │   ├── __init__.py
│   │   ├── base_client.py
│   │   ├── ss_cilent.py
│   │   ├── ssr_client.py
│   │   ├── trojan_client.py
│   │   └── v2ray_client.py
│   ├── parsers
│   │   ├── __init__.py
│   │   ├── base_configs
│   │   ├── base_parser.py
│   │   ├── clash_parser.py
│   │   ├── config_parser.py
│   │   ├── node_filter
│   │   ├── ss_parser.py
│   │   ├── ss_parsers
│   │   ├── ssr_parser.py
│   │   ├── ssr_parsers
│   │   ├── trojan_parser.py
│   │   ├── v2ray_parser.py
│   │   └── v2ray_parsers
│   ├── paths
│   │   ├── __init__.py
│   │   └── paths.py
│   ├── result
│   │   ├── __init__.py
│   │   ├── exporter.py
│   │   ├── importer
│   │   ├── pusher
│   │   ├── simulator
│   │   └── sorter
│   ├── shell
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   └── web_cli.py
│   ├── speedtest
│   │   ├── __init__.py
│   │   ├── methodology.py
│   │   ├── methods
│   │   └── speed_test.py
│   ├── threadpool
│   │   ├── __init__.py
│   │   ├── abstract_task.py
│   │   ├── task_list.py
│   │   ├── thread_pool.py
│   │   └── work_thread.py
│   ├── types
│   │   ├── __init__.py
│   │   ├── errors
│   │   └── nodes
│   ├── utils
│   │   ├── __init__.py
│   │   ├── b64plus.py
│   │   ├── geo_ip.py
│   │   ├── platform_check.py
│   │   ├── port_check.py
│   │   ├── requirements_check.py
│   │   ├── rules
│   │   └── web
│   └── web.py
├── tests
│   ├── __init__.py
│   ├── root.py
│   ├── trojan_test.py
│   └── wpstest.py
```

## 致谢

* 原作者
  * [NyanChanMeow](https://github.com/NyanChanMeow)
* 原修改版
  * [PauperZ](https://github.com/PauperZ/SSRSpeedN)
* beta 版测试
  * [ChenBilly](https://t.me/ChenBilly)
  * [Duang](https://t.me/duang11212)
  * [万有引力](https://t.me/cloudspeedtest)
* 建议及支持
  * [jiexi](https://t.me/jiexi001)
  * [萌新黑客](https://t.me/yxkumad)
* 赞助
  * [便宜机场测速](https://t.me/cheap_proxy)
