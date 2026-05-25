FROM python:3.12-bookworm
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8050
ENV DASH_ENV=production
# COPY . /opt/app
WORKDIR /opt/app
CMD ["python", "app.py"]