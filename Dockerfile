#
# DeepStyle
#
# https://github.com/oeeckhoutte/twitterMood
#

# Pull base image.
FROM ubuntu:14.04

# Install basics.
RUN \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential && \
  apt-get install -y software-properties-common && \
  apt-get install -y byobu curl git htop man unzip vim wget

#RUN rm -rf /var/lib/apt/lists/*

# Add files.
ADD root/.bashrc /root/.bashrc
ADD root/.gitconfig /root/.gitconfig
ADD root/.scripts /root/.scripts

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root

# Install twitterMood deps.
RUN mkdir -p /root/code
ADD code /root/

RUN \
  apt-get install -y python && \
  apt-get install -y python-pip

RUN \
  wget http://apache.crihan.fr/dist/kafka/0.10.0.1/kafka_2.10-0.10.0.1.tgz && \
  tar -zxvf kafka_2.10-0.10.0.1.tgz 
  
RUN \
  apt-get install -y default-jdk 

RUN \  
  cd kafka_2.10-0.10.0.1 && \
  ls -l && \
  bin/zookeeper-server-start.sh config/zookeeper.properties && \
  bin/kafka-server-start.sh config/server.properties && \
  bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic twitterstream && \
  #bin/kafka-topics.sh --list --zookeeper localhost:2181

RUN \
  python twitter_to_kafka.py

RUN pip install -r requirements.txt
RUN pip install matplotlib


EXPOSE 2181

# Define default command.
CMD ["bash"]