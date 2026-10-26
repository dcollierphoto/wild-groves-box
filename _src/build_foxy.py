# Builds the Foxy bottle viewer and the Foxy label gallery.
# The label list lives in foxy/labels.json in the repo. The studio page edits that file too, so this
# script only ADDS labels it knows about that aren't there yet, keeps whatever names/order/foil the
# studio set, and never brings back a label the studio removed (listed under "removed").
from PIL import Image
import json, os
A='/mnt/user-data/attachments/241b421a-0ea5-57db-b0a6-97921a4abd10/'
REPO='/home/claude/wild-groves-box/foxy'
LABELS=[('02576135','Painted Fox'),('1f51367f','Harvest Branch'),('61e68d24','Pink Panel'),('017af5d8','Oil Splash'),
        ('20a3e28f','Black Foxy'),('a3c6823d','Hand-Lettered'),('ae378c09','Golden'),('c4711013','Painted Branch'),('8dacbfe6','Olive Row'),('5b145c1d','Big Olives'),('3cd78491','Fire Fox'),('53c9ed9d','Painted Fox Red')]
os.makedirs(f'{REPO}/img',exist_ok=True)
mpath=f'{REPO}/labels.json'
man=json.load(open(mpath)) if os.path.exists(mpath) else {}
man.setdefault('product',{'key':'foxy','name':'Foxy','sub':'Highest polyphenol · 500 mL','color':'#dc4e90'})
man.setdefault('labels',[]); man.setdefault('removed',[])
have={L['id'] for L in man['labels']}
for k,(f,name) in enumerate(LABELS):
    lid=f'{k+1:02d}'
    if lid in have or lid in man['removed']: continue
    im=Image.open(A+f+'-image.png').convert('RGB'); w,h=im.size
    full=f'img/{lid}.webp'; th=f'img/t{lid}.webp'; card=f'img/c{lid}.webp'
    if not os.path.exists(f'{REPO}/{full}'): im.resize((2048,int(2048*6.4967/7.0)),Image.LANCZOS).save(f'{REPO}/{full}','WEBP',quality=86,method=6)
    if not os.path.exists(f'{REPO}/{th}'): im.crop((int(w*0.27),int(h*0.04),int(w*0.73),int(h*0.62))).resize((168,200),Image.LANCZOS).save(f'{REPO}/{th}','WEBP',quality=84)
    if not os.path.exists(f'{REPO}/{card}'): im.resize((720,int(720*h/w)),Image.LANCZOS).save(f'{REPO}/{card}','WEBP',quality=84)
    man['labels'].append({'id':lid,'name':name,'full':full,'thumb':th,'card':card})
man['rev']=man.get('rev',0)+1
json.dump(man,open(mpath,'w'),indent=1,ensure_ascii=False)

d=json.load(open('tex_foxy.json'))
TEX={'glass':d['glass'],'rm':d['rm'],'fallback':man}
t=open('foxy.template.html').read()
r=t.replace("https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js","../three.module.min.js").replace('__TEX_JSON__',json.dumps(TEX))
i=r.index('</style>')+len('</style>')
head='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="robots" content="noindex, nofollow">\n<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n'
open(f'{REPO}/index.html','w').write(head+r[:i]+'\n</head>\n<body>'+r[i:]+'\n</body>\n</html>\n')
g=open('foxy_labels.template.html').read().replace('__FALLBACK__',json.dumps(man))
os.makedirs(f'{REPO}/labels',exist_ok=True)
open(f'{REPO}/labels/index.html','w').write(g)
# the studio copies these pages as the starting point for a brand-new product (same 500 mL bottle)
TP='/home/claude/wild-groves-box/product-template'
os.makedirs(f'{TP}/labels',exist_ok=True)
blank={'product':{'key':'new','name':'New product','sub':'500 mL','color':'#6f7d3c'},'labels':[],'removed':[]}
T2={**TEX,'fallback':blank}
open(f'{TP}/index.html','w').write(head+r[:i]+'\n</head>\n<body>'+r[i:].replace(json.dumps(TEX),json.dumps(T2))+'\n</body>\n</html>\n')
open(f'{TP}/labels/index.html','w').write(open('foxy_labels.template.html').read().replace('__FALLBACK__',json.dumps(blank)))
if not os.path.exists(f'{TP}/labels.json'): json.dump(blank,open(f'{TP}/labels.json','w'),indent=1)
# local test copy of the viewer with three.js from the CDN
open('foxy.html','w').write(t.replace('__TEX_JSON__',json.dumps(TEX)))
print('built', len(man['labels']), 'labels, rev', man['rev'])
