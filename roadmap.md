# Roadmap and file structure

2. Use controllers that can decrypt and ecrypt (maybe inheritance)
    1. For each endpoint, resolve the algorithm first
    2. Build a controller to put it into an endpoint
    3. test
3. Do for each controller
4. Think about all the verification
5. Add a nice html index to display example curl commands



```bash
curl -X POST http://127.0.0.1:5000/encrypt -H 'Content-Type: application/json' -d '{"Hello": "world"}'
```