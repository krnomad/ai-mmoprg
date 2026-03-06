# MMORPG Prototype Browser Client

Simple browser client prototype using plain HTML/CSS/JavaScript.

## Run locally

```bash
python3 -m http.server 4173
```

Open <http://localhost:4173>.

## Controls

- **Connect** to a websocket server (default `ws://localhost:8080/ws`)
- **Move** with arrow keys or WASD
- **Toggle spectator mode** with the toolbar button
- **Chat** using the chat box

## Message formats (expected)

Incoming JSON examples:

- `{"type":"welcome","playerId":"p1","map":{"width":30,"height":17},"entities":[...]}`
- `{"type":"snapshot","map":{"width":30,"height":17},"entities":[...]}`
- `{"type":"entity","id":"m1","x":2,"y":3,"name":"Slime","type":"monster","hp":25,"maxHp":50}`
- `{"type":"chat","from":"npc-shop","name":"Merchant","text":"Welcome."}`
- `{"type":"speech","id":"npc-shop","text":"Fresh wares!"}`

Outgoing JSON examples:

- `{"type":"hello","spectator":false}`
- `{"type":"move","id":"player-local","x":5,"y":4}`
- `{"type":"chat","text":"Hello"}`
- `{"type":"speech","text":"Hello"}`
- `{"type":"spectator","enabled":true}`
