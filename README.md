# betting-software-test-task

### env file
```shell
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### run app
```shell
docker-compose up
```
When we run this command, our app is available 127.0.0.1:8080

### run tests
```shell
docker exec -it betting-software-test-task pytest tests/ --disable-warnings
```