FROM python:3.9.19

RUN apt-get update && apt-get -y install \
    build-essential \
    wget \
    pigz \
    libncurses5-dev \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev


WORKDIR /tmp
RUN wget https://github.com/samtools/samtools/releases/download/1.19.2/samtools-1.19.2.tar.bz2
RUN tar xvjf samtools-1.19.2.tar.bz2 
WORKDIR /tmp/samtools-1.19.2
RUN ./configure --prefix=/usr/local/ && make && make install
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /tmp
RUN wget -O /usr/local/bin/bedtools https://github.com/arq5x/bedtools2/releases/download/v2.31.0/bedtools.static
RUN chmod +x /usr/local/bin/bedtools

WORKDIR /home
