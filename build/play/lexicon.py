# Builds the spelling dictionary: everyday English words (wordfreq's frequency list) that a real dictionary also
# lists as ordinary lower-case words (Webster's web2 and GCIDE, via the english-words package), so names and brands
# drop out. Rude words are removed with better_profanity's list plus a few extra. Most common words come first.
import re
from wordfreq import top_n_list
from english_words import get_english_words_set as g
from better_profanity import profanity
real=set(x for x in g(['web2'],lower=False)|g(['gcide'],lower=False) if x.isalpha() and x.islower())
bad=set(str(w).lower() for w in profanity.CENSOR_WORDSET)
extra="sex sexy porn nude naked kill killer rape nazi drug drugs cocaine heroin crack weed bomb gun guns suicide murder slave slaves damn hell bloody crap pee poop fart butt booze beer vodka whisky whiskey wine drunk sodding bugger bollocks idiot stupid".split()
bad|=set(extra)
allow={'butter','buttered','buttery','butters'}
out=[]
for w in top_n_list('en',150000):
    if not re.fullmatch('[a-z]{3,12}',w) or w not in real: continue
    if w not in allow and (w in bad or any(w.endswith(s) and w[:-len(s)] in bad for s in ('s','es','ed','ing','er','ers','y','ies'))): continue
    out.append(w.upper())
open('lexicon.txt','w').write('\n'.join(out))
print(len(out), sum(len(x)+1 for x in out))
