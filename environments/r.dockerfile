FROM rocker/tidyverse:4.0.0-ubuntu18.04
 
# Install python
RUN apt-get update -qq && \
 apt-get install -y python3
 
# create link for python
RUN ln -f /usr/bin/python3 /usr/bin/python
