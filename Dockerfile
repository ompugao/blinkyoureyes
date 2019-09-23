FROM alpine:latest as release

MAINTAINER Shohei Fujii<fujii.shohei@gmail.com>

RUN apk --update --no-cache add python3 py3-qt5
COPY blinkyoureyes.py /scripts/blinkyoureyes.py

CMD ["python3", "/scripts/blinkyoureyes.py"]


FROM release as debug
RUN apk --update --no-cache add python3-dev bash
RUN pip3 install --upgrade pip
RUN pip3 install ipython

