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

* UDP NAT Type

  ```text
  Full-cone NAT                              全锥形 NAT
  Symmetric NAT                              对称型 NAT
  Restricted Cone NAT                        限制锥形 NAT (IP 受限)                                                                                                                       
  Port-Restricted Cone NAT                   端口限制锥形 NAT (IP 和端口都受限)
  Blocked                                    未开启UDP

  其中全锥型的穿透性最好，而对称型的安全性最高，如果要使用代理打游戏，节点的 UDP NAT 类型最好为全锥型，其次为对称型，尽量不要用其他 NAT 类型的节点玩游戏
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

其他平台需要测试，欢迎反馈

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

可选参数:
  -h, --help            输出帮助信息并退出
  --version             输出版本号并退出
  -c GUICONFIG, --config=GUICONFIG

                        通过节点配置文件加载节点信息.

  -u URL, --url=URL     通过节点订阅链接加载节点信息.
  -mc MAX_CONNECTIONS, --max-connections=MAX_CONNECTIONS

                        最大连接数。某些机场不支持并发连接，可设置为 1.
                        
  -m TEST_METHOD, --method=TEST_METHOD

                        在 [speedtestnet, fast, socket, stasync] 中选择测试方法.

  -M TEST_MODE, --mode=TEST_MODE

                        在 [default, pingonly, stream, all, wps] 中选择测试模式.  
                        
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
  --paolu               删除项目所有文件.
```

使用样例 :

```powershell
python -m ssrspeed -c gui-config.json -M stream --include 韩国 --include-remark Azure --include-group YoYu
python -m ssrspeed -u "https://home.yoyu.dev/subscriptionlink" --include 香港 Azure --include-group YoYu --exclude Azure
```

## 自由配置

* **修改测速内容**

  在 `ssrspeed.json` 文件下第 15 行至第 31 行，默认允许。

  ```jsonc
    "fastSpeed": false,  // 是否开启快速测速
    "ntt": { "enabled": true, "internal_ip": "0.0.0.0", "internal_port": 54320 }, // UDP 类型测试
    "geoip": true,       // 是否测 GeoIP, 包括 Inbound & Outbound
    "ping": true,        // 是否测 ping
    "gping": true,       // 是否测 Google ping
    "stream": true,      // 是否测流媒体解锁
    "speed": true,       // 是否测速
    "method": "SOCKET",  // 测速方式，SOCKET / YOUTUBE / NETFLIX
    "StSpeed": true,     // 是否同时测单线程/多线程
    "netflix": true,     // 是否测 Netflix 解锁
    "hbo": true,         // 是否测 HBO max 解锁
    "disney": true,      // 是否测 Disney+ 解锁
    "youtube": true,     // 是否测 YouTube premium 解锁
    "abema": true,       // 是否测 Abema 解锁
    "bahamut": true,     // 是否测 Bahamut (动画疯) 解锁
    "dazn": true,        // 是否测 Dazn 解锁
    "tvb": true,         // 是否测 My tvsuper 解锁
    "bilibili": true,    // 是否测 Bilibili 解锁
  ```

* **修改结果输出**

  ```jsonc
    "port": true,       // 是否输出端口
    "multiplex": true,  // 是否输出复用检测
    "exportResult": {
        "addition": "测速频道：@Cheap_Proxy",   // 自定义附加信息
        "uploadResult": false,
        "hide_max_speed": false,               // 是否隐藏最高速度
        "font": "SourceHanSansCN-Medium.otf",  // 自定义字体，见下方说明
        "colors": [                            // 自定义配色，见下方说明
            {
                "name": "origin",
                "colors": {
                    "4.0": [102, 255, 102],
                    "8.0": [255, 255, 102],
                    "16.0": [255, 178, 102],
                    "24.0": [255, 102, 102],
                    "32.0": [226, 140, 255],
                    "40.0": [102, 204, 255],
                    "50.0": [102, 102, 255]
                }
            },
            {
                "name": "poor",
                "colors": {
                    "4.0": [255, 215, 0],
                    "8.0": [255, 178, 1],
                    "16.0": [252, 105, 114],
                    "24.0": [233, 130, 217],
                    "32.0": [194, 108, 255],
                    "40.0": [102, 192, 255],
                    "50.0": [102, 111, 255]
                }
            }
        ]
    },
  ```

  * **自定义附加信息**

    修改为你自己的频道或群组等信息

  * **自定义字体**

    下载字体文件放入 `resources/custom/` 文件夹下，修改 `ssrspeed.json` 文件下第 44 行为字体文件名，本项目自带两个字体

  * **自定义颜色**

    采用速度 (MB/s) 对应输出颜色 (RGB 256) 方式

## 项目结构

```tree
SSRSpeedN
├── LICENSE
├── README.md
├── bin
│   ├── ssrspeed.bat
│   ├── ssrspeed.sh
│   └── st.bat
├── data
│   ├── logs
│   │   └── 2022-09-12-19-23-35.log
│   ├── restats
│   ├── results
│   │   ├── 2022-09-12-19-26-02
│   │   └── 2022-09-12-19-26-02.json
│   ├── ssrspeed.example.json
│   ├── ssrspeed.json
│   ├── stats.json
│   ├── stats.svg
│   ├── tmp
│   │   ├── config.json
│   │   ├── test.txt
│   │   └── uploads
│   └── tree.md
├── pyproject.toml
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
│   ├── databases
│   │   ├── GeoLite2-ASN.mmdb
│   │   ├── GeoLite2-City.mmdb
│   │   └── GeoLite2-Country.mmdb
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
├── setup.py
├── ssrspeed
│   ├── __init__.py
│   ├── __main__.py
│   ├── config
│   │   ├── __init__.py
│   │   └── config.py
│   ├── core
│   │   ├── __init__.py
│   │   └── core.py
│   ├── launchers
│   │   ├── __init__.py
│   │   ├── base_client.py
│   │   ├── ss_client.py
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
│   │   ├── render
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
│   ├── type
│   │   ├── __init__.py
│   │   ├── errors
│   │   └── nodes
│   ├── utils
│   │   ├── __init__.py
│   │   ├── b64plus.py
│   │   ├── geoip.py
│   │   ├── platform_check.py
│   │   ├── port_check.py
│   │   ├── pynat.py
│   │   ├── reqs_check.py
│   │   ├── rules
│   │   └── web
│   └── web.py
├── tests
│   ├── __init__.py
│   ├── geoip.py
│   ├── pf
│   ├── print_stats.py
│   ├── root.py
│   ├── spy
│   ├── tree
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
