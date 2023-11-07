#! /usr/bin/sh

sudo apt update && sudo apt upgrade -y
sudo apt install p7zip-full wget curl axel aria2 -y

axel -n 6 https://github.com/bannedbook/fanqiang/releases/download/ChromeGo-latest/ChromeGo.7z -o ./downlaod/ChromeGo.7z
# axel -n 6 https://ghproxy.com/https://github.com/bannedbook/fanqiang/releases/download/ChromeGo-latest/ChromeGo.7z -o ./downlaod/ChromeGo.7z
cd downlaod && 7z x ChromeGo.7z -r && cd ..
