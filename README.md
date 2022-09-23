# blinkyoureyes

- a tool to help you to blink your eyes
https://youtu.be/JnzDWCNB-94
- [![](https://img.youtube.com/vi/JnzDWCNB-94/0.jpg)](https://www.youtube.com/watch?v=JnzDWCNB-94)
- The icon is taken from [ICOOON MONO](https://icooon-mono.com/00089-%e9%9b%ab%e3%81%ae%e3%82%a2%e3%82%a4%e3%82%b3%e3%83%b3%e7%b4%a0%e6%9d%90/).

## Usage

- Download a binary file from https://github.com/ompugao/blinkyoureyes/releases/latest , install and run it.
	- for linux: `blinkyoureyes`
	- for mac: `blinkyoureyes.zip`
	- for windows: `blinkyoureyes.exe`

## (For linux) Registration to systemd
```bash
mkdir -p ~/.config/systemd/user/
cp -a dist/blinkyoureyes $HOME/install/bin/
cp -a blinkyoureyes.service ~/.config/systemd/user/
cp -a xsession.target ~/.config/systemd/user/
cat .xsessionrc >> ~/.xsessionrc
# start
systemctl --user start blinkyoureyes.service
```
- for your reference: https://superuser.com/questions/759759/writing-a-service-that-depends-on-xorg

## Development
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install pyinstaller pyqt5 ewmh
python3 blinkyoureyes2.py
# to build a binary
pyinstaller --add-data assets:assets -n blinkyoureyes --onefile blinkyoureyes2.py
```
