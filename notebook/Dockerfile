FROM jupyter/minimal-notebook:python-3.11

WORKDIR /home/jovyan

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /home/jovyan/work/notebooks
