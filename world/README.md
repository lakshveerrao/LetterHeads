# The world server

One shared world for everyone at letterheads.live. A Cloudflare Worker with one Durable Object (`World`).

The simulation runs in a visitor's browser, the keeper. The server chooses the keeper (a visible tab, computers before
phones, then whoever came first), stores the latest snapshot of the world, and passes messages: live frames and events
from the keeper to everyone else, and requests for help from everyone else to the keeper. If the keeper leaves, hides
its tab or goes quiet for 8 seconds, another visitor takes over. When nobody is there, the world rests until someone
comes back. One backup per hour of the day is kept in storage (`bak0` to `bak23`).

- `GET /ws`: the WebSocket the game connects to.
- `GET /status`: `{online, keeper, updated}`, for the home page.

The game finds the server through `site/world.json` (`{"url":"wss://.../ws"}`). Without it, or with `?solo`, the game
runs a private world saved in the browser, as before. `?world=ws://localhost:8787/ws` points at a local server.

Deploys run from `.github/workflows/world.yml` on every push that changes `world/`, using the repository secrets
`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. Local: `npm install`, then `npx wrangler dev`.

Optional: set a `KEEPER_KEY` secret on the Worker (`npx wrangler secret put KEEPER_KEY`). A browser that opens the game
with `?key=` and that value is always preferred as keeper, for example the YouTube stream machine.
