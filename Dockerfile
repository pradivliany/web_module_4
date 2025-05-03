# інсталюю базовий образ пайтон версії 3.12
FROM python:3.12

# встановлюю робочу директорію всередині контейнеру в папці app
WORKDIR /app

# копіюю файли поетрі в цю папку
COPY pyproject.toml poetry.lock ./

# встановлюю поетрі
RUN pip install poetry==2.1.2

# копіюю решту файлів
COPY . .

# встановлюю залежності з поетрі
RUN poetry install --no-root

# кажу що програма всередины контейнеру прауюватиме на 2-х портах
EXPOSE 3000
EXPOSE 5000/udp

# точка входу
ENTRYPOINT ["poetry", "run", "python", "main.py"]
