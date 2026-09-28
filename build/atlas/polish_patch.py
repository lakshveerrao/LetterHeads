# Fixes from the 28 September 2026 audit. Run from assemble.py via exec(), after shared_patch.py.

# Names stay unique among living letters. The 72 names used to be handed out in turn, so once 72 letters had been
# born, new letters repeated living names ("Follow Elif" could mean two letters). A traveller or a renamed letter
# also keeps its own name only when nobody alive has it.
rep('name:NAMES[(S.nameIdx++)%NAMES.length],',
    'name:freeName(),')
rep('function makeAgent(ch,x,y,born,young){',
    'function freeName(){const used=new Set(S.agents.map(a=>a.name));for(let k=0;k<NAMES.length;k++){const n=NAMES[(S.nameIdx++)%NAMES.length];if(!used.has(n))return n;}return NAMES[(S.nameIdx++)%NAMES.length];}\nfunction makeAgent(ch,x,y,born,young){')
rep('if(NAMES.includes(args.n))x.name=args.n;',
    'const was=NAMES.includes(args.n)?args.n:null;if(was&&!S.agents.some(o=>o.name===was))x.name=was;const renamed=was&&x.name!==was;')
# a traveller whose name is already taken here says so, so the sender can still find them
rep('remember(x,`I travelled here from ${where}.`,true);chron(`${x.name}, ${art(c)} ${c}, arrived at the Hearth refuge from ${where}.`,"people");',
    'remember(x,renamed?`I travelled here from ${where}, where I was called ${was}. Someone here already had that name, so I became ${x.name}.`:`I travelled here from ${where}.`,true);chron(renamed?`${was}, ${art(c)} ${c}, arrived at the Hearth refuge from ${where} and took the name ${x.name}, because ${/^[AEIOU]/.test(was)?"an":"a"} ${was} already lived here.`:`${x.name}, ${art(c)} ${c}, arrived at the Hearth refuge from ${where}.`,"people");')
rep('if(n!==a.name&&(!NAMES.includes(n)||a.renamed))n=a.name;',
    'if(n!==a.name&&(!NAMES.includes(n)||a.renamed||S.agents.some(o=>o!==a&&o.name===n)))n=a.name;')

# A shared moment links to the letter it was about, in the same world, instead of only to the home page.
rep('kind:o.kind,chapter:era()};',
    'kind:o.kind,chapter:era(),who:(o.main!=null&&agentById(o.main)?.name)||((o.ids||[]).map(agentById).find(Boolean)?.name)||null};')
rep('const text=`${m.text} (Letterheads, day ${m.day}) https://letterheads.live`;',
    'const text=`${m.text} (Letterheads, day ${m.day}) ${momentLink(m)}`;')
rep('async function shareMoment(m){',
    '''function momentLink(m){const f=m.who?"follow="+encodeURIComponent(m.who):"";
  if(WORLD.on&&WORLD.mode!=="world"&&WORLD.vid)return "https://letterheads.live/play/?v="+WORLD.vid+(f?"&"+f:"");
  if(WORLD.on)return "https://letterheads.live/play/"+(f?"?"+f:"");return "https://letterheads.live/play/";}
async function shareMoment(m){''')

# Phones: the place pill and "Your letters (3)" used to push the menu button off the right edge. On narrow screens
# the pill hangs below the name without widening its column, and the companions button is shorter.
rep("</style>", """@media (max-width:480px){.top .brand{position:relative}.top .brand .place-link{position:absolute;left:0;top:100%;margin-top:0}}
@media (max-width:360px){.top{gap:6px;padding-left:14px;padding-right:12px}}
</style>""")
rep('jb.textContent=n?`Your letters (${n})`:"Join";', 'jb.textContent=n?(innerWidth<=480?`♥ ${n}`:`Your letters (${n})`):"Join";jb.setAttribute("aria-label",n?`Your letters (${n})`:"Join");')

# In The World the join sheet talks about The World, not a valley.
rep('<h2 id="sheetTitle">Join the valley</h2>', '<h2 id="sheetTitle">${WORLD.on&&WORLD.mode==="world"?"Join The World":"Join the valley"}</h2>')
