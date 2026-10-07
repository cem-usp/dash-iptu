FROM python:3.12-bookworm
COPY requirements.txt constraints.txt ./
RUN pip install -r requirements.txt
EXPOSE 8050
ENV DASH_ENV=production
# COPY . /opt/app
WORKDIR /opt/app
CMD ["gunicorn", "-b", "0.0.0.0:8050", "--timeout", "300", "app:server"]