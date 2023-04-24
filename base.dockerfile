FROM ubuntu:22.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        git \
        autoconf \
        automake \
        autotools-dev \
        curl \
        libmpc-dev \
        libmpfr-dev \
        libgmp-dev \
        gawk \
        build-essential \
        bison \
        flex \
        texinfo \
        gperf \
        libtool \
        patchutils \
        bc \
        zlib1g-dev \
        libexpat-dev \
        ninja-build \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /repos

RUN git clone https://github.com/riscv/riscv-gnu-toolchain \
    && cd riscv-gnu-toolchain \
    && ./configure --prefix=/opt/riscv --with-arch=rv32im --with-abi=ilp32 \
    && make \
    && rm -r /repos/*

ENV PATH $PATH:/opt/riscv/bin

WORKDIR /opt
