# Public launch (27 September 2026): wording for real players, and sharing that works on letterheads.live.
# Run from assemble.py via exec(), after trailer_patch.py.
rep('Joining happens only on this device in this prototype.','Joining is free, needs no account, and lives only on this device.')
rep('<h3>About this prototype</h3>','<h3>About Letterheads</h3>')
rep('The world lives while this page is open and is saved on this device.','The world lives while this page is open and is saved only in this browser: no accounts, no ads, no tracking.')
rep("Preview an era (for demos; the world's own clock is unchanged):","Peek at another era (your world's own clock keeps running):")
rep('const text=`${m.text} (Letterheads, day ${m.day})`;','const text=`${m.text} (Letterheads, day ${m.day}) https://letterheads.live`;')
# Outside claude.ai there is no save prompt, so offer the picture as a normal download.
rep('if(!blob&&copied){note("The words are copied. Paste them anywhere.");return;}',
    'if(!dl&&blob&&!window.claude){const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="letterheads-moment.jpg";document.body.appendChild(a);a.click();a.remove();note(copied?"Picture saved, and the words are copied. Paste them with it.":"Picture saved.");return;}\n  if(!blob&&copied){note("The words are copied. Paste them anywhere.");return;}')
