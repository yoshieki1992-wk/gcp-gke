FROM python:3-slim AS build
ADD . /app
COPY requirements.txt /
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

FROM gcr.io/distroless/python3
COPY --from=build /app /app
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages
ENV FLASK_APP=/app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 80
ENTRYPOINT ["python", "-m", "flask", "run", "--port", "80"]
