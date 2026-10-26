# Adds the Tour (scripted look + pour), two-finger side swipe to turn, and a cleaner phone layout
# to both bottle templates. Run once on each template.
import sys

TOUR_JS = r'''
// ---- Tour: a short scripted look at the bottle that ends with a pour ----
// The bottle hangs from a pivot at its middle so it can tip over for the pour.
const tiltG = new THREE.Group(); scene.add(tiltG); scene.remove(bottle); tiltG.add(bottle);
tiltG.position.set(0, CY, 0); bottle.position.y = -CY;
let camX = 0;
// under the cap: the threaded black neck and the white pour insert seen in the studio pour photos
const finishPts=[V(0,1404),V(87,1404)];
for(let h=1408; h<=1606; h+=3){ const thread = h>1452 ? 2.6*Math.max(0,Math.sin((h-1452)/9*Math.PI)) : 0; finishPts.push(V(87+thread,h)); }
finishPts.push(V(86,1610),V(84,1612),V(0,1612));
const finish=new THREE.Mesh(new THREE.LatheGeometry(finishPts,96), new THREE.MeshStandardMaterial({color:0x121212, roughness:.38, metalness:.25}));
const insert=new THREE.Mesh(new THREE.LatheGeometry([V(58,1600),V(62,1630),V(66,1638),V(79,1638),V(83,1632),V(83,1610)].map(p=>p),96), new THREE.MeshStandardMaterial({color:0xf3f1ea, roughness:.45, side:THREE.DoubleSide}));
const hole=new THREE.Mesh(new THREE.CircleGeometry(58*PX,48), new THREE.MeshStandardMaterial({color:0x3a3410, roughness:.2}));
hole.rotation.x=-Math.PI/2; hole.position.y=1601*PX;
[finish,insert,hole].forEach(m=>{ m.visible=false; bottle.add(m); });
// oil, plate and a little pool
const oilMat=new THREE.MeshPhysicalMaterial({color:0xdcc23c, roughness:.06, clearcoat:1, transparent:true, opacity:.92, emissive:0x2e2600, envMapIntensity:1.5});
let streamMesh=null;
const plate=new THREE.Mesh(new THREE.CylinderGeometry(4.6,4.2,0.22,96), new THREE.MeshStandardMaterial({color:0xf6f4ef, roughness:.32, transparent:true, opacity:0}));
const pool=new THREE.Mesh(new THREE.CircleGeometry(1,48), oilMat.clone()); pool.rotation.x=-Math.PI/2;
plate.visible=pool.visible=false; scene.add(plate); scene.add(pool);
const tipLocal=new THREE.Vector3(0,1639*PX,0), tipW=new THREE.Vector3(), baseW=new THREE.Vector3();
function pose(k){ // 0 = standing, 1 = pouring
  tiltG.position.set(-2.1*k, CY+2.7*k, 0); tiltG.rotation.z = -1.80*k; tiltG.updateMatrixWorld();
}
let tourT=null, tourStart=0, TL=null, plateX=0, pourZoom=1.4, pourX=0;
const tourBtn=document.getElementById('tour');
const ease=s=>s*s*(3-2*s);
function at(keys,t){ if(t<=keys[0][0]) return keys[0][1]; for(let i=1;i<keys.length;i++){ const [t1,v1]=keys[i], [t0,v0]=keys[i-1]; if(t<=t1){ const s=ease((t-t0)/Math.max(1e-6,t1-t0)); return v0+(v1-v0)*s; } } return keys[keys.length-1][1]; }
function startTour(){
  spinning=false; spinBtn.setAttribute('aria-pressed','false'); target.yaw=null; vel=0; hideHint();
  // work out the pour framing for this screen shape
  bottle.rotation.y=0; pose(1); bottle.updateMatrixWorld();
  bottle.localToWorld(tipW.copy(tipLocal)); bottle.localToWorld(baseW.set(0,0,0));
  plateX = tipW.x + 1.2; pose(0);
  const xmin=Math.min(baseW.x,tipW.x)-1.0, xmax=plateX+4.8, ymin=-0.3, ymax=Math.max(baseW.y,tipW.y)+1.4;
  pourX=(xmin+xmax)/2;
  const tanH=Math.tan(THREE.MathUtils.degToRad(camera.fov/2));
  pourZoom=Math.max((ymax-ymin)/2*1.1/(baseDist*tanH), (xmax-xmin)/2*1.06/(baseDist*tanH*camera.aspect), 1.05);
  plate.position.set(plateX,0.11,0); pool.position.set(tipW.x+0.25,0.226,0);
  const F=Math.PI*2, y0=((yaw%F)+F*1.5)%F-F/2; yaw=y0;
  const L=sideAngle(0.14), R=sideAngle(0.87);
  TL={
    yaw:   [[0,y0],[2.5,0],[10,0],[12.5,L],[15,L],[17.5,R],[20,R],[22,0],[34,0]],
    zoom:  [[0,zoom],[2.5,1],[4.5,0.5],[8.5,0.5],[10,1],[21,1],[23.5,pourZoom],[31,pourZoom],[33.5,1]],
    panY:  [[0,panY],[2.5,0],[4.5,1.5],[5.2,1.5],[8.6,-1.4],[10,0],[34,0]],
    pitch: [[0,pitch],[2.5,0.08],[21,0.08],[23.5,0.14],[31,0.14],[33.5,0.08]],
    camX:  [[0,0],[21,0],[23.5,pourX],[31,pourX],[33.5,0]],
    cap:   [[0,0],[20.5,0],[22.5,1],[31.5,1],[33.5,0]],
    tilt:  [[0,0],[22.5,0],[25,1],[29.6,1],[31.6,0]],
    plate: [[0,0],[21.5,0],[23,1],[31.5,1],[33,0]],
    head:  [[0,0],[24.6,0],[25.5,1],[34,1]],
    tail:  [[0,0],[29.3,0],[30.3,1],[34,1]],
    pool:  [[0,0],[25.4,0],[29.6,1],[31.5,1],[33,0]],
  };
  tourStart=performance.now(); tourT=0; tourBtn.setAttribute('aria-pressed','true');
}
function stopTour(){
  if(tourT===null) return; tourT=null; tourBtn.setAttribute('aria-pressed','false');
  pose(0); camX=0; capMesh.position.y=0; capMesh.visible=true; [finish,insert,hole].forEach(m=>m.visible=false);
  plate.visible=pool.visible=false; if(streamMesh){ scene.remove(streamMesh); streamMesh.geometry.dispose(); streamMesh=null; }
  shadow.material.opacity=1; zoom=Math.min(zoom,1.4); panY=0;
}
function tourStep(now){
  const t=(now-tourStart)/1000; tourT=t;
  if(t>34){ stopTour(); return; }
  yaw=at(TL.yaw,t); zoom=at(TL.zoom,t); panY=at(TL.panY,t); pitch=at(TL.pitch,t); camX=at(TL.camX,t);
  const cap=at(TL.cap,t), k=at(TL.tilt,t), pl=at(TL.plate,t), head=at(TL.head,t), tail=at(TL.tail,t), pk=at(TL.pool,t);
  // cap lifts straight up and away; the neck and pour insert show underneath
  capMesh.position.y = cap*2.4; capMesh.visible = cap<0.98; [finish,insert,hole].forEach(m=>m.visible=cap>0.02);
  pose(k); shadow.material.opacity=1-k;
  plate.visible=pl>0.01; plate.material.opacity=pl;
  pool.visible=pk>0.01; pool.scale.setScalar(0.15+1.35*pk); pool.material.opacity=0.9*Math.min(1,pk*3);
  // the stream runs from the pour insert down to the plate
  if(streamMesh){ scene.remove(streamMesh); streamMesh.geometry.dispose(); streamMesh=null; }
  if(head>tail+0.01 && k>0.95){
    bottle.updateMatrixWorld(); bottle.localToWorld(tipW.copy(tipLocal));
    const top=new THREE.Vector3(tipW.x+0.08,tipW.y-0.05,0), land=new THREE.Vector3(tipW.x+0.25,0.23,0);
    const curve=new THREE.CatmullRomCurve3([top, new THREE.Vector3(top.x+0.18,top.y-0.5,0), new THREE.Vector3(land.x,(top.y+land.y)/2,0), land]);
    const pts=[]; for(let i=0;i<=40;i++) pts.push(curve.getPoint(tail+(head-tail)*i/40));
    streamMesh=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),60,0.032,8), oilMat); scene.add(streamMesh);
  }
}
tourBtn.onclick=()=>{ if(tourT!==null) stopTour(); else startTour(); };
'''

def patch(path):
    t = open(path).read()
    def rep(a, b, count=1):
        nonlocal t
        assert t.count(a) == count, (path, a[:60], t.count(a))
        t = t.replace(a, b)
    # cap mesh gets a name so it can come off
    rep("bottle.add(new THREE.Mesh(capGeo, capMat));", "const capMesh=new THREE.Mesh(capGeo, capMat); bottle.add(capMesh);")
    rep("bottle.position.y = 0;\n", "")
    # tour button
    rep('<button id="spin" aria-pressed="false">Spin</button>', '<button id="spin" aria-pressed="false">Spin</button>\n    <button id="tour" aria-pressed="false" title="A short tour of the bottle, ending with a pour">Tour</button>')
    # tour code goes in just before the animation loop
    rep("function frame(now){", TOUR_JS + "\nfunction frame(now){")
    rep("  if(pts.size===0){\n    if(target.yaw!==null)", "  if(tourT!==null) tourStep(now);\n  else if(pts.size===0){\n    if(target.yaw!==null)")
    rep("  camera.position.set(0, lookY+Math.sin(pitch)*d, Math.cos(pitch)*d);\n  camera.lookAt(0,lookY,0);",
        "  camera.position.set(camX, lookY+Math.sin(pitch)*d, Math.cos(pitch)*d);\n  camera.lookAt(camX,lookY,0);")
    # zoom clamp lets the tour pull back wider than a person can
    rep("  const pm=panMax(); panY=THREE.MathUtils.clamp(panY,-pm,pm);", "  if(tourT===null){ const pm=panMax(); panY=THREE.MathUtils.clamp(panY,-pm,pm); }")
    # touching the bottle, a button or a key stops the tour
    rep("cv.addEventListener('pointerdown',e=>{", "cv.addEventListener('pointerdown',e=>{stopTour();")
    rep("spinBtn.onclick=()=>{", "spinBtn.onclick=()=>{stopTour();")
    rep("addEventListener('keydown',e=>{", "addEventListener('keydown',e=>{\n  if(e.key.startsWith('Arrow')) stopTour();")
    for b in ["document.getElementById('front').onclick=()=>{", "document.getElementById('left').onclick=()=>{", "document.getElementById('right').onclick=()=>{"]:
        rep(b, b + "stopTour();")
    # two-finger swipe: side to side turns the bottle, up and down (or a pinch) zooms
    rep("cv.addEventListener('wheel',e=>{e.preventDefault(); zoom=THREE.MathUtils.clamp(zoom*Math.exp(e.deltaY*0.001),0.45,1.4); hideHint();},{passive:false});",
        "cv.addEventListener('wheel',e=>{e.preventDefault(); stopTour();\n"
        "  if(!e.ctrlKey && Math.abs(e.deltaX)>Math.abs(e.deltaY)){ yaw+=e.deltaX*0.006; vel=0; target.yaw=null; spinning=false; spinBtn.setAttribute('aria-pressed','false'); }\n"
        "  else zoom=THREE.MathUtils.clamp(zoom*Math.exp(e.deltaY*(e.ctrlKey?0.01:0.001)),0.45,1.4);\n"
        "  hideHint();},{passive:false});")
    # phone layout: only for narrow screens, so the desktop page is untouched
    css = '''
/* phones: less around the bottle. Small back arrow, title only, no hint, small label tiles, compact buttons */
@media (max-width:720px){
  .stage{padding-block:8px 10px}
  header{position:relative;gap:0}
  .allp{position:absolute;left:0;top:2px;margin:0;padding:7px 10px;font-size:0;letter-spacing:0}
  .allp::before{content:"\\2190";font-size:15px;line-height:1}
  h1{font-size:19px;padding-inline:40px}
  .sub,.hint{display:none}
  .bar{gap:5px;flex-wrap:nowrap}
  .bar button{padding:9px 10px;font-size:10.5px;letter-spacing:.06em}
  .picks .head{display:none}
  .thumb{flex:0 0 46px !important;width:46px !important}
  .thumb .nm{display:none}
}
'''
    rep("</style>", css + "</style>")
    open(path, 'w').write(t)
    print('patched', path)

for p in sys.argv[1:]:
    patch(p)
