FROM ubuntu:22.04


ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y \
    build-essential libusb-1.0-0 \
    git wget libncurses-dev flex bison gperf cmake ninja-build ccache libffi-dev libssl-dev \
    python3 python3-pip python3-setuptools python3-serial python3-click python3-cryptography \
    python3-future python3-pyparsing python3-pyelftools python-is-python3


ARG USER
ARG UID
ARG GID

RUN groupadd -g $GID -o $USER
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $USER
USER $USER


WORKDIR /opt

CMD ["bash"]
