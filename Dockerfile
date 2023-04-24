FROM serodioj/riscv-toolchain:latest

WORKDIR /simulator

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY project .
