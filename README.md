# blinkyoureyes

- a tool to help you to blink your eyes
https://youtu.be/2hCUxoMv8vI


[![behaviour](https://img.youtube.com/vi/2hCUxoMv8vI/maxresdefault.jpg)](https://youtu.be/2hCUxoMv8vI)

- The icon is taken from [ICOOON MONO](https://icooon-mono.com/00089-%e9%9b%ab%e3%81%ae%e3%82%a2%e3%82%a4%e3%82%b3%e3%83%b3%e7%b4%a0%e6%9d%90/).

## Usage
```bash
# install docker and
bash run.sh
```
## Registration to systemd
```bash
pyinstaller --onefile blinkyoureyes.py
mkdir -p ~/.config/systemd/user/
cp -a dist/blinkyoureyes $HOME/install/bin/
cp -a blinkyoureyes.service ~/.config/systemd/user/
cp -a xsession.target ~/.config/systemd/user/
cat .xsessionrc >> ~/.xsessionrc
# start
systemctl --user start blinkyoureyes.service
# reference
# https://superuser.com/questions/759759/writing-a-service-that-depends-on-xorg
```
