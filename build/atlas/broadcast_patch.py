# Broadcast mode (28 September 2026): /play/?broadcast turns the game into a clean picture for a 24/7 YouTube Live stream.
# No buttons, a large caption, a LIVE badge, the era and day, and a pointer to letterheads.live. The camera always
# follows the best story and music is on. Run from assemble.py via exec(), after product_patch.py.
rep("</style>", """body.broadcast .top,body.broadcast .zoom,body.broadcast .tour-btn,body.broadcast #hint,body.broadcast .caption .row,
body.broadcast #elsewhere,body.broadcast #returnBtn,body.broadcast #storyToast,body.broadcast #trailerDlg,body.broadcast #intro,
body.broadcast .sheet,body.broadcast #atlasUI .row,body.broadcast #atlasUI .atime,body.broadcast .aclose{display:none!important}
body.broadcast{cursor:none}
body.broadcast .caption{width:min(1100px,calc(100% - 80px));bottom:48px;padding:22px 34px 24px;background:rgba(20,26,24,.9)}
body.broadcast .caption p{font-size:40px;line-height:1.18}
body.broadcast .caption .sub{font-size:22px}
body.broadcast .acard{width:min(1000px,calc(100% - 80px));bottom:48px}
body.broadcast .acard p{font-size:36px}body.broadcast .acard .sub{font-size:21px}
#bcast{display:none}
body.broadcast #bcast{display:block}
#bcast .b-live{position:fixed;left:36px;top:30px;display:flex;align-items:center;gap:14px;font-family:Spectral,Georgia,serif;font-size:34px;font-weight:600;color:#F6F2E8;text-shadow:0 2px 10px rgba(0,0,0,.6)}
#bcast .b-live i{font-style:normal;font-family:'Atkinson Hyperlegible',sans-serif;font-size:16px;font-weight:700;letter-spacing:.12em;background:#D93A2B;color:#fff;padding:5px 11px;border-radius:6px;text-shadow:none}
#bcast .b-era{position:fixed;right:36px;top:34px;max-width:52%;text-align:right;font-size:20px;line-height:1.35;color:#F6F2E8;background:rgba(20,26,24,.72);padding:10px 16px;border-radius:12px}
#bcast .b-url{position:fixed;right:36px;bottom:14px;font-size:17px;font-weight:700;color:#F6F2E8;text-shadow:0 1px 6px rgba(0,0,0,.7)}
#bcast .b-url b{color:#F2B96A}
</style>""")

rep('<button class="float" id="returnBtn">', """<div id="bcast" aria-hidden="true"><div class="b-live"><i>LIVE</i>Letterheads</div><div class="b-era" id="bEra"></div><div class="b-url">Play along at <b>letterheads.live</b></div></div>
<button class="float" id="returnBtn">""")

rep('window.__lango={', """if(/[?&]broadcast\\b/.test(location.search)){
  document.body.classList.add("broadcast");
  S.settings.camera="director";S.settings.tips=false;
  const enter=()=>{const g=document.getElementById("introGo");const ib=document.getElementById("intro");if(ib&&ib.style.display!=="none"&&g)g.click();
    if(typeof setSound==="function"&&!Music.on)setSound(true);};
  setTimeout(enter,1500);setInterval(enter,60000);
  setInterval(()=>{const e=document.getElementById("eraLine");const parts=e?e.textContent.split(" · "):[];document.getElementById("bEra").textContent=parts.slice(1,3).join(" · ");},1000);
}
window.__lango={""")
