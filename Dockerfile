FROM python:3.11-slim

EXPOSE 8000

COPY requirements.txt .

RUN python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --upgrade -r requirements.txt

COPY server.py server.py

CMD ["python", "server.py"]