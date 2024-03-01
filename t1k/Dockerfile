FROM ubuntu:20.04

WORKDIR /app


RUN apt-get update && apt-get -y upgrade && \
	apt-get install -y build-essential wget git curl pigz \
		libncurses5-dev zlib1g-dev libbz2-dev liblzma-dev libcurl3-dev && \
	apt-get clean && apt-get purge && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


#Samtools
RUN wget https://github.com/samtools/samtools/releases/download/1.19.2/samtools-1.19.2.tar.bz2 && \
	tar jxf samtools-1.19.2.tar.bz2 && \
	rm samtools-1.19.2.tar.bz2 && \
	cd samtools-1.19.2 && \
	./configure --prefix $(pwd) && \
	make

ENV PATH /usr/src/samtools-1.9:$PATH


# install t1k
RUN git clone https://github.com/mourisl/T1K.git
WORKDIR /app/T1K
RUN make
RUN perl t1k-build.pl -o hlaidx --download IPD-IMGT/HLA
WORKDIR /app
ENV PATH /app/T1K:$PATH

