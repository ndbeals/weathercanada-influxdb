from python:3.8

COPY ./setup.py /opt/weather/setup.py
RUN cd /opt/weather && \
    touch README.md && \
    python setup.py install

WORKDIR /opt/weather
CMD [ "python", "weathercanada_atom" ]