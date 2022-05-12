FROM python:3.9-buster
COPY . /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt
EXPOSE 8050
EXPORT DASH_ENV=production
CMD ["python", "app.py"]