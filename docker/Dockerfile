FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    gcc-7 g++-7 \
    build-essential \
    python3 \
    python3-pip \
    libboost-all-dev \
    libcgal-dev \
    libsqlite3-dev \
    libgtk-3-dev \
    pkg-config \
    libxml2-dev \
    git \
    wget \
    ca-certificates \
    && apt-get clean

RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 100 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 100
