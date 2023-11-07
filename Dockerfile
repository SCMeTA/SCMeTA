FROM mono:6.12.0.182-slim as BUILD

# MAINTAINER Jo Shields <jo.shields@xamarin.com>
# MAINTAINER Alexander Köplinger <alkpli@microsoft.com>

RUN apt-get update \
  && apt-get install -y \
    binutils \
    curl \
    mono-devel \
    ca-certificates-mono \
    fsharp \
    mono-vbnc \
    nuget \
    referenceassemblies-pcl \
  && rm -rf /var/lib/apt/lists/* /tmp/*


FROM python:3.11-slim-bullseye as RUNTIME

COPY --from=BUILD /usr/lib/mono /usr/lib/mono

WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# Install python dependencies
COPY requirements-docker.txt requirements.txt

RUN python3 -m pip install -i "https://pypi.tuna.tsinghua.edu.cn/simple" --upgrade pip \
    && pip3 install -i "https://pypi.tuna.tsinghua.edu.cn/simple" -r requirements.txt --no-cache-dir


COPY main.ipynb.example main.ipynb

RUN mkdir Data \
    && chmod -R 777 Data

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser", "--port=8888" ]

EXPOSE 8888
VOLUME ["/app/Data"]
