// Letterheads world server: The World that everyone shares, and a valley of their own for anyone who wants one.
//
// Every world (The World, or one person's valley) is one Durable Object of class World. The simulation itself runs in
// a browser, the "keeper"; the server picks the keeper, keeps the latest copy of the world, and passes messages between
// the keeper and everyone else ("watchers"):
//   keeper  -> server : binary snapshot of the whole world (every few seconds), stored and passed to watchers
//   keeper  -> server : {t:"live"} small frames (twice a second), passed to watchers
//   watcher -> server : {t:"cmd"} a request to help a letter, passed to the keeper
//   keeper  -> server : {t:"res", to} the answer to a request, passed back to the watcher who asked
// In The World any visible visitor can be the keeper, and another takes over if it leaves. In a valley only its owner
// (who holds the valley's secret token) is ever the keeper; while the owner is away, visitors see it as it last was.
// Owners report their valley to the Directory, which lists open valleys for the Atlas.

const MAX_SNAPSHOT = 3 * 1024 * 1024;
const PERSIST_EVERY = 60 * 1000;
const KEEPER_QUIET = 8 * 1000;
const WATCH_EVERY = 5 * 1000; // how often a world with more than one person checks its keeper is still there
const CMD_PER_MIN = 30;
const ARRIVE_GAP = 2 * 60 * 1000;
const VALLEY_ID = /^[a-z0-9]{6,16}$/;
const NAME_OK = /^[A-Z][a-z]{1,11}$/; // valley names are built from letter names, which come from the game's own list
// Every letter in The World carries one of the game's own names, so a keeper that sends anything else is not the game.
const NAMES = new Set(["Asha","Kofi","Mei","Luca","Amara","Tariq","Yuki","Lars","Zola","Emeka","Leila","Chen","Ines","Ravi","Nia","Omar","Sofia","Kenji","Ayo","Mila","Diego","Hana","Farah","Ivan","Priya","Tomas","Ama","Wen","Elif","Sami","Rosa","Kwame","Lina","Arjun","Noor","Pablo","Aiko","Dara","Maya","Juno","Sade","Pavel","Anya","Kai","Zeynep","Rahim","Lucia","Tariku","Mira","Oskar","Yara","Chidi","Selin","Hugo","Aroha","Minh","Nadia","Felix","Imani","Rohan","Esme","Joon","Talia","Bruno","Keira","Idris","Suki","Mateo","Freya","Ade","Lian","Nour"]);
const WORD_OK = /^[A-Z]{2,14}$/;
const TAG_LIKE = /<[a-z\/!]/i;

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const cors = { "access-control-allow-origin": "*", "cache-control": "no-store" };
    const json = (body) => new Response(typeof body === "string" ? body : JSON.stringify(body), { headers: { "content-type": "application/json", ...cors } });
    const w = url.searchParams.get("w") || "world";
    if (w !== "world" && !VALLEY_ID.test(w)) return new Response("Unknown valley", { status: 404, headers: cors });
    const stub = env.WORLD.get(env.WORLD.idFromName(w === "world" ? "main" : "v:" + w));
    if (url.pathname === "/ws") {
      if (req.headers.get("upgrade") !== "websocket") return new Response("Expected a WebSocket", { status: 426 });
      const h = new Headers(req.headers);
      h.set("x-lh-world", w);
      return stub.fetch(new Request(req, { headers: h }));
    }
    if (url.pathname === "/status") {
      const r = await stub.fetch(new Request(url.origin + "/status?w=" + w, { headers: { "x-lh-world": w } }));
      return json(await r.text());
    }
    if (url.pathname === "/restore" || url.pathname === "/backups") {
      // for the project's owner only (the key is a Worker secret set by the deploy workflow): list the hourly backups
      // of The World, or put one back
      const r = await stub.fetch(new Request(url.origin + url.pathname + url.search, { method: req.method, headers: { "x-lh-world": w, "x-lh-key": req.headers.get("x-lh-key") || "" } }));
      return new Response(await r.text(), { status: r.status, headers: { "content-type": "application/json", ...cors } });
    }
    if (url.pathname === "/valleys") {
      const r = await env.DIR.get(env.DIR.idFromName("all")).fetch(new Request(url.origin + "/list"));
      return json(await r.text());
    }
    return new Response("Letterheads world server. Play at https://letterheads.live", { headers: cors });
  },
};

async function sha(text) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export class World {
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
    this.wid = null; // "world" or a valley id
    this.clients = new Map(); // id -> {ws, joined, visible, mobile, trusted, owner, courier, ip, cmds:[]}
    this.keeper = null;
    this.snap = null; // Uint8Array
    this.snapAt = 0;
    this.persistedAt = 0;
    this.keeperHeard = 0;
    this.nextId = 1;
    this.meta = null;
    this.reportedAt = 0;
    this.arrivals = new Map(); // ip -> time, in The World
    this.guard = null; // what The World's last good snapshot said: {created, simT, agents, nextId}
    // Sockets use Cloudflare's hibernation: between messages the object sleeps and costs nothing, and when it wakes
    // it rebuilds who is here from each socket's attachment. Nothing runs on a timer while one person or nobody is
    // here, so an empty world, or one person alone, uses almost none of the daily allowance.
    for (const ws of ctx.getWebSockets()) {
      const a = ws.deserializeAttachment() || {};
      if (!a.id) continue;
      this.clients.set(a.id, { ...a, ws, cmds: [] });
      if (a.k) this.keeper = a.id;
      this.nextId = Math.max(this.nextId, (+a.id || 0) + 1);
    }
    this.keeperHeard = Date.now();
    ctx.setWebSocketAutoResponse(new WebSocketRequestResponsePair("ping", "pong"));
    this.ready = ctx.blockConcurrencyWhile(async () => {
      this.wid = (await ctx.storage.get("wid")) || null;
      this.nextId = Math.max(this.nextId, (await ctx.storage.get("nextId")) || 1);
      const s = await ctx.storage.get("snap");
      if (s) { this.snap = new Uint8Array(s); this.snapAt = (await ctx.storage.get("snapAt")) || 0; }
      this.ownerHash = (await ctx.storage.get("ownerHash")) || null;
      this.inbox = (await ctx.storage.get("inbox")) || [];
      this.meta = (await ctx.storage.get("meta")) || null;
    });
  }

  get isValley() { return this.wid && this.wid !== "world"; }

  async fetch(req) {
    await this.ready;
    if (!this.wid) { this.wid = req.headers.get("x-lh-world") || "world"; await this.ctx.storage.put("wid", this.wid); }
    const url = new URL(req.url);
    if (url.pathname === "/status") {
      const n = [...this.clients.values()].filter((c) => c.hello && !c.courier).length;
      return new Response(JSON.stringify({ online: n, keeper: !!this.keeper, updated: this.snapAt, name: this.meta?.name || null }));
    }
    if (url.pathname === "/restore" || url.pathname === "/backups") return this.admin(req, url);
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    this.ctx.acceptWebSocket(server);
    const id = String(this.nextId++);
    this.ctx.storage.put("nextId", this.nextId);
    const c = { ws: server, id, joined: Date.now(), visible: true, mobile: false, trusted: false, owner: false, courier: false, cmds: [], hello: false,
      ip: req.headers.get("cf-connecting-ip") || "local" };
    this.clients.set(id, c);
    this.keep(c);
    return new Response(null, { status: 101, webSocket: client });
  }

  // what survives hibernation about each person, stored on their socket
  keep(c) {
    try { c.ws.serializeAttachment({ id: c.id, joined: c.joined, visible: c.visible, mobile: c.mobile, trusted: c.trusted, owner: c.owner, courier: c.courier, hello: c.hello, barred: !!c.barred, ip: c.ip, k: c.id === this.keeper }); } catch (e) {}
  }
  setKeeper(id) {
    const old = this.keeper;
    this.keeper = id;
    if (old && this.clients.has(old)) this.keep(this.clients.get(old));
    if (id && this.clients.has(id)) this.keep(this.clients.get(id));
  }
  idOf(ws) { const a = ws.deserializeAttachment(); return a && a.id; }
  async webSocketMessage(ws, data) { await this.ready; const id = this.idOf(ws); if (id && this.clients.has(id)) await this.onMessage(id, data); }
  async webSocketClose(ws) { await this.ready; const id = this.idOf(ws); if (id) this.drop(id); }
  async webSocketError(ws) { await this.ready; const id = this.idOf(ws); if (id) this.drop(id); }
  // with more than one person here, check now and then that the keeper is still there; otherwise stay asleep
  async watch() {
    if (this.clients.size < 2) return;
    if (!(await this.ctx.storage.getAlarm())) await this.ctx.storage.setAlarm(Date.now() + WATCH_EVERY);
  }
  async alarm() { await this.ready; this.tick(); await this.watch(); }

  send(id, msg) {
    const c = this.clients.get(id);
    if (!c) return;
    try { c.ws.send(typeof msg === "string" || msg instanceof Uint8Array || msg instanceof ArrayBuffer ? msg : JSON.stringify(msg)); }
    catch (e) { this.drop(id); }
  }

  people() { return [...this.clients.values()].filter((c) => c.hello && !c.courier).length; }

  toWatchers(msg) {
    for (const [id, c] of this.clients) if (id !== this.keeper && c.hello && !c.courier) this.send(id, msg);
  }

  count() {
    const n = this.people();
    for (const [id, c] of this.clients) if (c.hello && !c.courier) this.send(id, { t: "count", n, live: !!this.keeper });
  }

  canKeep(c) { return this.isValley ? c.owner : !c.courier && !c.barred; }

  // The World is kept by a visitor's browser, so what it sends is checked against what the game itself can produce:
  // the same world (never a different or reset one), time that only moves forward, letters that only come and never
  // vanish in bulk, names from the game's list, words in capitals, and no markup. A keeper that fails is replaced and
  // never keeps again on that connection; everyone keeps the last good world.
  async unpack(bytes) {
    if (bytes[0] === 1) return await new Response(new Blob([bytes.subarray(1)]).stream().pipeThrough(new DecompressionStream("gzip"))).text();
    return new TextDecoder().decode(bytes.subarray(1));
  }
  guardFrom(d) { return { created: d.S.created, simT: d.S.simT, agents: d.S.agents.length, nextId: d.nextId || 0 }; }
  async checkSnap(bytes) {
    let d;
    try { d = JSON.parse(await this.unpack(bytes)); } catch (e) { return "unreadable"; }
    const S = d && d.S;
    if (!S || S.v !== 3 || typeof S.created !== "number" || typeof S.simT !== "number") return "shape";
    if (!Array.isArray(S.agents) || S.agents.length > 90) return "agents";
    for (const a of S.agents) if (!a || !NAMES.has(a.name) || typeof a.ch !== "string" || !/^[A-Z]$/.test(a.ch)) return "letter";
    if (!Array.isArray(S.words) || S.words.length > 120) return "words";
    for (const w of S.words) if (!w || typeof w.text !== "string" || !WORD_OK.test(w.text)) return "word";
    if (S.spoken != null && this.badSpoken(S.spoken)) return "spoken";
    if (S.vocab != null) { if (typeof S.vocab !== "object" || Array.isArray(S.vocab)) return "vocab"; const ks = Object.keys(S.vocab); if (ks.length > 12000 || ks.some(k => !WORD_OK.test(k))) return "vocab"; }
    for (const k of ["chronicle", "history", "moments"]) {
      const list = S[k];
      if (list == null) continue;
      if (!Array.isArray(list) || list.length > 3100) return k;
      for (const e of list) if (!e || typeof e.text !== "string" || e.text.length > 400 || TAG_LIKE.test(e.text)) return k;
    }
    if (!this.guard && this.snap) { try { const o = JSON.parse(await this.unpack(this.snap)); if (o && o.S && Array.isArray(o.S.agents)) this.guard = this.guardFrom(o); } catch (e) {} }
    const g = this.guard;
    if (g) {
      if (S.created !== g.created) return "another world";
      if (S.simT < g.simT - 30) return "time went back";
      if (S.agents.length < g.agents - 3) return "letters vanished";
      if ((d.nextId || 0) < g.nextId) return "ids went back";
    }
    this.guard = this.guardFrom(d);
    return null;
  }
  checkLive(m) {
    if (!Array.isArray(m.A) || m.A.length > 90) return "agents";
    for (const a of m.A) if (!a || !NAMES.has(a.name) || typeof a.ch !== "string" || !/^[A-Z]$/.test(a.ch)) return "letter";
    if (!Array.isArray(m.W) || m.W.length > 120) return "words";
    for (const w of m.W) if (!w || typeof w.text !== "string" || !WORD_OK.test(w.text)) return "word";
    if (m.SP != null && this.badSpoken(m.SP)) return "spoken";
    if (this.guard && (m.A.length < this.guard.agents - 3 || m.T < this.guard.simT - 30)) return "not this world";
    return null;
  }
  // words letters are saying together right now: a short list of real-looking words
  badSpoken(list) { return !Array.isArray(list) || list.length > 20 || list.some(s => !s || typeof s.text !== "string" || !WORD_OK.test(s.text) || !Array.isArray(s.ids) || s.ids.length > 12); }
  bar(id, why) {
    const c = this.clients.get(id);
    if (!c) return;
    console.log("barred a keeper:", why);
    c.barred = true;
    this.keep(c);
    if (this.keeper === id) { this.send(id, { t: "role", keeper: false }); this.setKeeper(null); this.elect(id); }
    if (this.snap) this.send(id, this.snap);
  }

  // Owner tools (The World only): list the hourly backups, or put one back. The keeper is replaced by a visitor who
  // has loaded the restored world, and that keeper then lives through the time since the backup.
  async admin(req, url) {
    const key = req.headers.get("x-lh-key") || "";
    if (this.isValley || !this.env.KEEPER_KEY || key !== this.env.KEEPER_KEY) return new Response(JSON.stringify({ error: "not allowed" }), { status: 403 });
    const list = [];
    for (let h = 0; h < 24; h++) { const at = await this.ctx.storage.get("bakAt" + h); if (at) list.push({ bak: h, at }); }
    list.sort((a, b) => b.at - a.at);
    if (url.pathname === "/backups") return new Response(JSON.stringify({ now: Date.now(), backups: list }));
    if (req.method !== "POST") return new Response(JSON.stringify({ error: "use POST" }), { status: 405 });
    const ago = Math.max(0, Math.min(23, parseInt(url.searchParams.get("hours") || "1", 10) || 0));
    const pick = list.find((b) => Date.now() - b.at >= ago * 3600 * 1000);
    if (!pick) return new Response(JSON.stringify({ error: "no backup that old", backups: list }), { status: 404 });
    const buf = await this.ctx.storage.get("bak" + pick.bak);
    if (!buf) return new Response(JSON.stringify({ error: "backup missing" }), { status: 404 });
    this.snap = new Uint8Array(buf);
    this.snapAt = Date.now();
    this.guard = null;
    try { const o = JSON.parse(await this.unpack(this.snap)); this.guard = this.guardFrom(o); } catch (e) {}
    await this.ctx.storage.put({ snap: buf, snapAt: this.snapAt });
    this.persistedAt = Date.now();
    if (this.keeper) { this.send(this.keeper, { t: "role", keeper: false }); this.setKeeper(null); }
    for (const [id, c] of this.clients) if (c.hello && !c.courier) this.send(id, this.snap);
    await this.ctx.storage.setAlarm(Date.now() + 1500); // the alarm elects a keeper who has loaded the restored world
    return new Response(JSON.stringify({ restored: pick }));
  }

  async onMessage(id, data) {
    const c = this.clients.get(id);
    if (!c) return;
    if (typeof data !== "string") {
      // a snapshot, accepted only from the keeper
      if (id !== this.keeper) return;
      const bytes = new Uint8Array(data);
      if (bytes.length > MAX_SNAPSHOT || bytes.length < 2) return;
      if (!this.isValley) {
        const bad = await this.checkSnap(bytes);
        if (bad) { this.bar(id, "snapshot: " + bad); return; }
        if (id !== this.keeper) return;
      }
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
        if (c.hello) return;
        c.courier = !!m.courier;
        c.visible = m.visible !== false;
        c.mobile = !!m.mobile;
        c.trusted = !!(this.env.KEEPER_KEY && m.key && m.key === this.env.KEEPER_KEY);
        if (this.isValley && typeof m.own === "string" && m.own.length >= 16 && m.own.length <= 64) {
          const h = await sha(m.own);
          if (!this.ownerHash) { this.ownerHash = h; await this.ctx.storage.put("ownerHash", h); }
          c.owner = h === this.ownerHash;
        }
        c.hello = true;
        this.keep(c);
        if (c.courier) { this.send(id, { t: "welcome", id, keeper: false, courier: true }); return; }
        let keeper = false;
        const cur = this.keeper && this.clients.get(this.keeper);
        if (this.canKeep(c) && (!cur || (c.trusted && !cur.trusted) || (c.owner && this.isValley))) {
          if (this.keeper) this.send(this.keeper, { t: "role", keeper: false });
          this.setKeeper(id); this.keeperHeard = Date.now(); keeper = true;
        }
        this.send(id, { t: "welcome", id, keeper, owner: c.owner, hasSnap: !!this.snap, n: this.people(), live: !!this.keeper, valley: this.isValley, name: this.meta?.name || null });
        if (!keeper) this.keeperHeard = Date.now(); // the keeper may have been quiet while alone; give it time to notice
        if (this.snap) this.send(id, this.snap); // a valley owner gets it too: their other device may have kept it since
        if (keeper) this.flushInbox();
        this.count();
        this.watch();
        break;
      }
      case "vis":
        c.visible = !!m.on;
        this.keep(c);
        if (this.isValley) break;
        if (id === this.keeper && !c.visible) this.elect(id);
        else if (!this.keeper && c.visible) this.elect(null);
        break;
      case "live":
        if (id !== this.keeper) return;
        if (!this.isValley) { const bad = this.checkLive(m); if (bad) { this.bar(id, "live: " + bad); return; } }
        this.keeperHeard = Date.now();
        this.toWatchers(data);
        break;
      case "meta":
        // the owner describes their valley for the Atlas
        if (id !== this.keeper || !this.isValley || !c.owner) return;
        this.meta = this.cleanMeta(m);
        if (Date.now() - this.reportedAt > 100000) this.report(true);
        break;
      case "res":
        if (id !== this.keeper || typeof m.to !== "string") return;
        this.send(m.to, data);
        break;
      case "cmd": {
        const now = Date.now();
        c.cmds = c.cmds.filter((t) => now - t < 60000);
        if (c.cmds.length >= CMD_PER_MIN) { this.send(id, { t: "res", rid: m.rid, error: "busy" }); return; }
        c.cmds.push(now);
        if (c.courier) {
          // a letter travelling from someone's valley into The World
          if (this.isValley || m.name !== "arrive") return;
          if (now - (this.arrivals.get(c.ip) || 0) < ARRIVE_GAP) { this.send(id, { t: "res", rid: m.rid, error: "wait" }); return; }
          this.arrivals.set(c.ip, now);
          const a = m.args || {};
          const item = { name: "arrive", args: { ch: String(a.ch || "").slice(0, 1), n: String(a.n || "").slice(0, 12), from: String(a.from || "").slice(0, 12) } };
          if (this.keeper) { this.send(this.keeper, { t: "cmd", rid: 0, from: "inbox", ...item }); }
          else { this.inbox = [...this.inbox, item].slice(-20); await this.ctx.storage.put("inbox", this.inbox); }
          this.send(id, { t: "res", rid: m.rid, ok: true });
          return;
        }
        if (id === this.keeper || !this.keeper) { this.send(id, { t: "res", rid: m.rid, error: "nokeeper" }); return; }
        m.from = id;
        this.send(this.keeper, m);
        break;
      }
    }
  }

  cleanMeta(m) {
    const num = (v, lo, hi) => (typeof v === "number" && isFinite(v) ? Math.max(lo, Math.min(hi, v)) : 0);
    return {
      name: typeof m.name === "string" && NAME_OK.test(m.name) ? m.name : null,
      listed: m.listed !== false,
      x: num(m.x, -1e6, 1e6), yy: num(m.yy, -1e6, 1e6), y: num(m.y, 0, 300000),
      place: typeof m.place === "string" ? m.place.replace(/[<>]/g, "").slice(0, 60) : "",
      letters: num(m.letters, 0, 999) | 0, words: num(m.words, 0, 999) | 0,
    };
  }

  async flushInbox() {
    if (!this.inbox.length || !this.keeper) return;
    for (const item of this.inbox) this.send(this.keeper, { t: "cmd", rid: 0, from: "inbox", ...item });
    this.inbox = [];
    await this.ctx.storage.put("inbox", []);
  }

  async report(online) {
    if (!this.isValley || !this.meta) return;
    this.reportedAt = Date.now();
    await this.ctx.storage.put("meta", this.meta);
    try {
      await this.env.DIR.get(this.env.DIR.idFromName("all")).fetch(new Request("https://dir/report", {
        method: "POST", body: JSON.stringify({ id: this.wid, ...this.meta, online, watching: Math.max(0, this.people() - 1) }),
      }));
    } catch (e) {}
  }

  // Pick a new keeper: in The World a visible visitor (trusted first, then computers before phones, then whoever came
  // first); in a valley only its owner.
  elect(avoid) {
    const old = this.keeper;
    const cands = [...this.clients.entries()].filter(([id, c]) => c.hello && this.canKeep(c) && (this.isValley || c.visible) && id !== avoid);
    cands.sort((a, b) => (b[1].trusted - a[1].trusted) || (a[1].mobile - b[1].mobile) || (a[1].joined - b[1].joined));
    if (!cands.length) {
      if (old && this.clients.has(old)) return; // nobody better: keep the current keeper, even hidden
      this.setKeeper(null);
      this.count();
      return;
    }
    const next = cands[0][0];
    if (next === old) return;
    if (old && this.clients.has(old)) this.send(old, { t: "role", keeper: false });
    this.setKeeper(next);
    this.keeperHeard = Date.now();
    this.send(next, { t: "role", keeper: true });
    this.flushInbox();
    this.count();
    this.persist();
  }

  drop(id) {
    if (!this.clients.has(id)) return;
    try { this.clients.get(id).ws.close(); } catch (e) {}
    this.clients.delete(id);
    if (id === this.keeper) {
      this.setKeeper(null);
      this.elect(null);
      if (this.isValley && !this.keeper) this.report(false);
    }
    this.count();
    if (!this.clients.size) this.persist();
  }

  tick() {
    if (this.keeper && Date.now() - this.keeperHeard > KEEPER_QUIET && this.clients.size > 1 && !this.isValley) this.elect(this.keeper);
    if (!this.keeper && this.clients.size) this.elect(null);
  }

  async persist() {
    if (!this.snap || this.persistedAt >= this.snapAt) return;
    this.persistedAt = Date.now();
    const buf = this.snap.slice().buffer;
    await this.ctx.storage.put({ snap: buf, snapAt: this.snapAt });
    if (this.isValley) return;
    // one backup per hour of the day, so a bad keeper can be undone
    const h = new Date().getUTCHours();
    const last = await this.ctx.storage.get("bakHour");
    if (last !== h || !(await this.ctx.storage.get("bakAt" + h))) await this.ctx.storage.put({ ["bak" + h]: buf, ["bakAt" + h]: Date.now(), bakHour: h });
  }
}

// The list of valleys for the Atlas: every valley whose owner has had it open in the last two days and wants it shown.
export class Directory {
  constructor(ctx) {
    this.ctx = ctx;
    this.list = new Map();
    this.dirty = false;
    this.ready = ctx.blockConcurrencyWhile(async () => {
      const l = await ctx.storage.get("list");
      if (l) for (const v of l) this.list.set(v.id, v);
    });
  }

  async fetch(req) {
    await this.ready;
    const url = new URL(req.url);
    const now = Date.now();
    if (url.pathname === "/report" && req.method === "POST") {
      let v;
      try { v = await req.json(); } catch (e) { return new Response("bad", { status: 400 }); }
      if (!v || !VALLEY_ID.test(v.id)) return new Response("bad", { status: 400 });
      if (!v.listed || !v.name) this.list.delete(v.id);
      else this.list.set(v.id, { id: v.id, name: v.name, x: v.x, yy: v.yy, y: v.y, place: v.place, letters: v.letters, words: v.words, online: !!v.online, watching: v.watching | 0, seen: now });
      await this.save();
      return new Response("ok");
    }
    if (url.pathname === "/list") {
      const out = [...this.list.values()].filter((v) => now - v.seen < 48 * 3600 * 1000)
        .map((v) => ({ ...v, online: v.online && now - v.seen < 5 * 60000 }))
        .sort((a, b) => (b.online - a.online) || (b.seen - a.seen)).slice(0, 150);
      return new Response(JSON.stringify({ valleys: out }));
    }
    return new Response("not found", { status: 404 });
  }

  async save() {
    this.dirty = false;
    const now = Date.now();
    for (const [id, v] of this.list) if (now - v.seen > 48 * 3600 * 1000) this.list.delete(id);
    await this.ctx.storage.put("list", [...this.list.values()]);
  }
}
