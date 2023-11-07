

import os
from pathlib import Path
import shutil
import time
import re
import platform
import getpass
import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, wait, ALL_COMPLETED
import asyncio

import httpx
import py7zr

from modules.downloader import DownloadFile

proxy_flag = False
proxy = "http://127.0.0.1:7890" if proxy_flag else None
proxies = {
    "http": proxy,
    "https": proxy
} if proxy_flag else None
timeout = 30
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60"
}

httpx_session = httpx.Client(http2=False, proxies=proxies)
httpx_session.headers = {"author": "lgf"}


def find_url(string): 
    # findall() 查找匹配正则表达式的所有网址集合
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url 

async def get_async_request(client, url: str, file_name: str, proxy_type: str, client_type: str):
    print("正在爬取 url: ",url)
    if client_type == "httpx":
        print("当前使用httpx, proxy已经添加在client中")
        res = await client.get(url=url, headers=headers, timeout=timeout) 
        text = res.text
    else:
        print("当前使用aiohttp, proxy需要添加到如下的get请求中, proxy的值为: ", proxy)
        res = await client.get(url=url, headers=headers, proxy=proxy)
        text = await res.text(encoding="utf-8")
        # json = await resp.json()
        # content = await res.read()
    # print(text)
    ext = url.split("/")[-1].split(".")[-1]
    with open(f"./all_proxy_config_file/{proxy_type}/{file_name}.{ext}", "w", encoding='utf-8') as f:
        f.write(text)

def get_status_code(url):
    res = httpx.get(url=url, headers=headers, timeout=timeout, proxies=proxies)
    print(res.status_code)
    
def get_httpx(url):
    res = httpx.get(url=url, headers=headers, timeout=timeout, proxies=proxies)
    print(res.text)

def get_httpx_with_session(url):
    res = httpx_session.get(url=url, headers=headers, timeout=timeout)
    print(res.text)
    
async def get_async_httpx(url, num):
    print("启动httpx异步请求",num)
    async with httpx.AsyncClient(http2=False, proxies=proxies) as client:
        res = await client.get(url=url, headers=headers, timeout=timeout)
        print(res.text)

async def async_httpx_test(url, num):
    tasks = [asyncio.create_task(get_async_httpx(url, num)) for _ in range(num)]
    await asyncio.gather(*tasks)

async def async_httpx_once_client(urls_list, proxy):
    async with httpx.AsyncClient(http2=False, proxies=proxy) as client:
        tasks = [asyncio.create_task(get_async_request(client=client, url=url, file_name=file_name, proxy_type=proxy_type, client_type="httpx")) for (file_name, proxy_type, url) in urls_list]
        await asyncio.gather(*tasks)



if __name__ == '__main__':
    start_time = time.time()
    
    gh_proxy_download_url = [
                                ['https://gh.h233.eu.org/https://github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [@X.I.U/XIU2] 提供'],
                                ['https://gh.api.99988866.xyz/https://github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [hunshcn/gh-proxy] 提供'],
                                ['https://gh.ddlc.top/https://github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [@mtr-static-official] 提供'],
                                ['https://gh2.yanqishui.work/https://github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [@HongjieCN] 提供'],
                                ['https://ghdl.feizhuqwq.cf/https://github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [feizhuqwq.com] 提供'],
                                ['https://gh-proxy-misakano7545.koyeb.app/https://github.com', '美国', '[美国 Cloudflare CDN]'],
                                ['https://gh.flyinbug.top/gh/https://github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [Mintimate] 提供'],
                                ['https://github.91chi.fun/https://github.com', '美国', '[美国 Cloudflare CDN]'],
                                ['https://slink.ltd/https://github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [知了小站] 提供'],
                                ['https://git.xfj0.cn/https://github.com', '美国', '[美国 Cloudflare CDN]'],
                                ['https://gh.con.sh/https://github.com', '美国', '[美国 Cloudflare CDN]'],
                                ['https://ghps.cc/https://github.com', '美国', '[美国 Cloudflare CDN]'],
                                ['https://cors.isteed.cc/github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [Lufs\'s] 提供'],
                                ['https://hub.gitmirror.com/https://github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [GitMirror] 提供'],
                                ['https://js.xxooo.ml/https://github.com', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [饭太硬] 提供'],
                                ['https://proxy.freecdn.ml/?url=https://github.com', '美国', '[美国 Cloudflare CDN]'],
                                ['https://cdn.githubjs.cf', '美国', '[美国 Cloudflare CDN]'],
                                ['https://download.njuu.cf', '美国', '[美国 拉斯维加斯] - 该公益加速源由 [LibraryCloud] 提供'],
                                ['https://download.yzuu.cf', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [LibraryCloud] 提供'],
                                ['https://download.nuaa.cf', '美国', '[美国 Cloudflare CDN] - 该公益加速源由 [LibraryCloud] 提供'],
                                ['https://download.fastgit.org', '德国', '[德国] - 该公益加速源由 [FastGit] 提供&#10;&#10;提示：如果速度可以接受，希望大家尽量多使用前面的美国节点（每次随机 4 个来负载均衡），&#10;避免流量都集中到亚洲公益节点，减少成本压力才能运营更持久~', 'https://archive.fastgit.org'],
                                ['https://ghproxy.com/https://github.com', '韩国', '[日本、韩国、德国等]（CDN 不固定） - 该公益加速源由 [ghproxy] 提供&#10;&#10;提示：如果速度可以接受，希望大家尽量多使用前面的美国节点（每次随机 4 个来负载均衡），&#10;避免流量都集中到亚洲公益节点，减少成本压力才能运营更持久~'],
                                ['https://kgithub.com', '新加坡', '[新加坡] - 该公益加速源由 [KGitHub] 提供&#10;&#10;提示：如果速度可以接受，希望大家尽量多使用前面的美国节点（每次随机 4 个来负载均衡），&#10;避免流量都集中到亚洲公益节点，减少成本压力才能运营更持久~']
                            ]
    zips_name = ["ChromeGo.7z","ChromeGoMac.tar.gz","EdgeGo.7z","FirefoxFQ.7z","FirefoxFqLinux.tar.gz"]
    # "https://github.com/bannedbook/fanqiang/releases/download/ChromeGo-latest/ChromeGo.7z", https://kgithub.com/bannedbook/fanqiang/releases/download/ChromeGo-latest/ChromeGo.7z
    common_path = "bannedbook/fanqiang/releases/download/ChromeGo-lates/"
    zip_url = "https://ghproxy.com/https://github.com/bannedbook/fanqiang/releases/download/ChromeGo-latest/ChromeGo.7z" if getpass.getuser() == "lgf" else "https://github.com/bannedbook/fanqiang/releases/download/ChromeGo-latest/ChromeGo.7z"
    print(zip_url)
    proxy_url_map = {
        "us1": "https://ghdl.feizhuqwq.cf/https://github.com/",
        "us2": "https://gh.con.sh/https://github.com/",
        "us3": "https://gh.h233.eu.org/https://github.com/",
        "us4": "https://download.yzuu.cf/",
        "singapore": "https://kgithub.com/",
        "korean": "https://ghproxy.com/https://github.com/",
        "github": "https://github.com/"
    }
    url = "http://httpbin.org/forms/post"
    
    
    
    # run_test = async_httpx_once_test(url, proxy, 10)
    # asyncio.run(run_test)
    # get_status_code(zip_url)
    
    # chromego_download_url = "https://ghproxy.com/https://github.com/bannedbook/fanqiang/releases/download/ChromeGo-latest/ChromeGo.7z" if getpass.getuser() == "lgf" else "https://github.com/bannedbook/fanqiang/releases/download/ChromeGo-latest/ChromeGo.7z"
    # data_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'downlaod')
    # thread_num = 20
    # downloader = DownloadFile(chromego_download_url, data_folder, thread_num)
    # downloader.run()
    
    # BUG: py7zr.exceptions.UnsupportedCompressionMethodError: (b'\x03\x03\x01\x1b', 'BCJ2 filter is not supported by py7zr. Please consider to contribute to XZ/liblzma project and help Python core team implementing it. Or please use another tool to extract it.')
    # with py7zr.SevenZipFile('./downlaod/ChromeGo.7z', mode='r') as z:
    #     z.extractall("./downlaod")
    
    # shutil.register_unpack_format('7zip', ['.7z'], py7zr.unpack_7zarchive)
    # shutil.unpack_archive('./downlaod/ChromeGo.7z', "./downlaod")
    
    # proxy_types = ["clash.meta","clashB","hysteria","hysteria2","naiveproxy","singbox","v2go","v2rayB","Xray"]
    path = Path('./downlaod/ChromeGo/')
    proxy_paths = [e for e in path.iterdir() if (e.is_dir() and "Browser" not in str(e) and "chrome-user-data" not in str(e))]
    
    proxy_urls_map = {}
    proxy_urls_tuple_list = []
    for proxy_path in proxy_paths:
        proxy_type = str(proxy_path).replace(str(path),"").replace("/","").replace("\\","")
        ip_bat_path = Path(f"./downlaod/ChromeGo/{proxy_type}/","ip_Update/")
        proxy_urls = []
        if os.path.exists(ip_bat_path):
            for file in os.listdir(ip_bat_path):
                if file.endswith(".bat"):
                    file_name = file.split(".")[0]
                    with open(Path(ip_bat_path, file), 'r') as f:
                        # print(f.read())
                        ip_data = f.read()
                        # print("Urls: ", find_url(ip_data))
                        ip_urls = find_url(ip_data)
                        if len(ip_urls) > 0 and (not ip_urls[0].endswith(".md")):
                            proxy_urls.append(ip_urls[0])
                            proxy_urls_tuple_list.append((file_name, proxy_type, ip_urls[0]))
        if len(proxy_urls) > 0:
            proxy_urls_map[proxy_type] = proxy_urls
        
    # print(proxy_urls_map)
    json_data = json.dumps(proxy_urls_map, sort_keys=True, indent=2, separators=(',', ':'))
    print(json_data)
    print(proxy_urls_tuple_list)
    with open("all_proxy_config_urls.json", "w") as f:
        f.write(json_data)
        
    
    asyncio.run(async_httpx_once_client(proxy_urls_tuple_list, proxy))
    
    
    
    end_time = time.time()
    print("总共耗时: ", end_time-start_time) 










































































































