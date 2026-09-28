// Letterheads world server: one shared world for everyone at letterheads.live.
//
// The simulation itself runs in a visitor's browser, the "keeper". The server picks the keeper, keeps the latest
// copy of the world, and passes messages between the keeper and everyone else ("watchers"):
//   keeper   -> server : binary snapshot of the whole world (every few seconds), stored and passed to watchers
//   keeper   -> server : {t:"live"} small frames (twice a second) and {t:"ev"} events, passed to watchers
//   watcher  -> server : {t:"cmd"} a request to help a letter, passed to the keeper
//   keeper   -> server : {t:"res", to} the answer to a request, passed back to the watcher who asked
// If the keeper leaves, hides its tab or goes quiet, another visitor takes over from the world as it last was.

const MAX_SNAPSHOT = 3 * 1024 * 1024;
const PERSIST_EVERY = 60 * 1000;
const KEEPER_QUIET = 8 * 1000;
const CMD_PER_MIN = 30;

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const cors = { "access-control-allow-origin": "*", "cache-control": "no-store" };
    const world = env.WORLD.get(env.WORLD.idFromName("main"));
    if (url.pathname === "/ws") {
      if (req.headers.get("upgrade") !== "websocket") return new Response("Expected a WebSocket", { status: 426 });
      return world.fetch(req);
    }
    if (url.pathname === "/status") {
      const r = await world.fetch(new Request(url.origin + "/status"));
      return new Response(await r.text(), { headers: { "content-type": "application/json", ...cors } });
    }
    return new Response("Letterheads world server. Play at https://letterheads.live", { headers: cors });
  },
};

export class World {
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
    this.clients = new Map(); // id -> {ws, joined, visible, mobile, trusted, cmds:[]}
    this.keeper = null;
    this.snap = null; // Uint8Array
    this.snapAt = 0;
    this.persistedAt = 0;
    this.keeperHeard = 0;
    this.nextId = 1;
    this.ready = ctx.blockConcurrencyWhile(async () => {
      const s = await ctx.storage.get("snap");
      if (s) { this.snap = new Uint8Array(s); this.snapAt = (await ctx.storage.get("snapAt")) || 0; }
    });
    this.timer = setInterval(() => this.tick(), 2000);
  }

  async fetch(req) {
    await this.ready;
    const url = new URL(req.url);
    if (url.pathname === "/status") {
      return new Response(JSON.stringify({ online: this.clients.size, keeper: !!this.keeper, updated: this.snapAt }));
    }
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    server.accept();
    const id = String(this.nextId++);
    const c = { ws: server, joined: Date.now(), visible: true, mobile: false, trusted: false, cmds: [], hello: false };
    this.clients.set(id, c);
    server.addEventListener("message", async (e) => {
      let d = e.data;
      if (typeof d !== "string" && !(d instanceof ArrayBuffer)) { try { d = await new Response(d).arrayBuffer(); } catch (err) { return; } }
      this.onMessage(id, d);
    });
    server.addEventListener("close", () => this.drop(id));
    server.addEventListener("error", () => this.drop(id));
    return new Response(null, { status: 101, webSocket: client });
  }

  send(id, msg) {
    const c = this.clients.get(id);
    if (!c) return;
    try { c.ws.send(typeof msg === "string" || msg instanceof Uint8Array || msg instanceof ArrayBuffer ? msg : JSON.stringify(msg)); }
    catch (e) { this.drop(id); }
  }

  toWatchers(msg) {
    for (const [id, c] of this.clients) if (id !== this.keeper && c.hello) this.send(id, msg);
  }

  count() {
    const n = this.clients.size;
    for (const [id, c] of this.clients) if (c.hello) this.send(id, { t: "count", n });
  }

  onMessage(id, data) {
    const c = this.clients.get(id);
    if (!c) return;
    if (typeof data !== "string") {
      // a snapshot, accepted only from the keeper
      if (id !== this.keeper) return;
      const bytes = new Uint8Array(data);
      if (bytes.length > MAX_SNAPSHOT || bytes.length < 2) return;
      this.snap = bytes; this.snapAt = Date.now(); this.keeperHeard = Date.now();
      this.toWatchers(bytes);
      if (Date.now() - this.persistedAt > PERSIST_EVERY) this.persist();
      return;
    }
    if (data.length > 256 * 1024) return;
    let m;
    try { m = JSON.parse(data); } catch (e) { return; }
    if (!m || typeof m.t !== "string") return;
    switch (m.t) {
      case "hello": {
        c.hello = true;
        c.visible = m.visible !== false;
        c.mobile = !!m.mobile;
        c.trusted = !!(this.env.KEEPER_KEY && m.key && m.key === this.env.KEEPER_KEY);
        let keeper = false;
        if (!this.keeper || (c.trusted && !this.clients.get(this.keeper)?.trusted)) {
          if (this.keeper) this.send(this.keeper, { t: "role", keeper: false });
          this.keeper = id; this.keeperHeard = Date.now(); keeper = true;
        }
        this.send(id, { t: "welcome", id, keeper, hasSnap: !!this.snap, n: this.clients.size });
        if (this.snap) this.send(id, this.snap);
        this.count();
        break;
      }
      case "vis":
        c.visible = !!m.on;
        if (id === this.keeper && !c.visible) this.elect(id);
        else if (!this.keeper && c.visible) this.elect(null);
        break;
      case "live":
      case "ev":
        if (id !== this.keeper) return;
        this.keeperHeard = Date.now();
        this.toWatchers(data);
        break;
      case "res":
        if (id !== this.keeper || typeof m.to !== "string") return;
        this.send(m.to, data);
        break;
      case "cmd": {
        if (id === this.keeper || !this.keeper) { this.send(id, { t: "res", rid: m.rid, error: "nokeeper" }); return; }
        const now = Date.now();
        c.cmds = c.cmds.filter((t) => now - t < 60000);
        if (c.cmds.length >= CMD_PER_MIN) { this.send(id, { t: "res", rid: m.rid, error: "busy" }); return; }
        c.cmds.push(now);
        m.from = id;
        this.send(this.keeper, m);
        break;
      }
    }
  }

  // Pick a new keeper: a visible visitor, trusted first, then computers before phones, then whoever came first.
  elect(avoid) {
    const old = this.keeper;
    const cands = [...this.clients.entries()].filter(([id, c]) => c.hello && c.visible && id !== avoid);
    cands.sort((a, b) => (b[1].trusted - a[1].trusted) || (a[1].mobile - b[1].mobile) || (a[1].joined - b[1].joined));
    if (!cands.length) {
      // nobody better: keep the current keeper if it is still here, even hidden
      if (old && this.clients.has(old)) return;
      this.keeper = null;
      return;
    }
    const next = cands[0][0];
    if (next === old) return;
    if (old && this.clients.has(old)) this.send(old, { t: "role", keeper: false });
    this.keeper = next;
    this.keeperHeard = Date.now();
    this.send(next, { t: "role", keeper: true });
    this.persist();
  }

  drop(id) {
    if (!this.clients.has(id)) return;
    try { this.clients.get(id).ws.close(); } catch (e) {}
    this.clients.delete(id);
    if (id === this.keeper) { this.keeper = null; this.elect(null); }
    this.count();
    if (!this.clients.size) this.persist();
  }

  tick() {
    if (this.keeper && Date.now() - this.keeperHeard > KEEPER_QUIET && this.clients.size > 1) this.elect(this.keeper);
    if (!this.keeper && this.clients.size) this.elect(null);
  }

  async persist() {
    if (!this.snap || this.persistedAt >= this.snapAt) return;
    this.persistedAt = Date.now();
    const buf = this.snap.slice().buffer;
    await this.ctx.storage.put({ snap: buf, snapAt: this.snapAt });
    // one backup per hour of the day, so a bad keeper can be undone
    const h = new Date().getUTCHours();
    const last = await this.ctx.storage.get("bakHour");
    if (last !== h) await this.ctx.storage.put({ ["bak" + h]: buf, bakHour: h });
  }
}
