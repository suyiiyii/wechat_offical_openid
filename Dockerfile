FROM python-3.11-slim

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir 

COPY ./code /app

WORKDIR /app

CMD ["python3", "main.py"]
