# blinkyoureyes

- a tool to help you to blink your eyes
https://youtu.be/2hCUxoMv8vI


[![behaviour](https://img.youtube.com/vi/2hCUxoMv8vI/maxresdefault.jpg)](https://youtu.be/2hCUxoMv8vI)

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
# start
systemctl --user start blinkyoureyes.service
# reference
# https://superuser.com/questions/759759/writing-a-service-that-depends-on-xorg
```
