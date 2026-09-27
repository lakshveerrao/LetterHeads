# v27: the trailer plays inside the game ("Watch the trailer" under the brand, and in the menu).
# Run from assemble.py via exec(), so `s` and rep() are in scope. The film ships next to the page as trailer.mp4.
rep("</style>",""".trailer-link{display:inline-flex;align-items:center;gap:5px;margin-top:5px;padding:2px 0;border:none;background:none;font-family:'Atkinson Hyperlegible',sans-serif;font-size:13px;font-weight:700;color:inherit;text-decoration:underline;text-decoration-color:#E8962F;text-decoration-thickness:2px;text-underline-offset:3px;white-space:nowrap;cursor:pointer;pointer-events:auto}
.trailer-link svg{width:12px;height:12px;fill:#E8962F}
.trailer-link:focus-visible{outline:3px solid #E8962F;outline-offset:2px;border-radius:4px}
#trailerDlg{position:fixed;inset:0;z-index:50;display:flex;align-items:center;justify-content:center;padding:calc(16px + env(safe-area-inset-top,0px)) 16px calc(16px + env(safe-area-inset-bottom,0px));background:rgba(6,7,7,.94)}
#trailerDlg[hidden]{display:none}
#trailerDlg .tbox{width:min(100%,calc((100vh - 110px) * 16 / 9));display:flex;flex-direction:column;gap:12px}
#trailerDlg video{display:block;width:100%;aspect-ratio:16/9;background:#000;border-radius:10px}
#trailerDlg .tbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;color:#E6E1D4;font-size:14px;line-height:1.4}
#trailerDlg .tbar a{color:#F2B96A}
#trailerClose{min-height:44px;padding:0 20px;border-radius:22px;border:1px solid rgba(255,255,255,.4);background:transparent;color:#F6F2E8;font:inherit;font-weight:700;cursor:pointer}
#trailerClose:focus-visible{outline:3px solid #E8962F;outline-offset:2px}
.tour-btn{top:calc(90px + env(safe-area-inset-top,0px))}
@media (max-width:480px){.tour-btn{top:calc(72px + env(safe-area-inset-top,0px))}}
@media (max-width:440px){.trailer-link{font-size:12px}.trailer-link svg{display:none}}
</style>""")

rep('<small id="eraLine">A living world of letters</small></div>',
    '<small id="eraLine">A living world of letters</small><button class="trailer-link" id="trailerLink" type="button"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1l9 5-9 5z"/></svg>Watch the trailer</button></div>')

rep('<button class="float" id="returnBtn">', """<div id="trailerDlg" role="dialog" aria-modal="true" aria-label="Letterheads trailer" hidden>
  <div class="tbox">
    <video id="trailerVid" controls playsinline preload="none"></video>
    <div class="tbar"><span id="trailerNote">300,000 years of being human, in 86 seconds.</span><button id="trailerClose" type="button">Close</button></div>
  </div>
</div>
<button class="float" id="returnBtn">""")

rep('document.getElementById("mTrailer").onclick=()=>{window.open(/letterheads\\.live$/.test(location.hostname)?"/trailer/":"https://claude.ai/artifact/LLWwJuLLAzXpRxxwFR3rBv","_blank","noopener");};',
    'document.getElementById("mTrailer").onclick=()=>{closeSheet();openTrailer();};')

rep('document.getElementById("menuBtn").onclick=()=>{', """// The trailer film ships next to the game as trailer.mp4; if it is missing, point to the trailer page instead.
const TRAILER_PAGE=/letterheads\\.live$/.test(location.hostname)?"/trailer/":"https://claude.ai/artifact/LLWwJuLLAzXpRxxwFR3rBv";
let trailerBack=null,trailerMusic=false;
function openTrailer(){const d=document.getElementById("trailerDlg"),v=document.getElementById("trailerVid");if(!d.hidden)return;trailerBack=document.activeElement;
  trailerMusic=Music.on;if(trailerMusic)Music.setOn(false);d.hidden=false;if(!v.getAttribute("src"))v.src=location.pathname.startsWith("/play")?"/trailer.mp4":"trailer.mp4";
  const p=v.play();if(p&&p.catch)p.catch(()=>{});document.getElementById("trailerClose").focus();}
function closeTrailer(){const d=document.getElementById("trailerDlg"),v=document.getElementById("trailerVid");if(d.hidden)return;v.pause();d.hidden=true;
  if(trailerMusic&&S.settings.sound)Music.setOn(true);if(trailerBack&&trailerBack.focus)trailerBack.focus();}
document.getElementById("trailerLink").onclick=openTrailer;document.getElementById("trailerClose").onclick=closeTrailer;
document.getElementById("trailerDlg").addEventListener("click",e=>{if(e.target.id==="trailerDlg")closeTrailer();});
addEventListener("keydown",e=>{if(e.key==="Escape"&&!document.getElementById("trailerDlg").hidden)closeTrailer();});
document.getElementById("trailerVid").addEventListener("error",()=>{const n=document.getElementById("trailerNote");n.textContent="The film could not load here. ";const a=document.createElement("a");a.href=TRAILER_PAGE;a.target="_blank";a.rel="noopener";a.textContent="Open the trailer page";n.appendChild(a);});
document.getElementById("menuBtn").onclick=()=>{""")

# Link previews and the favicon for the live site (letterheads.live serves the game at its root).
rep('<title>Letterheads: a living world of letters</title>', """<title>Letterheads: a living world of letters</title>
<link rel="canonical" href="https://letterheads.live/play/">
<meta name="description" content="A living world of letters on the real Earth. The Letterheads find food, make friends, form words, discover fire and walk 300,000 years of human history, all on their own.">
<meta property="og:title" content="Letterheads: a living world of letters">
<meta property="og:description" content="The game you can play without playing. 300,000 years of being human, on the real Earth.">
<meta property="og:image" content="https://letterheads.live/og-image.png">
<meta property="og:url" content="https://letterheads.live/play/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">""")
