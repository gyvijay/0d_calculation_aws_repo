FROM python:3.11

WORKDIR /0D_Calculation_AWS

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]