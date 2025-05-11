# Etapa base com Python
FROM python:3.12-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos para dentro do container
COPY . .

# Instala dependências
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão usada pelo Reflex
EXPOSE 3000

# Comando de inicialização
CMD ["reflex", "run", "--env", "prod", "--backend-port", "3000", "--backend-only"]
