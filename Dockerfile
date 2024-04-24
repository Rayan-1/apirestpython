# Use a imagem base do Python
FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie os arquivos do diretório atual para o diretório de trabalho no contêiner
COPY . .

# Instale as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta em que a sua aplicação Flask está sendo executada
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["python3", "bancario.py"]
