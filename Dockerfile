FROM continuumio/miniconda3

COPY samples/docker/v2_env.yml .

RUN apt-get update && \
    apt-get -y install gcc mono-mcs curl && \
    rm -rf /var/lib/apt/lists/*

RUN conda env create -f v2_env.yml

COPY samples ./root
