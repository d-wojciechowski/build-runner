FROM centos:7.7.1908

RUN yum install -y zlib-dev zlib-devel make gcc python3 python3-pip
RUN pip3 install wheel

COPY . .
RUN pip3 install -r requirements.txt && pyinstaller main.spec

ENTRYPOINT ["top", "-b"]
