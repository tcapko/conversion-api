FROM python:3.9
WORKDIR /app
COPY app/requirements.txt .
RUN apt-get update && apt-get -y install unoconv libreoffice
RUN sed -i 's|#!/usr/bin/env python3|#!/usr/bin/python3|' /usr/bin/unoconv
RUN pip3 install --upgrade pip
COPY ./converterLib /app/converterLib
RUN pip3 install -r requirements.txt
COPY /app .
CMD ["python", "app.py"]
