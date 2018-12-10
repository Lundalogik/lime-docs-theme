FROM docker.lundalogik.com/lundalogik/crm/python-base:latest

CMD sh

RUN pip3 install -U pip setuptools click

# Set timezone to Sweden.
ENV TZ=Europe/Stockholm
RUN apk --no-cache add tzdata \
    && cp /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

WORKDIR /lime
COPY . /lime

RUN pip3 install --no-cache-dir -r requirements.txt
