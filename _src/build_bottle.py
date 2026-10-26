import json
t=open('v6.template.html').read(); d=json.load(open('tex4.json'))
open('v6.html','w').write(t.replace('__TEX_JSON__',json.dumps(d)))
r=t.replace("https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js","../three.module.min.js").replace('__TEX_JSON__',json.dumps(d))
i=r.index('</style>')+len('</style>')
head='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="robots" content="noindex, nofollow">\n<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n'
open('/home/claude/wild-groves-box/bottle/index.html','w').write(head+r[:i]+'\n</head>\n<body>'+r[i:]+'\n</body>\n</html>\n')
print('bottle built')
