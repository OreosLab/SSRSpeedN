@echo off&
set bin=%~dp0
for %%a in ("%bin:~0,-1%") do set SSRSpeed=%%~dpa
set PYTHONPATH=%SSRSpeed%;%PYTHONPATH%
cd %SSRSpeed%
echo.
echo ================== SSRSpeedN ==================
if exist "%SSRSpeed%\venv\Scripts\activate.bat" ( call "%SSRSpeed%\venv\Scripts\activate.bat" )
if defined VIRTUAL_ENV ( echo 当前环境 %VIRTUAL_ENV% ) else ( echo 当前目录 %SSRSpeed% )
if exist "%SystemRoot%\SysWOW64" path %path%;%windir%\SysNative;%SystemRoot%\SysWOW64;%SSRSpeed%
bcdedit >nul
if '%errorlevel%' NEQ '0' ( echo 当前权限 普通用户 ) else ( echo 当前权限 管理员 )
if exist "%SSRSpeed%\resources\clients\v2ray-core\v2ray.exe" ( set v1=1 ) else ( set v1=0 )
set /a v3=v1+v2
if %v3%==2 ( echo 已经安装 V2ray-core ) else ( echo 尚未安装 V2ray-core )
:start
echo ===============================================
echo [1] 开始测速（自定义设置）
echo [2] 首次运行安装 pip 和相关支持（需管理员权限）
echo [3] 参数查阅
echo [4] 当前 SSRSpeed 版本
echo [5] 为本次运行获取管理员权限
echo ===============================================
echo 请选择 [1-5]: 
choice /c 12345
if %errorlevel%==5 ( goto :uac )
if %errorlevel%==4 ( goto :ver )
if %errorlevel%==3 ( goto :help )
if %errorlevel%==2 ( goto :pip )
if %errorlevel%==1 ( goto :test2 )


:pip
if exist "%SystemRoot%\SysWOW64" path %path%;%windir%\SysNative;%SystemRoot%\SysWOW64;%SSRSpeed%
bcdedit >nul
if '%errorlevel%' NEQ '0' ( echo X 当前无管理员权限，无法安装。 && echo. && echo * 您可以通过命令 5 获取权限，或右键以管理员权限启动。 && pause && goto :start ) else ( goto :pip2 )
:pip2
python -m pip install --upgrade pip
pip3 install -r "%SSRSpeed%\requirements.txt"
:: pip3 install aiofiles
:: pip3 install aiohttp-socks
:: pip3 install Flask-Cors
:: pip3 install geoip2
:: pip3 install loguru
:: pip3 install pilmoji
:: pip3 install PySocks
:: pip3 install PyYAML
:: pip3 install requests
:: pip3 install selenium
:: pip3 install webdriver-manager
pause
goto :start

:ver
python -m ssrspeed --version
pause
goto :start

:help
echo.
echo [1] 原文（en）
echo [2] 翻译（zh）
choice /c 12
if %errorlevel%==2 ( goto :fy )
if %errorlevel%==1 ( goto :yw )

:yw

echo.
echo usage: ssrspeed [-h] [--version] [-d DIR] [-u URL] [-i IMPORT_FILE] [-c GUICONFIG] [-mc MAX_CONNECTIONS] [-M {default,pingonly,stream,all,wps}]
echo                 [-m {stasync,socket,speedtestnet,fast}] [--reject-same] [--include FILTER [FILTER ...]] [--include-group GROUP [GROUP ...]]
echo                 [--include-remark REMARKS [REMARKS ...]] [--exclude EFILTER [EFILTER ...]] [--exclude-group EGFILTER [EGFILTER ...]]
echo                 [--exclude-remark ERFILTER [ERFILTER ...]] [-g GROUP_OVERRIDE] [-C RESULT_COLOR] [-s {speed,rspeed,ping,rping}]
echo                 [--skip-requirements-check] [-w] [-l LISTEN] [-p PORT] [--download {all,client,database}] [--debug]
echo.
echo optional arguments:
echo  -h, --help            show this help message and exit
echo  --version             show program's version number and exit
echo  -d DIR, --dir DIR     Specify a work directory with clients and data.
echo  -u URL, --url URL     Load ssr config from subscription url.
echo  -i IMPORT_FILE, --import IMPORT_FILE
echo                        Import test result from json file and export it.
echo  -c GUICONFIG, --config GUICONFIG
echo                        Load configurations from file.
echo  -mc MAX_CONNECTIONS, --max-connections MAX_CONNECTIONS
echo                        Set max number of connections.
echo  -M {default,pingonly,stream,all,wps}, --mode {default,pingonly,stream,all,wps}
echo                        Select test mode in [default, pingonly, stream, all, wps].
echo  -m {stasync,socket,speedtestnet,fast}, --method {stasync,socket,speedtestnet,fast}
echo                        Select test method in [speedtestnet, fast, socket, stasync].
echo  --reject-same         Reject nodes that appear later with the same server and port as before.
echo  --include FILTER [FILTER ...]
echo                        Filter nodes by group and remarks using keyword.
echo  --include-group GROUP [GROUP ...]
echo                        Filter nodes by group name using keyword.
echo  --include-remark REMARKS [REMARKS ...]
echo                        Filter nodes by remarks using keyword.
echo  --exclude EFILTER [EFILTER ...]
echo                        Exclude nodes by group and remarks using keyword.
echo  --exclude-group EGFILTER [EGFILTER ...]
echo                        Exclude nodes by group using keyword.
echo  --exclude-remark ERFILTER [ERFILTER ...]
echo                        Exclude nodes by remarks using keyword.
echo  -g GROUP_OVERRIDE     Manually set group.
echo  -C RESULT_COLOR, --color RESULT_COLOR
echo                        Set the colors when exporting images..
echo  -s {speed,rspeed,ping,rping}, --sort {speed,rspeed,ping,rping}
echo                        Select sort method in [speed, rspeed, ping, rping], default not sorted.
echo  --skip-requirements-check
echo                        Skip requirements check.
echo  -w, --web             Start web server.
echo  -l LISTEN, --listen LISTEN
echo                        Set listen address for web server.
echo  -p PORT, --port PORT  Set listen port for web server.
echo  --download {all,client,database}
echo                        Download resources in ['all', 'client', 'database']
echo  --debug               Run program in debug mode.
echo.
echo  Test Modes
echo  Mode                 Remark
echo  DEFAULT               Freely configurable via ssrspeed.json
echo  TCP_PING              Only tcp ping, no speed test
echo  STREAM                Only streaming unlock test
echo  ALL                   Full speed test (exclude web page simulation)
echo  WEB_PAGE_SIMULATION   Web page simulation test
echo.
echo  Test Methods
echo  Methods              Remark
echo  ST_ASYNC              Asynchronous download with single thread
echo  SOCKET                Raw socket with multithreading
echo  SPEED_TEST_NET        Speed Test Net speed test
echo  FAST                  Fast.com speed test
echo.
pause
goto :start

:fy

echo.
echo 用法：ssrspeed [-h] [--version] [-d DIR] [-u URL] [-i IMPORT_FILE] [-c GUICONFIG] [-mc MAX_CONNECTIONS] [-M {default,pingonly,stream,all,wps}]
echo               [-m {stasync,socket,speedtestnet,fast}] [--reject-same] [--include FILTER [FILTER ...]] [--include-group GROUP [GROUP ...]]
echo               [--include-remark REMARKS [REMARKS ...]] [--exclude EFILTER [EFILTER ...]] [--exclude-group EGFILTER [EGFILTER ...]]
echo               [--exclude-remark ERFILTER [ERFILTER ...]] [-g GROUP_OVERRIDE] [-C RESULT_COLOR] [-s {speed,rspeed,ping,rping}]
echo               [--skip-requirements-check] [-w] [-l LISTEN] [-p PORT] [--download {all,client,database}] [--debug]
echo.
echo 可选参数：
echo.
echo  -h, --help            输出帮助信息并退出
echo  --version             输出版本号并退出
echo  -d DIR, --dir DIR     指定包含 clients 和 data 的目录，默认为当前目录.
echo  -u URL, --url URL     通过节点订阅链接加载节点信息.
echo  -i IMPORT_FILE, --import IMPORT_FILE
echo                        根据 json 文件输出测试结果.
echo  -c GUICONFIG, --config GUICONFIG
echo                        通过节点配置文件加载节点信息.
echo  -mc MAX_CONNECTIONS, --max-connections MAX_CONNECTIONS
echo                        设置最大连接数。某些机场不支持并发连接，可设置为 1.
echo  -M {default,pingonly,stream,all,wps}, --mode {default,pingonly,stream,all,wps}
echo                        在 [default, pingonly, stream, all, wps] 中选择测试模式.
echo  -m {stasync,socket,speedtestnet,fast}, --method {stasync,socket,speedtestnet,fast}
echo                        在 [stasync, socket, speedtestnet, fast] 中选择测试方法.
echo  --reject-same         只保留相同服务器和端口第一次出现的节点.
echo  --include FILTER [FILTER ...]
echo                        通过节点标识和组名筛选节点.
echo  --include-group GROUP [GROUP ...]
echo                        通过组名筛选节点.
echo  --include-remark REMARKS [REMARKS ...]
echo                        通过节点标识筛选节点.
echo  --exclude EFILTER [EFILTER ...]
echo                        通过节点标识和组名排除节点.
echo  --exclude-group EGFILTER [EGFILTER ...]
echo                        通过组名排除节点.
echo  --exclude-remark ERFILTER [ERFILTER ...]
echo                        通过节点标识排除节点.
echo  -g GROUP_OVERRIDE     自定义测速组名.
echo  -C RESULT_COLOR, --color RESULT_COLOR
echo                        设定测速结果展示配色.
echo  -s {speed,rspeed,ping,rping}, --sort {speed,rspeed,ping,rping}
echo                        选择节点排序方式 [按速度排序 / 速度倒序 / 按延迟排序 / 延迟倒序]，默认不排序.
echo  --skip-requirements-check
echo                        跳过确认.
echo  -w, --web             启动网络服务器.
echo  -l LISTEN, --listen LISTEN
echo                        设置网络服务器的监听地址.
echo  -p PORT, --port PORT  设置网络服务器的监听端口.
echo  --download {all,client,database}
echo                        在 [all, client, database] 中选择下载资源类型.
echo  --debug               采用 debug 模式.
echo.
echo  测试模式
echo  模式                 备注
echo  DEFAULT               可以通过 ssrspeed.json 自由配置
echo  TCP_PING              仅 tcp ping，无速度测试
echo  STREAM                仅流媒体解锁测试
echo  ALL                   全速测试（不包括网页模拟）
echo  WEB_PAGE_SIMULATION   网页模拟测试
echo.
echo  测试方法
echo  方法                 备注
echo  ST_ASYNC              单线程异步下载
echo  SOCKET                具有多线程的原始套接字
echo  SPEED_TEST_NET        SpeedTest.Net 速度测试
echo  FAST                  Fast.com 速度测试
echo.
pause
goto :start

:test2
echo.
echo * 以下自定义选项留空回车即可跳过
echo.
:test3
set /p a="请输入您的订阅链接（不可留空）: "
if "%a%"=="" (
goto :test3
) else (
goto :jx1
)
:jx1
echo.
echo * 以下 2 项可以通过空格分隔关键词
echo.
set /p e="1. 使用关键字通过注释筛选节点: "
set /p i="2. 通过使用关键字的注释排除节点: "
set /p k="3. 请输入测速组名: "
set /p m="4. 导出图像时设置颜色 [origin, poor]，默认 origin: "
set /p n="5. 在 [speed, rspeed, ping, rping] 中选择输入排序方法，默认不排序，如默认请跳过: "
echo.
if "%e%"=="" (
set e= && goto :jx1
) else (
set e=--include-remark %e% && goto :jx1
)
:jx1
if "%i%"=="" (
set i= && goto :jx2
) else (
set i=--exclude-remark %i% && goto :jx2
)
:jx2
if "%k%"=="" (
set k= && goto :jx3
) else (
set k=-g %k% && goto :jx3
)
:jx3
set l=-y && goto :jx4
:jx4
if "%m%"=="" (
set m= && goto :jx5
) else (
set m=-C %m% && goto :jx5
)
:jx5
if "%n%"=="" (
set n= && goto :jx6
) else (
set n=-s %n% && goto :jx6
)
:jx6
set o=--skip-requirements-check && goto :jx7
:jx7
echo python -m ssrspeed -u "%a%" %e% %i% %k% %y% %m% %n%  %o%
echo.
python -m ssrspeed -u "%a%" %e% %i% %k% %y% %m% %n%  %o%
pause
set a=
set e=
set i=
set k=
set y=
set m=
set n=
set o=
goto :start

:uac
echo.
if exist "%SystemRoot%\SysWOW64" path %path%;%windir%\SysNative;%SystemRoot%\SysWOW64;%SSRSpeed%
bcdedit >nul
if '%errorlevel%' NEQ '0' ( goto UACPrompt ) else ( goto UACAdmin )
:UACPrompt
echo 提示：通用依赖安装需要管理员权限（命令 4）
echo.
echo       尝试获取管理员权限，程序将重启
ping -n 3 127.0.0.1>nul && %1 start "" mshta vbscript:createobject("shell.application").shellexecute("""%~0""","::",,"runas",1)(window.close)&exit
exit /B
:UACAdmin
cd /d "%SSRSpeed%"
echo.
echo 已获取管理员权限
echo.
pause
goto :start
