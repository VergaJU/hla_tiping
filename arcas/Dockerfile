FROM continuumio/miniconda3:latest

WORKDIR /app

# Install Git LFS
RUN apt-get update && \
    apt-get install -y git curl pigz
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
RUN apt-get install -y git-lfs
RUN git lfs install

RUN git clone --branch VergaJU-patch-1 https://github.com/VergaJU/arcasHLA.git
RUN conda env create -f /app/arcasHLA/environment.yml
RUN echo "source activate arcas-hla" > ~/.bashrc
ENV PATH /opt/conda/envs/arcas-hla/bin:$PATH
ENV PATH /app/arcasHLA/:$PATH
RUN arcasHLA reference --update