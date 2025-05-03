Запуск збірки: 
    docker build -t web-module-4 .

Запуск контейнера: 
    docker run -p 3000:3000 -p 5000:5000/udp -v <шлях куди зберігати на вашому ПК>:/app/storage web-module-4