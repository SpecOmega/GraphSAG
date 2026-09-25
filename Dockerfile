FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
CMD ["python","-c","import graphsag; print('GraphSAG 1.0.0')"]
