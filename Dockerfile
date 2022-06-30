FROM python:3.9-buster
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8050
ENV DASH_ENV=production
# COPY . /opt/app
WORKDIR /opt/app
CMD ["python", "app.py"]