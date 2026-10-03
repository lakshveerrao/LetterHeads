# A quieter connection to the world server (3 October 2026). Cloudflare's free plan allows only so much server time a
# day, and the server now sleeps between messages. So a keeper who is alone in a world sends nothing live (nobody
# would see it) and a copy of the world every two minutes instead of every ten seconds; the moment someone else
# arrives it sends a fresh copy and live frames again. A valley describes itself for the Atlas every two minutes.
# Run from assemble.py via exec(), after move_patch.py.
rep('function sendLive(){if(!W.keeper||!S||CATCHING)return;', 'function sendLive(){if(!W.keeper||!S||CATCHING||W.n<=1)return;')
rep('async function sendSnap(){if(!W.keeper||!S||CATCHING)return;', 'let snapSentAt=0;async function sendSnap(force){if(!W.keeper||!S||CATCHING)return;if(force!==true&&W.n<=1&&Date.now()-snapSentAt<120000)return;snapSentAt=Date.now();')
rep('else if(m.t==="count"){W.n=m.n;if(m.live!=null)W.live=m.live;}', 'else if(m.t==="count"){const was=W.n;W.n=m.n;if(m.live!=null)W.live=m.live;if(W.keeper&&started&&m.n>was)sendSnap(true);}')
rep('if(W.own)metaT=setInterval(sendMeta,30000);', 'if(W.own)metaT=setInterval(sendMeta,120000);')
# a tiny ping keeps the connection open through networks that drop quiet ones; the server answers it while asleep
rep('socket.onopen=()=>{', 'socket.onopen=()=>{clearInterval(socket._ping);socket._ping=setInterval(()=>{if(socket.readyState===1)socket.send("ping");},45000);')
rep('W.snapNow=()=>sendSnap();', 'W.snapNow=()=>sendSnap(true);')
# leaving or hiding the page sends the latest world first, so a lone keeper loses nothing
rep('document.addEventListener("visibilitychange",()=>send({t:"vis",on:!document.hidden}));',
    'document.addEventListener("visibilitychange",()=>{if(document.hidden&&W.keeper)sendSnap(true);send({t:"vis",on:!document.hidden});});addEventListener("pagehide",()=>{if(W.keeper)sendSnap(true);});')
