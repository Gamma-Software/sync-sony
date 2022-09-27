FROM python
RUN mkdir /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY process_image.py /app/process_image.py
