## Run veloce
- default
```bash
colima start;
docker-compose up -d --build;
docker exec -it pi-agent-dev bash

pi --no-session
```
- avvio pi
```bash
colima start;
docker-compose up -d; docker exec -it pi-agent-dev bash -c 'pi --no-session'
```
- restart
```bash
docker-compose down;
docker-compose up -d --build;
docker exec -it pi-agent-dev bash
```

## Avvia il container
```bash
colima start;

docker-compose up -d --build;
docker exec -it pi-agent-dev bash

docker-compose up -d;
docker exec -it pi-agent-dev bash

pi --no-session

docker-compose down;
colima stop
```
- build no cache
```bash
docker-compose down;
docker-compose build --no-cache;
docker-compose up -d --build;
docker exec -it pi-agent-dev bash
```

## Reset Colima
```bash
# 1. Forza lo spegnimento della macchina virtuale
colima stop --force

# 2. Elimina la configurazione e la VM danneggiata
colima delete --force
```

# Rebuild --no-cache
```bash
docker-compose build --no-cache
```

## Pi
```
pi --no-session
```
