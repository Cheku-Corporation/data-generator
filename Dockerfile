FROM python:3.8-slim-buster
RUN pip install --upgrade pip


WORKDIR /
COPY . .

RUN pip install -r requirements.txt
RUN chmod a+x run.sh
CMD [ "./run.sh"]
