#!/bin/sh
docker build -t ompugao/blinkyoureyes:release --target=release .
docker build -t ompugao/blinkyoureyes:debug --target=debug .
