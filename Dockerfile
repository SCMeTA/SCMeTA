FROM python:3.11-slim-bullseye

COPY sources.list /etc/apt/sources.list

WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* /tmp/*

RUN curl -L https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -o packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb

RUN apt-get update \
    && apt-get install -y \
    dotnet-runtime-6.0 \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# Install python dependencies
COPY requirements-docker.txt requirements.txt

RUN python3 -m pip install -i "https://pypi.tuna.tsinghua.edu.cn/simple" --upgrade pip \
    && pip3 install -i "https://pypi.tuna.tsinghua.edu.cn/simple" -r requirements.txt --no-cache-dir


COPY SCMeTA SCMeTA

COPY main.ipynb.example main.ipynb

RUN mkdir Data \
    && chmod -R 777 Data

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser", "--port=8888" ]

EXPOSE 8888
VOLUME ["/app/Data"]
