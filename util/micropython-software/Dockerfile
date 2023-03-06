FROM ubuntu:22.04

# Install via https://github.com/micropython/micropython/wiki/Getting-Started
RUN apt-get update && \
    apt-get install -y python3 build-essential libreadline-dev libffi-dev git pkg-config gcc-arm-none-eabi libnewlib-arm-none-eabi

RUN git clone --recurse-submodules https://github.com/micropython/micropython.git /micropython

WORKDIR /micropython/mpy-cross
RUN make

WORKDIR /micropython/ports/unix
RUN make

ENTRYPOINT ["./build-standard/micropython"]
