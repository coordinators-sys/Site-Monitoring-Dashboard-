/* ================= CCCM Somalia — PUBLIC Site Monitoring Dashboard ================= */
/* Renders ONLY from DATA, which build_public.py assembles exclusively from
   published_data.py (the officially released Q2 2026 report). There is no draft
   dataset embedded in this file at all — not hidden, not labelled, simply absent. */
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const fmt=n=>n==null?'—':n.toLocaleString('en-US');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function toast(m){const t=$('#toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200);}
function bandColor(b){return b==='Severe'?'#D9534F':b==='High'?'#EC6B4D':b==='Moderate'?'#E9A23B':b==='Low'?'#3A8D68':'#9AA5B1';}
function sevBand(pct){return pct>=55?'Severe':pct>=40?'High':pct>=25?'Moderate':'Low';}

/* ================= LANGUAGE (English / Soomaali) ================= */
/* Partial, accessibility-focused translation: navigation, headings, controls, KPI
   labels, legends and site tooltips. Long methodology/caveat prose stays English —
   the visible banner states the English version is authoritative. Somali strings
   are an IM-drafted first pass and should be reviewed by a native speaker before
   the next formal dissemination round. */
let LANG=(function(){try{return localStorage.getItem('smd_lang')||'en';}catch(e){return 'en';}})();
const I18N={
 en:{
  'nav.overview':'Overview','nav.map':'Geographic Priorities','nav.sectors':'Sector Gaps',
  'nav.districts':'District Analysis','nav.downloads':'Downloads','nav.about':'About the Data',
  'h.overview':'National Overview','h.map':'Geographic Priorities','h.sectors':'Sector Gaps',
  'h.districts':'District Analysis','h.downloads':'Downloads','h.about':'About the Data',
  'h.sectorperf':'Sector Performance','h.findings':'Key Findings','h.opsnapshot':'Operational Snapshot',
  'h.caanalysis':'Catchment analysis','h.partners':'Reporting partners',
  'label.period':'Reporting period','badge.published':'PUBLISHED RESULTS','label.view':'View',
  'label.find':'Find','btn.reset':'Reset view','label.sitefilter':'Site filter','btn.clear':'Clear',
  'layer.sev':'District severity','layer.cov':'Assessment coverage','layer.ca':'Catchment severity',
  'layer.sites':'IDP sites',
  'kpi.sites':'Sites assessed','kpi.cas':'Catchment areas assessed','kpi.districts':'Districts assessed',
  'kpi.partners':'Reporting partners','kpi.hhs':'Households','kpi.ind':'Individuals',
  'ph.find':'Zoom to a district or region…','ph.site':'Search a site name…',
  'ph.dist':'Search by district or region…','ph.ca':'Search by catchment or district…',
  'opt.allregions':'All regions','opt.alldistricts':'All districts',
  'tip.severity':'Severity','tip.partner':'Partner','tip.hh':'Households','tip.ind':'Individuals','tip.ca':'Catchment',
  'band.Severe':'Severe','band.High':'High','band.Moderate':'Moderate','band.Low':'Low',
  'legend.notreported':'Not reported','legend.notassessed':'Not assessed this period',
  'sites.of':'{a} of {b} sites plotted (sites without GPS are listed in data but cannot be mapped)',
 },
 so:{
  'nav.overview':'Guudmar','nav.map':'Mudnaanta Juqraafi','nav.sectors':'Daldaloolada Qaybaha',
  'nav.districts':'Falanqaynta Degmooyinka','nav.downloads':'Soo dejin','nav.about':'Ku saabsan Xogta',
  'h.overview':'Guudmarka Qaranka','h.map':'Mudnaanta Juqraafiga','h.sectors':'Daldaloolada Qaybaha',
  'h.districts':'Falanqaynta Degmooyinka','h.downloads':'Soo dejinta','h.about':'Ku saabsan Xogta',
  'h.sectorperf':'Waxqabadka Qaybaha','h.findings':'Natiijooyinka Muhiimka ah','h.opsnapshot':'Muuqaal Hawleed',
  'h.caanalysis':'Falanqaynta Aagagga (CA)','h.partners':'Wada-hawlgalayaasha Warbixinaya',
  'label.period':'Muddada Warbixinta','badge.published':'NATIIJOOYIN LA DAABACAY','label.view':'Muuqaal',
  'label.find':'Raadi','btn.reset':'Dib u deji','label.sitefilter':'Shaandhaynta Goobaha','btn.clear':'Tirtir',
  'layer.sev':'Darnaanta Degmada','layer.cov':'Daboolka Qiimaynta','layer.ca':'Darnaanta Aagga (CA)',
  'layer.sites':'Goobaha IDP',
  'kpi.sites':'Goobaha la qiimeeyay','kpi.cas':'Aagagga (CA) la qiimeeyay','kpi.districts':'Degmooyinka la qiimeeyay',
  'kpi.partners':'Wada-hawlgalayaasha','kpi.hhs':'Qoysas','kpi.ind':'Shakhsiyaad',
  'ph.find':'U dhaqaaq degmo ama gobol…','ph.site':'Raadi magaca goobta…',
  'ph.dist':'Raadi degmo ama gobol…','ph.ca':'Raadi aag (CA) ama degmo…',
  'opt.allregions':'Dhammaan gobollada','opt.alldistricts':'Dhammaan degmooyinka',
  'tip.severity':'Darnaanta','tip.partner':'Wada-hawlgale','tip.hh':'Qoysas','tip.ind':'Shakhsiyaad','tip.ca':'Aagga (CA)',
  'band.Severe':'Daran','band.High':'Sare','band.Moderate':'Dhexdhexaad','band.Low':'Hooseeya',
  'legend.notreported':'Lama soo sheegin','legend.notassessed':'Muddadan lama qiimayn',
  'sites.of':'{a} ka mid ah {b} goobood ayaa la muujiyay (kuwa aan GPS lahayn lama muujin karo)',
 }
};
const t=k=>(I18N[LANG]&&I18N[LANG][k])||I18N.en[k]||k;
function applyLang(){
  document.documentElement.lang = LANG==='so'?'so':'en';
  const lb=$('#langBtn'); if(lb) lb.textContent = LANG==='so'?'English':'Soomaali';
  const ln=$('#langNote'); if(ln) ln.hidden = LANG!=='so';
  $$('[data-i18n]').forEach(el=>{ el.textContent=t(el.dataset.i18n); });
  [['#mapFilter','ph.find'],['#sfSite','ph.site'],['#distFilter','ph.dist'],['#opFilter','ph.ca']]
    .forEach(([sel,key])=>{ const el=$(sel); if(el) el.placeholder=t(key); });
}
function wireLang(){
  const lb=$('#langBtn');
  if(lb) lb.addEventListener('click',()=>{
    LANG = LANG==='so'?'en':'so';
    try{localStorage.setItem('smd_lang',LANG);}catch(e){}
    applyLang(); renderAll();
  });
  applyLang();
}

/* ================= REPORTING PERIOD ================= */
/* The dashboard is a standing product, not a single-quarter report, so the period is
   a user-selectable filter rather than site branding. Every analytical surface still
   declares which period its numbers belong to — a general product must never let a
   figure appear without its period attached. */
const PERIODS = (DATA.periods && DATA.periods.length) ? DATA.periods
  : [{id:'Q2 2026', label:DATA.period, full:true, kpi:DATA.kpi, note:''}];
let CUR_PERIOD = PERIODS[0].id;
const period = () => PERIODS.find(p=>p.id===CUR_PERIOD) || PERIODS[0];
function setPeriodChips(){
  const p=period();
  [['#ovPeriodChip',p.id],['#mapPeriodChip',p.id],['#secPeriodChip',p.id],['#distPeriodChip',p.id]]
    .forEach(([sel,txt])=>{ const el=$(sel); if(el) el.textContent=txt; });
  const foot=$('#footLine');
  if(foot) foot.textContent='CCCM Cluster Somalia · Site Monitoring Dashboard · '+p.label;
}
/* Shows the "this period is not published at this granularity" note on a surface, and
   returns true when that surface must NOT render published analytics for this period. */
function periodBlocked(noteSel){
  const p=period(), el=$(noteSel);
  if(el){ el.hidden = !!p.full; el.textContent = p.full ? '' : p.note; }
  return !p.full;
}
function renderPeriodSelector(){
  const sel=$('#periodSel');
  if(!sel) return;
  sel.innerHTML=PERIODS.map(p=>`<option value="${esc(p.id)}">${esc(p.label)}</option>`).join('');
  sel.value=CUR_PERIOD;
  sel.addEventListener('change',()=>{ CUR_PERIOD=sel.value; renderAll(); });
}

/* ================= TAB NAV ================= */
$$('.tab').forEach(b=>b.addEventListener('click',()=>{
  $$('.tab').forEach(x=>x.classList.remove('active'));b.classList.add('active');
  $$('.view').forEach(v=>v.classList.remove('active'));
  $('#view-'+b.dataset.view).classList.add('active');
  if(b.dataset.view==='map') renderMap().catch(e=>console.error('[public dashboard] "map" failed:', e));
  window.scrollTo({top:0,behavior:'smooth'});
}));

/* ================= OVERVIEW ================= */
function renderOverview(){
  const p=period(), K=p.kpi;
  periodBlocked('#ovPeriodNote');   // headline KPIs exist for every period; the note explains what doesn't
  $('#ovIntro').textContent=DATA.intro;
  const cards=[
    {v:fmt(K.sites),l:t('kpi.sites')},
    {v:fmt(K.catchments),l:t('kpi.cas')},
    {v:fmt(K.districts),l:t('kpi.districts')},
    {v:fmt(K.partners),l:t('kpi.partners')},
    {v:fmt(K.hhs),l:t('kpi.hhs')},
    {v:fmt(K.individuals),l:t('kpi.ind')},
  ];
  $('#kpiRow').innerHTML=cards.map(c=>`<div class="kpi">
    <div class="k-val">${c.v}</div><div class="k-lab">${esc(c.l)}</div></div>`).join('');

  // Key Findings and the Sector Performance chart are analytical results from the
  // full-granularity report — for a headline-totals-only period they are hidden
  // outright, never left on screen carrying another period's numbers.
  $('#findingsCard').hidden=!p.full;
  $('#sectorPerfBlock').hidden=!p.full;
  const fc=$('#findingsChip'); if(fc) fc.textContent=p.id;
  const sc=$('#sectorPerfChip'); if(sc) sc.textContent=p.id;
  if(p.full){
    $('#findingsList').innerHTML=DATA.keyFindings.map(f=>`<div class="finding">
      <div class="flab">${esc(f[0])}</div>
      <div class="fval">${esc(f[1])}</div>
      <div class="fsub">${esc(f[2])}</div></div>`).join('');
  }

  const q1=DATA.q1;
  const q1q2Rows=[
    ['Sites assessed',q1.sites,DATA.kpi.sites],
    ['Catchment areas',q1.catchments,DATA.kpi.catchments],
    ['Districts',q1.districts,DATA.kpi.districts],
    ['Reporting partners',q1.partners,DATA.kpi.partners],
    ['Households',q1.hhs,DATA.kpi.hhs],
    ['Individuals',q1.individuals,DATA.kpi.individuals],
  ];
  $('#q1q2Table').innerHTML=q1q2Rows.map(([l,a,b])=>`<tr>
    <td>${esc(l)}</td><td class="ctr">${fmt(a)}</td><td class="ctr" style="font-weight:700">${fmt(b)}</td></tr>`).join('');
  $('#coverageNote').textContent=DATA.coverageNote;
  if(p.full) renderSectorDiverge();
}
function renderSectorDiverge(){
  const max=Math.max(...DATA.sectors.map(s=>Math.max(s.gap,s.cov)));
  $('#sectorDiverge').innerHTML=DATA.sectors.map(s=>{
    const gw=s.gap/max*100, cw=s.cov/max*100;
    const icon=DATA.assets.icons[s.code]?`<img class="sec-ic" src="${DATA.assets.icons[s.code]}" alt="">`:'';
    return `<div class="dv-row">
      <div class="lab">${icon}<span class="lab-text" title="${esc(s.name)}">${esc(s.name)}</span></div>
      <div class="dv-left"><div class="dv-bar gap" style="width:${gw}%"><span>${s.gap}%</span></div></div>
      <div class="dv-right"><div class="dv-bar cov" style="width:${cw}%"><span>${s.cov}%</span></div></div>
    </div>`;
  }).join('');
}

/* ================= GEOGRAPHIC PRIORITIES (Leaflet + OSM) ================= */
/* Three layers. 'sev' and 'cov' shade DISTRICTS from published results and are only
   available for a period the Cluster published at that granularity. 'ca' shades
   CATCHMENTS from the live operational feed — unreconciled, so it carries its own
   amber banner and is never mixed into the published district layers. */
let MAP_FILL='sev', MAP_HOME=null, MAP_D_LAYER=null, MAP_CA_LAYER=null, MAP_INDEX=[], MAP_FOCUS=[];
let SHOW_SITES=false, SITE_LAYER=null, SITE_RENDERER=null, SF={region:'',district:'',q:''};
const swapRing=r=>r.map(([x,y])=>[y,x]);
const caKey=(pc,ca)=>String(pc||'').toUpperCase()+String(ca||'').toUpperCase();

function opCatchments(){
  /* Operational catchment rows for the selected period, or the nearest available one. */
  if(!OP_DATA||!OP_DATA.quarters) return {rows:[],label:null};
  const keys=Object.keys(OP_DATA.quarters);
  if(!keys.length) return {rows:[],label:null};
  const k=keys.includes(CUR_PERIOD)?CUR_PERIOD:keys[keys.length-1];
  return {rows:(OP_DATA.quarters[k].catchments||[]),label:k};
}

function buildMapShell(){
  const map=L.map('pubMap',{zoomSnap:.5});
  window.__pubMap=map;
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    maxZoom:17,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
  }).addTo(map);
  MAP_D_LAYER=L.layerGroup().addTo(map);
  MAP_CA_LAYER=L.layerGroup().addTo(map);
  SITE_LAYER=L.layerGroup().addTo(map);
  $$('.map-layer').forEach(b=>{
    b.onclick=()=>{ MAP_FILL=b.dataset.layer; renderMap(); };
  });
  const st=$('#sitesToggle');
  if(st) st.onclick=async()=>{
    SHOW_SITES=!SHOW_SITES;
    if(SHOW_SITES) await ensureOperational();
    renderSitePoints();
  };
  [['#sfRegion','region'],['#sfDistrict','district']].forEach(([sel,key])=>{
    const el=$(sel);
    if(el) el.onchange=()=>{ SF[key]=el.value; if(key==='region') SF.district=''; renderSitePoints(); };
  });
  const ss=$('#sfSite');
  if(ss) ss.oninput=()=>{ SF.q=ss.value; renderSitePoints(); };
  const sc=$('#sfClear');
  if(sc) sc.onclick=()=>{ SF={region:'',district:'',q:''}; const el=$('#sfSite'); if(el) el.value='';
                          renderSitePoints(); if(MAP_HOME) map.fitBounds(MAP_HOME); };
  const fi=$('#mapFilter');
  if(fi) fi.oninput=()=>applyMapFilter(fi.value);
  const rb=$('#mapReset');
  if(rb) rb.onclick=()=>{ if(fi) fi.value=''; $('#mapFilterMsg').textContent='';
                          if(MAP_HOME) map.fitBounds(MAP_HOME); };
}

/* ---------------- IDP site points (live operational feed) ---------------- */
function opSites(){
  if(!OP_DATA||!OP_DATA.quarters) return {rows:[],order:[]};
  const keys=Object.keys(OP_DATA.quarters);
  if(!keys.length) return {rows:[],order:[]};
  const k=keys.includes(CUR_PERIOD)?CUR_PERIOD:keys[keys.length-1];
  const q=OP_DATA.quarters[k];
  return {rows:q.sites||[],order:q.sectorsOrder||[]};
}
function siteTip(s,order){
  const dotColor={G:'#3A8D68',Y:'#E9A23B',R:'#D9534F',K:'#8a8f93',NA:'#d4d7d9'};
  const secs=(s.sc||[]).map((d,i)=>
    `<span class="sd"><i style="background:${dotColor[d]||'#d4d7d9'}"></i>${esc(order[i]||'')}</span>`).join('');
  return `<div class="site-tip"><b>${esc(s.n)}</b>
    <div class="meta">${esc(s.d)}, ${esc(s.r)}${s.c?' · '+esc(t('tip.ca'))+' '+esc(s.c):''}</div>
    ${esc(t('tip.severity'))}: <span class="badge ${esc(s.b)}">${s.v}%</span> <b>${esc(t('band.'+s.b))}</b><br>
    ${esc(t('tip.partner'))}: ${esc(s.p||'—')}<br>
    ${esc(t('tip.hh'))}: ${fmt(s.hh)} · ${esc(t('tip.ind'))}: ${fmt(s.ind)}
    <div class="secs">${secs}</div></div>`;
}
function populateSiteFilters(rows){
  const regs=[...new Set(rows.map(s=>s.r).filter(Boolean))].sort();
  if(SF.region&&!regs.includes(SF.region)) SF.region='';
  const dists=[...new Set(rows.filter(s=>!SF.region||s.r===SF.region).map(s=>s.d).filter(Boolean))].sort();
  if(SF.district&&!dists.includes(SF.district)) SF.district='';
  $('#sfRegion').innerHTML=`<option value="">${esc(t('opt.allregions'))}</option>`
    +regs.map(r=>`<option value="${esc(r)}"${r===SF.region?' selected':''}>${esc(r)}</option>`).join('');
  $('#sfDistrict').innerHTML=`<option value="">${esc(t('opt.alldistricts'))}</option>`
    +dists.map(d=>`<option value="${esc(d)}"${d===SF.district?' selected':''}>${esc(d)}</option>`).join('');
}
function renderSitePoints(){
  const row=$('#siteFilterRow');
  if(row) row.style.display=SHOW_SITES?'flex':'none';
  const st=$('#sitesToggle'); if(st) st.classList.toggle('active',SHOW_SITES);
  if(!SITE_LAYER) return;
  SITE_LAYER.clearLayers();
  if(!SHOW_SITES){ const c=$('#sfCount'); if(c) c.textContent=''; return; }
  const {rows,order}=opSites();
  populateSiteFilters(rows);
  const q=SF.q.trim().toLowerCase();
  const filtered=rows.filter(s=>(!SF.region||s.r===SF.region)
    &&(!SF.district||s.d===SF.district)
    &&(!q||String(s.n).toLowerCase().includes(q)));
  if(!SITE_RENDERER) SITE_RENDERER=L.canvas({padding:.3});
  let plotted=0; const pts=[];
  filtered.forEach(s=>{
    if(s.la==null||s.lo==null) return;
    const m=L.circleMarker([s.la,s.lo],{renderer:SITE_RENDERER,radius:5,weight:1,
      color:'#fff',fillColor:bandColor(s.b),fillOpacity:.85});
    m.bindTooltip(siteTip(s,order),{sticky:true,opacity:1});
    m.addTo(SITE_LAYER); plotted++; pts.push([s.la,s.lo]);
  });
  const c=$('#sfCount');
  if(c) c.textContent=t('sites.of').replace('{a}',fmt(plotted)).replace('{b}',fmt(rows.length));
  if((SF.region||SF.district||q)&&pts.length){
    // Fit the view to the 5th–95th percentile of points: a single mistagged GPS
    // (in-country but hundreds of km off) must not zoom the map out to all Somalia.
    // Every point is still plotted — only the automatic framing ignores outliers.
    let frame=pts;
    if(pts.length>20){
      const lats=pts.map(p=>p[0]).sort((a,b)=>a-b), lons=pts.map(p=>p[1]).sort((a,b)=>a-b);
      const lo=Math.floor(pts.length*.05), hi=Math.ceil(pts.length*.95)-1;
      frame=pts.filter(p=>p[0]>=lats[lo]&&p[0]<=lats[hi]&&p[1]>=lons[lo]&&p[1]<=lons[hi]);
      if(!frame.length) frame=pts;
    }
    const b=L.latLngBounds(frame);
    if(b.isValid()) window.__pubMap.fitBounds(b.pad(0.2),{maxZoom:13});
  }
}

function applyMapFilter(q){
  const map=window.__pubMap, msg=$('#mapFilterMsg');
  if(!map) return;
  const s=String(q||'').trim().toLowerCase();
  if(!s){ msg.textContent=''; if(MAP_HOME) map.fitBounds(MAP_HOME); return; }
  const hits=MAP_INDEX.filter(e=>e.hay.includes(s));
  if(!hits.length){ msg.textContent='No match on this layer'; return; }
  let b=hits[0].bounds;
  hits.slice(1).forEach(h=>{ b=b.extend(h.bounds); });
  map.fitBounds(b,{maxZoom:11});
  msg.textContent=`${hits.length} area${hits.length>1?'s':''} matched`;
}

async function renderMap(){
  const geo=DATA.geo;
  if(!geo||typeof L==='undefined'){
    $('#pubMap').innerHTML='<p class="empty-note">Map not available in this build.</p>'; return;
  }
  if(!window.__pubMap) buildMapShell();
  const map=window.__pubMap;
  $$('.map-layer').forEach(x=>x.classList.toggle('active',x.dataset.layer===MAP_FILL));

  const alias=geo.pcodeAlias||{};
  MAP_D_LAYER.clearLayers(); MAP_CA_LAYER.clearLayers(); MAP_INDEX=[]; MAP_FOCUS=[];
  const caMode=MAP_FILL==='ca';
  const p=period();

  // The published district layers only exist for a period published at that granularity.
  const blocked=!caMode && !p.full;
  const note=$('#mapPeriodNote');
  if(note){ note.hidden=!blocked; note.textContent=blocked?p.note:''; }
  $('#caBanner').hidden=!caMode;
  $('#caPanel').hidden=!caMode;
  $('#mapIntro').textContent=caMode
    ? 'Catchment severity from the live operational feed. Catchments without published boundaries are listed in the table below but cannot be shaded.'
    : 'District severity from published results. Grey districts were not individually reported.';

  if(caMode){
    await ensureOperational();
    const {rows,label}=opCatchments();
    const byKey={}; rows.forEach(r=>{ byKey[String(r.catchment).toUpperCase()]=r; });
    const chip=$('#caPeriodChip'); if(chip) chip.textContent=label||'—';
    let drawn=0;
    (geo.catchments||[]).forEach(gc=>{
      const rec=byKey[caKey(gc.pc,gc.ca)];
      const poly=L.polygon(gc.rings.map(swapRing),{
        color:'#fff',weight:.8,
        fillColor:rec?bandColor(sevBand(rec.avgSeverity)):'#E2E5E0',
        fillOpacity:rec?.65:.25});
      poly.bindTooltip(rec
        ? `<b>${esc(gc.ca)} — ${esc(gc.d)}</b><br>${fmt(rec.n)} sites · Avg. severity ${rec.avgSeverity}%`
          +`<br>Severe ${rec.Severe} · High ${rec.High} · Moderate ${rec.Moderate} · Low ${rec.Low}`
          +'<br><i>Operational — unreconciled</i>'
        : `<b>${esc(gc.ca)} — ${esc(gc.d)}</b><br>Not assessed in this period`,{sticky:true});
      poly.addTo(MAP_CA_LAYER);
      if(rec){ drawn++; MAP_FOCUS.push(poly.getBounds()); }
      MAP_INDEX.push({hay:`${gc.ca} ${gc.d}`.toLowerCase(),bounds:poly.getBounds()});
    });
    const unmapped=rows.filter(r=>!(geo.catchments||[]).some(gc=>caKey(gc.pc,gc.ca)===String(r.catchment).toUpperCase()));
    $('#caBanner').textContent='Operational, unreconciled — live from the field data pipeline, not '
      +'Information-Management reviewed and not comparable with the published figures. '
      +`${drawn} of ${rows.length} assessed catchments have published boundaries and are shaded`
      +(unmapped.length?`; ${unmapped.length} more are listed in the table below without a map shape.`:'.');
    renderCatchmentPanel(rows,geo,label);
  }else if(!blocked){
    const byPc={}; DATA.districts.forEach(d=>{ if(d.pc) byPc[d.pc]=d; });
    const fillFor=pc=>{
      const d=byPc[(alias[pc]||pc||'').toUpperCase()];
      if(!d) return '#E2E5E0';
      return MAP_FILL==='cov' ? (d.cov>=60?'#104E5D':d.cov>=45?'#17677A':d.cov>=25?'#6FAEBD':'#C9E0E6')
                              : bandColor(sevBand(d.gap));
    };
    geo.districts.forEach(gd=>{
      const d=byPc[(alias[gd.pc]||gd.pc||'').toUpperCase()];
      const poly=L.polygon(gd.rings.map(swapRing),
        {color:'#fff',weight:.8,fillColor:fillFor(gd.pc),fillOpacity:.6});
      poly.bindTooltip(d
        ? `<b>${esc(gd.n)}</b><br>${fmt(d.n)} sites assessed · Gap ${d.gap}% / Coverage ${d.cov}%`
        : `<b>${esc(gd.n)}</b><br>Not individually reported this period`,{sticky:true});
      poly.addTo(MAP_D_LAYER);
      if(d) MAP_FOCUS.push(poly.getBounds());
      MAP_INDEX.push({hay:`${gd.n} ${gd.r||''}`.toLowerCase(),bounds:poly.getBounds()});
    });
  }

  // Default view frames the areas that actually have data for this period; unassessed
  // areas stay on the map (greyed) but don't drag the viewport out to the whole country.
  const frame = MAP_FOCUS.length ? MAP_FOCUS : MAP_INDEX.map(e=>e.bounds);
  if(frame.length){
    let b=frame[0];
    frame.slice(1).forEach(x=>{ b=b.extend(x); });
    MAP_HOME=b; map.fitBounds(b,{padding:[18,18]});
  }
  const fi=$('#mapFilter');
  if(fi){ fi.value=''; $('#mapFilterMsg').textContent=''; }
  if(SHOW_SITES){ await ensureOperational(); }
  renderSitePoints();
  renderMapLegend();
  setTimeout(()=>map.invalidateSize(),60);
}

function renderCatchmentPanel(rows,geo,label){
  const hasGeo=k=>(geo.catchments||[]).some(gc=>caKey(gc.pc,gc.ca)===String(k).toUpperCase());
  const sorted=[...rows].sort((a,b)=>b.avgSeverity-a.avgSeverity);
  $('#caPanelNote').textContent=`${sorted.length} catchments assessed in ${label||'this period'}, `
    +'ranked by average severity. Severity is the share of applicable indicators scoring Red '
    +'across the sites in that catchment.';
  $('#caTable').innerHTML=sorted.length?sorted.map(c=>`<tr>
      <td style="font-weight:600">${esc(c.catchment)}</td><td>${esc(c.district)}</td><td>${esc(c.region)}</td>
      <td class="ctr">${fmt(c.n)}</td>
      <td class="ctr"><span class="badge ${sevBand(c.avgSeverity)}">${c.avgSeverity}%</span></td>
      <td class="ctr">${fmt(c.Severe)}</td><td class="ctr">${fmt(c.High)}</td>
      <td class="ctr">${fmt(c.Moderate)}</td><td class="ctr">${fmt(c.Low)}</td>
      <td class="ctr">${hasGeo(c.catchment)?'✓':'<span class="dash">—</span>'}</td>
    </tr>`).join('') : '<tr><td colspan="10"><p class="empty-note">No catchment data for this period.</p></td></tr>';
}

function renderMapLegend(){
  const it=(c,l)=>`<span class="it"><span class="dot" style="background:${c}"></span>${l}</span>`;
  const bands=it('#D9534F',t('band.Severe')+' ≥55%')+it('#EC6B4D',t('band.High')+' 40–55%')
    +it('#E9A23B',t('band.Moderate')+' 25–40%')+it('#3A8D68',t('band.Low')+' <25%');
  if(MAP_FILL==='ca'){
    $('#mapLegend').innerHTML=bands+it('#E2E5E0',t('legend.notassessed'));
    return;
  }
  $('#mapLegend').innerHTML = MAP_FILL==='sev'
    ? bands+it('#E2E5E0',t('legend.notreported'))
    : it('#104E5D','60%+')+it('#17677A','45–59%')+it('#6FAEBD','25–44%')+it('#C9E0E6','<25%')+it('#E2E5E0',t('legend.notreported'));
}

/* ================= SECTOR GAPS ================= */
let SD_CUR=null;
function renderSectorTabs(){
  if(periodBlocked('#secPeriodNote')){
    $('#sdTabs').innerHTML='';
    $('#sdTitle').textContent='';
    $('#sdBody').innerHTML='<p class="empty-note">Sector results are not published for this reporting period.</p>';
    $('#topGapsList').innerHTML='<p class="empty-note">Indicator-level gaps are not published for this reporting period.</p>';
    return;
  }
  SD_CUR=SD_CUR||DATA.sectors[0].code;
  $('#sdTabs').innerHTML=DATA.sectors.map(s=>{
    const icon=DATA.assets.icons[s.code]?`<img src="${DATA.assets.icons[s.code]}" alt="">`:'';
    return `<button class="sd-tab ${s.code===SD_CUR?'active':''}" data-c="${s.code}">${icon}${esc(s.name)}</button>`;
  }).join('');
  $$('#sdTabs .sd-tab').forEach(b=>b.addEventListener('click',()=>{SD_CUR=b.dataset.c;renderSectorTabs();renderSectorBody();}));
  renderSectorBody();
}
function renderSectorBody(){
  const s=DATA.sectors.find(x=>x.code===SD_CUR);
  $('#sdTitle').innerHTML=`${esc(s.name)} <span class="hint">Gap ${s.gap}% · Coverage ${s.cov}%</span>`;
  const rows=DATA.topRed.concat(DATA.topGreen).filter(r=>r.sector===SD_CUR);
  if(!rows.length){
    $('#sdBody').innerHTML='<p class="empty-note">No indicator-level detail published for this sector this quarter. '
      +'Sector-wide gap and coverage percentages are shown above.</p>';
    return;
  }
  $('#sdBody').innerHTML=rows.map(r=>`<div class="tri-row">
    <div class="l" title="${esc(r.indicator)}">${esc(r.indicator)}${r.lc?' <span style="color:var(--muted);font-size:10px">(LC)</span>':''}</div>
    <div class="tri-bar"><div class="tri-seg ${r.kind==='red'?'r':'g'}" style="width:${r.pct}%"></div></div>
    <div class="ctr" style="font-weight:700">${r.pct}%</div></div>`).join('')
    +(rows.some(r=>r.lc)?`<p style="margin:10px 0 0;font-size:11px;color:var(--muted)">${esc(DATA.lcNote)}</p>`:'');
}
function renderTopGaps(){
  if(!period().full) return;   // renderSectorTabs already wrote the unavailable note
  const rows=[...DATA.topRed].sort((a,b)=>b.pct-a.pct);
  $('#topGapsList').innerHTML=rows.map(r=>`<div class="hbar-row">
    <div class="l" title="${esc(r.indicator)}">${esc(r.indicator)}</div>
    <div class="hbar-track"><div class="hbar-fill" style="width:${r.pct}%;background:var(--gap)"></div></div>
    <div class="v" style="color:var(--gap)">${r.pct}%</div></div>`).join('');
}

/* ================= DISTRICT ANALYSIS ================= */
const DIST_ROWS=()=>[...DATA.districts].sort((a,b)=>b.gap-a.gap);
function paintDistrictRows(rows){
  $('#distTable').innerHTML=rows.length?rows.map(d=>{
    const band=sevBand(d.gap);
    const bandCell=k=>d.bands?fmt(d.bands[k]):'<span class="dash">—</span>';
    return `<tr>
      <td style="font-weight:600">${esc(d.district)}</td><td>${esc(d.region)}</td>
      <td class="ctr">${fmt(d.n)}</td>
      <td class="ctr"><span class="badge ${band}">${d.gap}%</span></td>
      <td class="ctr">${bandCell('Severe')}</td><td class="ctr">${bandCell('High')}</td>
      <td class="ctr">${bandCell('Moderate')}</td><td class="ctr">${bandCell('Low')}</td>
      <td style="font-size:12px">${esc(d.mainGap||'—')}</td>
    </tr>`;
  }).join('') : `<tr><td colspan="9"><p class="empty-note">No districts match this filter.</p></td></tr>`;
}
function renderDistricts(){
  $('#partnerChips').innerHTML=DATA.partners.map(p=>
    `<span class="pub-chip-sm" style="padding:5px 11px;font-size:12px">${esc(p)}</span>`).join('');
  renderOperational().catch(e=>console.error('[public dashboard] "operational" failed:', e));
  if(periodBlocked('#distPeriodNote')){
    $('#distTable').innerHTML='<tr><td colspan="9"><p class="empty-note">District rankings are not '
      +'published for this reporting period.</p></td></tr>';
    $('#distFootnote').textContent='';
    $('#distFilterCount').textContent='';
    const fi=$('#distFilter'); if(fi){ fi.value=''; fi.disabled=true; }
    return;
  }
  const fi=$('#distFilter'); if(fi) fi.disabled=false;
  const all=DIST_ROWS();
  paintDistrictRows(all);
  const total=all.length;
  const input=$('#distFilter');
  const apply=()=>{
    const q=input.value.trim().toLowerCase();
    const rows=q?all.filter(d=>d.district.toLowerCase().includes(q)||d.region.toLowerCase().includes(q)):all;
    paintDistrictRows(rows);
    $('#distFilterCount').textContent=q?`${rows.length} of ${total} districts`:'';
  };
  input.value='';
  input.oninput=apply;
  $('#distFootnote').innerHTML=DATA.districtFootnote;
}

/* ================= OPERATIONAL SNAPSHOT (unreconciled) ================= */
let OP_Q=null, OP_DATA=null, OP_LIVE=false;
function paintOpRows(rows){
  $('#opTable').innerHTML=rows.length?rows.map(c=>`<tr>
      <td style="font-weight:600">${esc(c.catchment)}</td><td>${esc(c.district)}</td><td>${esc(c.region)}</td>
      <td class="ctr">${fmt(c.n)}</td>
      <td class="ctr"><span class="badge ${sevBand(c.avgSeverity)}">${c.avgSeverity}%</span></td>
      <td class="ctr">${fmt(c.Severe)}</td><td class="ctr">${fmt(c.High)}</td>
      <td class="ctr">${fmt(c.Moderate)}</td><td class="ctr">${fmt(c.Low)}</td>
    </tr>`).join('') : `<tr><td colspan="9"><p class="empty-note">No catchments match this filter.</p></td></tr>`;
}
let OP_PROMISE=null;
/* One fetch per page load, shared by the Operational Snapshot table and the map's
   catchment layer — switching period or tab must not re-hit the endpoint. */
function ensureOperational(){
  if(!OP_PROMISE) OP_PROMISE=loadOperationalData().then(op=>{ OP_DATA=op; return op; });
  return OP_PROMISE;
}
async function loadOperationalData(){
  // Prefer the live endpoint (queries Kobo/Zite server-side, token never reaches the
  // browser, edge-cached ~10 min). Fall back to the snapshot baked in at build time —
  // labelled as such — if the live call fails (network issue, Kobo/Zite outage, etc.)
  // so the section degrades gracefully instead of breaking.
  try{
    const r=await fetch('/api/operational',{headers:{'Accept':'application/json'}});
    if(!r.ok) throw new Error('HTTP '+r.status);
    const j=await r.json();
    if(!j||!j.quarters) throw new Error('malformed response');
    OP_LIVE=true;
    return j;
  }catch(e){
    console.warn('[public dashboard] live operational endpoint unavailable, using build-time snapshot:', e);
    OP_LIVE=false;
    return DATA.operational&&DATA.operational.available?
      {generatedNote:DATA.operational.note,generatedAt:null,quarters:DATA.operational.quarters}:null;
  }
}
function paintOperational(op){
  const qkeys=Object.keys(op.quarters);
  OP_Q=OP_Q&&qkeys.includes(OP_Q)?OP_Q:qkeys[qkeys.length-1];
  $('#opQuarterTabs').innerHTML=qkeys.map(k=>
    `<button class="op-tab ${k===OP_Q?'active':''}" data-q="${esc(k)}">${esc(k)}</button>`).join('');
  $$('#opQuarterTabs .op-tab').forEach(b=>b.addEventListener('click',()=>{OP_Q=b.dataset.q;paintOperational(OP_DATA);}));
  const q=op.quarters[OP_Q];
  const all=[...(q.catchments||[])].sort((a,b)=>b.avgSeverity-a.avgSeverity);
  paintOpRows(all);
  const input=$('#opFilter');
  const apply=()=>{
    const s=input.value.trim().toLowerCase();
    const rows=s?all.filter(c=>c.catchment.toLowerCase().includes(s)||c.district.toLowerCase().includes(s)):all;
    paintOpRows(rows);
    $('#opFilterCount').textContent=s?`${rows.length} of ${all.length} catchments`:`${all.length} catchments · ${q.kpi.sites} sites (${OP_Q})`;
  };
  input.value=''; input.oninput=apply; apply();
}
async function renderOperational(){
  const op=await ensureOperational();
  if(!op||!op.quarters||!Object.keys(op.quarters).length){ return; }
  $('#opSection').hidden=false;
  const src=$('#opSourceNote');
  if(src) src.textContent=OP_LIVE
    ? 'Live — queried directly from Kobo/Zite'+(op.generatedAt?` as of ${esc(op.generatedAt)}`:'')+'.'
    : 'Live endpoint unreachable right now — showing the last snapshot generated at deploy time, not a real-time read.';
  // The header period selector drives this section too; the chips below still let a
  // user compare periods without changing the whole page.
  if(Object.keys(op.quarters).includes(CUR_PERIOD)) OP_Q=CUR_PERIOD;
  paintOperational(op);
}

/* ================= DOWNLOADS ================= */
function csvDownload(name, rows){
  const csv=rows.map(r=>r.map(x=>`"${String(x??'').replace(/"/g,'""')}"`).join(',')).join('\n');
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob(['﻿'+csv],{type:'text/csv;charset=utf-8'}));
  a.download=name; a.click(); toast('Downloaded '+name);
}
function metaHeader(title){
  const p=period();
  return [['CCCM Cluster Somalia — Site Monitoring Dashboard'],[title],
    ['Status','PUBLISHED'],['Reporting period', p.label],
    ['Data source', DATA.source],['Generated', DATA.generated],
    ['Contact', DATA.contact.im],['Methodology','See the About the Data page'],[]];
}
function renderDownloads(){
  const p=period(), K=p.kpi, slug='cccm_'+p.id.toLowerCase().replace(/[^a-z0-9]+/g,'_');
  // Every period publishes headline coverage; only a full-granularity period publishes
  // the district and sector tables, so those buttons simply are not offered otherwise —
  // an export must never be able to carry another period's numbers under this label.
  const items=[
    ['KPI summary',()=>csvDownload(slug+'_kpi_summary.csv',[...metaHeader('KPI summary'),
      ['Metric','Value'],['Sites assessed',K.sites],['Catchment areas',K.catchments],
      ['Districts',K.districts],['Reporting partners',K.partners],
      ['Households',K.hhs],['Individuals',K.individuals]]
      .concat(K.severity!=null?[['National severity %',K.severity]]:[]))],
  ];
  if(p.full){
    items.push(
      ['District summary',()=>csvDownload(slug+'_district_summary.csv',[...metaHeader('District summary'),
        ['District','Region','Sites','Gap %','Coverage %','Severe','High','Moderate','Low'],
        ...DATA.districts.map(d=>[d.district,d.region,d.n,d.gap,d.cov,
          d.bands?d.bands.Severe:'',d.bands?d.bands.High:'',d.bands?d.bands.Moderate:'',d.bands?d.bands.Low:''])])],
      ['Sector-gap table',()=>csvDownload(slug+'_sector_gaps.csv',[...metaHeader('Sector gaps'),
        ['Sector','Gap %','Coverage %'],...DATA.sectors.map(s=>[s.name,s.gap,s.cov])])]);
  }
  items.push(['Methodology note',()=>csvDownload(slug+'_methodology_note.csv',[...metaHeader('Methodology note'),
    ['Section','Content'],['Purpose',DATA.about.purpose],['Severity definition',DATA.about.severity],
    ...DATA.about.limits.map((l,i)=>['Limitation '+(i+1),l])])]);

  $('#dlList').innerHTML=items.map(([t],i)=>`<button class="dl-btn" data-di="${i}">
    <span>⬇ ${esc(t)}</span><span class="dmeta"><span class="pub-chip-sm">PUBLISHED</span> · ${esc(p.id)}</span></button>`).join('')
    +(p.full?'':`<p class="empty-note" style="text-align:left">District and sector exports are not offered for `
      +`${esc(p.id)} because they were not published at that granularity.</p>`);
  $$('#dlList .dl-btn').forEach(b=>b.addEventListener('click',()=>items[+b.dataset.di][1]()));
}

/* ================= ABOUT THE DATA ================= */
function renderAbout(){
  const a=DATA.about;
  $('#mPurpose').innerHTML=`<p>${esc(a.purpose)}</p>`;
  $('#mSources').innerHTML=`<p><b>Reporting period shown:</b> ${esc(period().label)}</p>
    <p><b>Source:</b> ${esc(DATA.source)}</p>
    <p><b>Data sources:</b> CCCM partner site-monitoring submissions, reported quarterly.</p>
    <p><b>Periods available:</b> ${PERIODS.map(p=>esc(p.id)+(p.full?'':' (headline totals only)')).join(' · ')}. `
    +`Use the reporting-period selector in the header to switch.</p>`;
  $('#mSeverity').innerHTML=`<p>${esc(a.severity)}</p>`;
  $('#mLimits').innerHTML=`<ul>${a.limits.map(l=>`<li>${esc(l)}</li>`).join('')}</ul>`;
  $('#mContact').innerHTML=`<p>Information Management: <a href="mailto:${DATA.contact.im}">${DATA.contact.im}</a></p>
    <p>Coordination: <a href="mailto:${DATA.contact.coordination}">${DATA.contact.coordination}</a></p>`;
  $('#genLine').textContent='Generated '+DATA.generated;
}

/* ================= HELP MODAL ================= */
function wireHelp(){
  const modal=$('#helpModal'), open=$('#helpBtn'), close=$('#helpX');
  const show=v=>{ modal.hidden=!v; if(v)(close||modal).focus(); else open.focus(); };
  open.addEventListener('click',()=>show(true));
  close.addEventListener('click',()=>show(false));
  modal.addEventListener('click',e=>{ if(e.target===modal) show(false); });
  document.addEventListener('keydown',e=>{ if(e.key==='Escape'&&!modal.hidden) show(false); });
}

/* ================= INIT ================= */
function renderBrand(){
  const lg=$('#brandLogo');
  if(lg&&DATA.assets.logo) lg.src=DATA.assets.logo;
}
/* Everything that depends on the selected reporting period. Each renderer is isolated
   so one failure can't blank the page. */
function renderAll(){
  [['period chips',setPeriodChips],['overview',renderOverview],['sector tabs',renderSectorTabs],
   ['top gaps',renderTopGaps],['districts',renderDistricts],['downloads',renderDownloads],
   ['about',renderAbout]
  ].forEach(([label,fn])=>{ try{ fn(); } catch(e){ console.error('[public dashboard] "'+label+'" failed:', e); } });
  // Only re-draw the map if it has already been built (it lazy-inits on first tab visit).
  if(window.__pubMap) renderMap().catch(e=>console.error('[public dashboard] "map" failed:', e));
}

[['brand',renderBrand],['period selector',renderPeriodSelector],['help modal',wireHelp],
 ['language',wireLang]
].forEach(([label,fn])=>{ try{ fn(); } catch(e){ console.error('[public dashboard] "'+label+'" failed:', e); } });
renderAll();
