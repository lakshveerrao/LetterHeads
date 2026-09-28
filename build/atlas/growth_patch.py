# Livelier start (28 September 2026). With one of each letter the first world had only four vowels, so after two or
# three words the rest of the letters could spell nothing and wandered alone. Now a new world starts with 26 letters
# (the 19 early letters plus E E I O R L D, which let about twice as many words form), and while letters are stuck
# alone the Hearth refuge brings, sooner, the one letter that would let them spell something.
# Run from assemble.py via exec(), after product_patch.py.
rep('''"ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").filter(c=>!LATE[c]).forEach(ch=>{''',
    '''["ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").filter(c=>!LATE[c]),..."EEIORLD"].flat().forEach(ch=>{''')

rep('''function neededLetter(){const wd=S.words.find(w=>w.state==="wounded");if(wd)return wd.text[wd.missing];''',
    '''function stuckLetters(){return S.agents.filter(a=>!a.word&&!a.young);}
function unlockLetter(){const free={};stuckLetters().forEach(a=>free[a.ch]=(free[a.ch]||0)+1);const score={};
  for(const w of DICT){if(REQ[w])continue;const have={...free};const miss=[];for(const c of w){if(have[c])have[c]--;else miss.push(c);}if(miss.length===1)score[miss[0]]=(score[miss[0]]||0)+1;}
  const best=Object.keys(score).filter(c=>!LATE[c]||S.lateBorn?.[c]).sort((p,q)=>score[q]-score[p]+(rnd()-.5)*.5)[0];return best||null;}
function neededLetter(){const wd=S.words.find(w=>w.state==="wounded");if(wd)return wd.text[wd.missing];{const u=stuckLetters().length>=2?unlockLetter():null;if(u&&rnd()<.8)return u;}''')

rep('''if(S.agents.length>=72)return;S.lastBirth=S.lastBirth||0;S.refugeAt=S.refugeAt||300;if(S.simT<S.refugeAt)return;S.refugeAt=S.simT+200;if(S.simT-S.lastBirth<500)return;''',
    '''if(S.agents.length>=72)return;S.lastBirth=S.lastBirth||0;const stuck=S.agents.length<40&&stuckLetters().length>=3;S.refugeAt=S.refugeAt||(stuck?120:300);if(S.simT<S.refugeAt)return;S.refugeAt=S.simT+(stuck?60:200);if(S.simT-S.lastBirth<(stuck?120:500))return;''')

# A letter that finds no word nearby looks a little further each time it tries, so lone letters spread across the
# valley still find each other. Its reach resets once it belongs to a word.
rep('const free=S.agents.filter(b=>b!==a&&formable(b)&&dist(a,b)<380&&side(a.x,a.y)===side(b.x,b.y));',
    'const free=S.agents.filter(b=>b!==a&&formable(b)&&dist(a,b)<(a.reach||380)&&side(a.x,a.y)===side(b.x,b.y));')
rep('  if(!best)return false;', '  if(!best){a.reach=Math.min(1000,(a.reach||380)+90);return false;}')
rep('const members=[a,...best.pick];', 'const members=[a,...best.pick];members.forEach(m=>m.reach=380);')
