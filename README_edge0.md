# run Pi Agent Docker
- run
```bash
colima start;

(cd docker_pi_agent;
docker-compose up -d);
docker exec -it pi-agent-dev bash
```
- run (with build)
```bash
colima start;

(cd docker_pi_agent;
docker-compose up -d --build);
docker exec -it pi-agent-dev bash
```
- reboot
```bash
(cd docker_pi_agent;
docker-compose down;
docker-compose up -d --build);
docker exec -it pi-agent-dev bash
```
- stop
```bash
(cd docker_pi_agent;
docker-compose down)

colima stop;
```

# run Edge0 già installato
```bash
(cd /Users/giuseppe.alfieri/my_work/DOCKER/edge0/edge0;
source venv/bin/activate;
edge0 serve ./models/edge0-35b --port 8080)
```

curl http://host.docker.internal:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "edge0-35b",
    "messages": [
      {"role": "user", "content": "Ciao! Dimmi chi sei in una sola frase."}
    ]
  }'