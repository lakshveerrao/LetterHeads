import json,os
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__))
ids=[p['id'] for p in json.load(open(D+'/../terrain/places.json'))]
s=Image.new('RGB',(720,480*len(ids)))
for i,f in enumerate(ids):s.paste(Image.open(f'{D}/{f}_ground.jpg'),(0,i*480))
s.save(D+'/ground.jpg',quality=80,optimize=True,progressive=True)
print(os.path.getsize(D+'/ground.jpg'))
