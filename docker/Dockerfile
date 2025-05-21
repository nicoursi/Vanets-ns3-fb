FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    libboost-all-dev \
    libcgal-dev \
    libsqlite3-dev \
    libgtk-3-dev \
    libgsl-dev \
    pkg-config \
    libxml2-dev \
    git \
    wget \
    ca-certificates \
    && apt-get clean
