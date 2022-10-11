FROM python
RUN mkdir /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY convert_to_jpg.py /app/convert_to_jpg.py
ENTRYPOINT [ "/app/convert_to_jpg.py" ]
