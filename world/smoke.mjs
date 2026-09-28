// Checks the deployed world server: /status answers, and a WebSocket gets a welcome. Usage: node smoke.mjs https://host
const base = process.argv[2];
for (let i = 0; i < 12; i++) {
  try { const r = await fetch(base + "/status"); if (r.ok) { console.log("status", await r.text()); break; } console.log("status", r.status); }
  catch (e) { console.log("status error", e.message); }
  await new Promise((r) => setTimeout(r, 10000));
}
const ws = new WebSocket(base.replace(/^http/, "ws") + "/ws");
const t = setTimeout(() => { console.log("no welcome"); process.exit(1); }, 15000);
ws.onopen = () => ws.send(JSON.stringify({ t: "hello", visible: false }));
ws.onmessage = (e) => { if (typeof e.data === "string" && e.data.includes("welcome")) { console.log("ws", e.data); clearTimeout(t); ws.close(); process.exit(0); } };
ws.onerror = (e) => console.log("ws error", e.message || e.type);
