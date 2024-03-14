# Dockerfile for service
# BUILD:
# > docker build . -t ach_facts

###
# RUN:
# docker run -p 8000:8000 ach_facts
# or RUN with login (allows shutdown from within) :
# docker run -it -p 8000:8000 ach_facts bash

FROM python:3.9

RUN mkdir /workdir
WORKDIR /workdir

# COPY roberta-EvidenceAlignment-tuned-model.zip /workdir/
# RUN unzip roberta-EvidenceAlignment-tuned-model.zip

COPY requirements.txt /workdir/
COPY *.py /workdir/

#install the requirements
RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT uvicorn app:app --workers 1 --host 0.0.0.0 --port 8000
#CMD ["uvicorn",  "en_sac:app",  "--workers" "1" "--host" "0.0.0.0" "--port" "8000"]
