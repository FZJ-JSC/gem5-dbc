FROM arm64v8/ubuntu:22.04
ADD qemu-aarch64-static /usr/bin/qemu-aarch64-static
ADD m5.aarch64 /sbin/m5
ADD init.gem5 /sbin/init

ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Mount point for secondary disk image
RUN mkdir /data

# Install basic setup
RUN apt-get update && apt-get install vim build-essential environment-modules        \
    git-core git python3 python3-dev psmisc zlib1g-dev libgmp3-dev libgmpxx4ldbl     \
    libmpfr-dev libunwind-dev pkg-config libpapi-dev papi-tools libgsl-dev cmake -y

RUN apt-get install \
    libnuma-dev gcc g++ -y

# Install mpi
RUN apt-get install -y mpich 

RUN apt-get install -y sqlite3 libsqlite3-dev

# get .bashrc
RUN touch ~/.bashrc
RUN echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data/lib/dynamic:/data/lib/static" >> ~/.bashrc

# resolv.conf
#RUN echo "nameserver 8.8.8.8" >> /etc/resolv.conf
RUN echo "gem5-host" >> /etc/hostname
