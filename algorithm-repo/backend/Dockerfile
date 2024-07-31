FROM python:3.11-alpine

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY src/ src/.

EXPOSE 55955

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "55955"]%