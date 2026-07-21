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
// Catchment codes are stored full (e.g. SO2401CA10) for the map join, but displayed
// short (CA10) — the district prefix is redundant next to the district column. Sites
// whose catchment field held no valid code show a dash.
function catShow(c){ c=String(c||''); if(!c||c==='(catchment not recorded)') return '—';
  return c.replace(/^SO\d+/i,''); }

/* ================= LANGUAGE (English / Soomaali) ================= */
/* Partial, accessibility-focused translation: navigation, headings, controls, KPI
   labels, legends and site tooltips. Long methodology/caveat prose stays English —
   the visible banner states the English version is authoritative. Somali strings
   are an IM-drafted first pass and should be reviewed by a native speaker before
   the next formal dissemination round. */
let LANG=(function(){try{return localStorage.getItem('smd_lang')||'en';}catch(e){return 'en';}})();
const I18N={
 en:{
  'nav.overview':'Overview','nav.map':'Geographic Analysis','nav.sectors':'Sector Analysis',
  'nav.districts':'District Profiles','nav.downloads':'Data & Downloads','nav.about':'About the Data',
  'h.overview':'National Overview','h.map':'Geographic Analysis','h.sectors':'Sector Analysis',
  'h.districts':'District Profiles','h.downloads':'Data & Downloads','h.downloads2':'Published downloads','h.about':'About the data',
  'btn.viewop':'View provisional operational data (live field data)',
  'dk.sites':'Sites assessed','dk.cas':'Catchments','dk.hh':'Households','dk.ind':'Individuals',
  'dk.sev':'Avg. severity','dk.gap':'Gap %','dk.cov':'Coverage %','dk.rank':'National rank',
  'dh.sevdist':'Severity distribution','dh.topgaps':'Top service gaps','dh.partners':'Reporting partners',
  'dh.q1q2':'Assessment coverage, Q1 vs Q2','dh.cas':'Catchments assessed',
  'd.published':'Published summary','d.operational':'Operational detail (live field data)',
  'd.nolive':'No live operational detail for this district in the selected period.',
  'd.opengeo':'Show on map','close':'Close',
  'd.pubnote':'Officially published, Information-Management reviewed figures for this district.',
  'd.notpublished':'This district was not individually published for the selected period. Open the provisional operational detail below for live field figures.',
  'd.viewop':'View provisional operational detail',
  'd.opwarn':'LIVE FIELD DATA — not Information-Management reviewed and not comparable with the published figures above. Do not cite for donor reporting.',
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
  'legend.notreported':'Not reported','legend.notassessed':'Not assessed this period','map.loading':'Loading map…',
  'sites.of':'{a} of {b} sites plotted (sites without GPS are listed in data but cannot be mapped)',
  'gf.title':'Filters','gf.state':'State','gf.region':'Region','gf.district':'District','gf.catchment':'Catchment',
  'gf.partner':'Partner','gf.sector':'Sector','gf.severity':'Severity','gf.search':'Site search','gf.reset':'Reset all',
  'gf.note':'Operational — filters apply to live site-level field data, not the published summary figures above.',
  'gf.matchsites':'Matching sites','gf.download':'⬇ Download filtered sites (CSV)',
  'gf.allstates':'All states','gf.allregions':'All regions','gf.alldistricts':'All districts',
  'gf.allcatchments':'All catchments','gf.allpartners':'All partners','gf.allsectors':'All sectors','gf.allseverity':'All severity',
  'gf.matchnote':'{n} sites match the current filters.','gf.nomatch':'No sites match the current filters.',
  'gf.capped':'Showing the first {cap} of {n} matching sites — narrow the filters or download the full set.',
  'gf.site':'Site',
 },
 so:{
  'nav.overview':'Guudmar','nav.map':'Falanqaynta Juqraafi','nav.sectors':'Falanqaynta Qaybaha',
  'nav.districts':'Astaamaha Degmooyinka','nav.downloads':'Xog & Soo dejin','nav.about':'Ku saabsan Xogta',
  'h.overview':'Guudmarka Qaranka','h.map':'Falanqaynta Juqraafiga','h.sectors':'Falanqaynta Qaybaha',
  'h.districts':'Astaamaha Degmooyinka','h.downloads':'Xog & Soo dejin','h.downloads2':'Soo dejinta la daabacay','h.about':'Ku saabsan xogta',
  'btn.viewop':'Fiiri xogta hawleed ee ku-meel-gaadhka ah (toos, aan la xaqiijin)',
  'dk.sites':'Goobaha la qiimeeyay','dk.cas':'Aagag (CA)','dk.hh':'Qoysas','dk.ind':'Shakhsiyaad',
  'dk.sev':'Celceliska darnaanta','dk.gap':'Daldalool %','dk.cov':'Daboolid %','dk.rank':'Darajada Qaranka',
  'dh.sevdist':'Qaybinta darnaanta','dh.topgaps':'Daldaloolada ugu waaweyn','dh.partners':'Wada-hawlgalayaasha',
  'dh.q1q2':'Daboolka qiimaynta, Q1 iyo Q2','dh.cas':'Aagagga la qiimeeyay',
  'd.published':'Kooban la daabacay','d.operational':'Faahfaahin hawleed (xog goobeed toos ah)',
  'd.nolive':'Ma jiro faahfaahin hawleed oo toos ah degmadan muddada la doortay.',
  'd.opengeo':'Ku muuji khariidada','close':'Xir',
  'd.pubnote':'Tirooyin rasmi ah oo la daabacay, oo Maaraynta Xogta dib u eegtay degmadan.',
  'd.notpublished':'Degmadan si gaar ah looma daabicin muddada la doortay. Fur faahfaahinta hawleed ee ku-meel-gaadhka ah ee hoose.',
  'd.viewop':'Fiiri faahfaahinta hawleed ee ku-meel-gaadhka ah',
  'd.opwarn':'XOG GOOBEED TOOS AH — aan Maaraynta Xogta dib u eegin, lamana barbardhigi karo tirooyinka la daabacay ee kor ku xusan. Ha u soo xigan warbixinta deeq-bixiyaha.',
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
  'legend.notreported':'Lama soo sheegin','legend.notassessed':'Muddadan lama qiimayn','map.loading':'Khariidada waa la soo rarayaa…',
  'sites.of':'{a} ka mid ah {b} goobood ayaa la muujiyay (kuwa aan GPS lahayn lama muujin karo)',
  'gf.title':'Shaandhaynta','gf.state':'Gobol-dowladeed','gf.region':'Gobol','gf.district':'Degmo','gf.catchment':'Aag (CA)',
  'gf.partner':'Wada-hawlgale','gf.sector':'Qayb','gf.severity':'Darnaan','gf.search':'Raadi goob','gf.reset':'Dib u deji dhammaan',
  'gf.note':'Hawleed — shaandhayntu waxay khusaysaa xog goobeed toos ah, ma aha tirooyinka la daabacay ee kor ku xusan.',
  'gf.matchsites':'Goobaha u dhigma','gf.download':'⬇ Soo dejiso goobaha la shaandhay (CSV)',
  'gf.allstates':'Dhammaan gobol-dowladeedyada','gf.allregions':'Dhammaan gobollada','gf.alldistricts':'Dhammaan degmooyinka',
  'gf.allcatchments':'Dhammaan aagagga','gf.allpartners':'Dhammaan wada-hawlgalayaasha','gf.allsectors':'Dhammaan qaybaha','gf.allseverity':'Dhammaan darnaanta',
  'gf.matchnote':'{n} goobood ayaa u dhigma shaandhaynta hadda.','gf.nomatch':'Ma jiraan goobo u dhigma shaandhaynta hadda.',
  'gf.capped':'Waxaa la muujinayaa {cap} ka mid ah {n} goobood — cufi shaandhaynta ama soo deji dhammaan.',
  'gf.site':'Goob',
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
// Published analytical payload for the active period. Each period carries its own
// sectors / indicators / district ranking / findings; fall back to the top-level
// (Q2) copy for any field a period does not define.
function PD(){
  const p=period();
  return {
    sectors: p.sectors||DATA.sectors, topRed: p.topRed||DATA.topRed,
    topGreen: p.topGreen||DATA.topGreen, districts: p.districts||DATA.districts,
    districtFootnote: p.districtFootnote||DATA.districtFootnote,
    keyFindings: p.keyFindings||DATA.keyFindings,
    lcNote: p.lcNote!=null?p.lcNote:DATA.lcNote,
  };
}
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
/* Single source of truth for which view is active — used by tab clicks and by the
   drawer's "Show on map". Updates the active class, aria-current and the visible view
   together so the underline can never lag on a previous tab. */
function activateView(view){
  $$('.tab').forEach(x=>{
    const on = x.dataset.view===view;
    x.classList.toggle('active', on);
    if(on) x.setAttribute('aria-current','page'); else x.removeAttribute('aria-current');
    if(x.blur) x.blur();
  });
  $$('.view').forEach(v=>v.classList.remove('active'));
  const el=$('#view-'+view); if(el) el.classList.add('active');
  if(view==='map') renderMap().catch(e=>console.error('[public dashboard] "map" failed:', e));
}
$$('.tab').forEach(b=>b.addEventListener('click',()=>{
  activateView(b.dataset.view);
  window.scrollTo({top:0,behavior:'smooth'});
}));

/* ================= OVERVIEW ================= */
function renderOverview(){
  const p=period(), K=p.kpi;
  periodBlocked('#ovPeriodNote');   // headline KPIs exist for every period; the note explains what doesn't
  $('#ovIntro').textContent=DATA.intro;
  // Comparison against the other reporting period, labelled explicitly as an
  // assessment-coverage change — never implying humanitarian conditions changed.
  const other=PERIODS.find(x=>x.id!==p.id);
  const cmp=(key)=>{
    if(!other) return '';
    const d=(K[key]||0)-(other.kpi[key]||0);
    if(d===0) return `same as ${other.id}`;
    return `${fmt(Math.abs(d))} ${d<0?'fewer':'more'} than ${other.id}`;
  };
  const cards=[
    {v:fmt(K.sites),l:t('kpi.sites'),s:cmp('sites'),view:'map',act:'sites'},
    {v:fmt(K.catchments),l:t('kpi.cas'),s:cmp('catchments'),view:'map',act:'ca'},
    {v:fmt(K.districts),l:t('kpi.districts'),s:cmp('districts'),view:'districts'},
    {v:fmt(K.partners),l:t('kpi.partners'),s:cmp('partners'),view:'districts',act:'partners'},
    {v:fmt(K.hhs),l:t('kpi.hhs'),s:cmp('hhs'),view:'districts'},
    {v:fmt(K.individuals),l:t('kpi.ind'),s:cmp('individuals'),view:'districts'},
  ];
  $('#kpiRow').innerHTML=cards.map((c,i)=>`<div class="kpi clickable" role="button" tabindex="0"
    data-view="${c.view}"${c.act?` data-act="${c.act}"`:''} aria-label="${esc(c.l)}: ${esc(String(c.v))}">
    <div class="k-val">${c.v}</div><div class="k-lab">${esc(c.l)}</div>
    ${c.s?`<div class="k-sub">${esc(c.s)}</div>`:''}</div>`).join('');
  $$('#kpiRow .kpi').forEach(k=>{
    const go=()=>{ activateView(k.dataset.view);
      if(k.dataset.act==='sites'){ SHOW_SITES=true; renderMap().then(renderSitePoints); }
      else if(k.dataset.act==='ca'){ MAP_FILL='ca'; renderMap(); }
      else if(k.dataset.act==='partners'){ const el=$('#partnerChips'); if(el) el.scrollIntoView({behavior:'smooth',block:'center'}); }
      window.scrollTo({top:0,behavior:'smooth'});
    };
    k.addEventListener('click',go);
    k.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); go(); } });
  });
  const cn=$('#kpiCaveat');
  if(cn) cn.textContent = other ? 'Differences versus '+other.id+' reflect which locations were assessed each period — not a change in conditions on the ground.' : '';

  // Key Findings and the Sector Performance chart are analytical results from the
  // full-granularity report — for a headline-totals-only period they are hidden
  // outright, never left on screen carrying another period's numbers.
  $('#findingsCard').hidden=!p.full;
  $('#sectorPerfBlock').hidden=!p.full;
  const fc=$('#findingsChip'); if(fc) fc.textContent=p.id;
  const sc=$('#sectorPerfChip'); if(sc) sc.textContent=p.id;
  if(p.full){
    $('#findingsList').innerHTML=PD().keyFindings.map(f=>`<div class="finding">
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
  const S=PD().sectors;
  const max=Math.max(...S.map(s=>Math.max(s.gap,s.cov)));
  $('#sectorDiverge').innerHTML=S.map(s=>{
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
   CATCHMENTS from the live operational feed — live field data, so it carries its own
   amber banner and is never mixed into the published district layers. */
let MAP_FILL='sev', MAP_HOME=null, MAP_D_LAYER=null, MAP_CA_LAYER=null, MAP_INDEX=[], MAP_FOCUS=[];
let SHOW_SITES=false, SITE_LAYER=null, SITE_RENDERER=null;
const swapRing=r=>r.map(([x,y])=>[y,x]);
const caKey=(pc,ca)=>String(pc||'').toUpperCase()+String(ca||'').toUpperCase();

/* ---- global cross-filter (operational site-level data only) ---- */
// Somali region -> Federal Member State, so a 'State' filter is available even though
// the source data carries region, not state.
const STATE_OF={
  'Banadir':'Banadir',
  'Bay':'South West','Bakool':'South West','Lower Shabelle':'South West','Shabelle Hoose':'South West',
  'Gedo':'Jubaland','Lower Juba':'Jubaland','Middle Juba':'Jubaland','Juba Hoose':'Jubaland','Juba Dhexe':'Jubaland',
  'Hiraan':'Hirshabelle','Middle Shabelle':'Hirshabelle','Shabelle Dhexe':'Hirshabelle',
  'Galgaduud':'Galmudug','Mudug':'Galmudug',
  'Nugaal':'Puntland','Bari':'Puntland','Sool':'Puntland','Sanaag':'Puntland','Karkaar':'Puntland',
  'Awdal':'Somaliland','Woqooyi Galbeed':'Somaliland','Togdheer':'Somaliland'};
const stateOf=r=>STATE_OF[r]||'Other';
let GF={state:'',region:'',district:'',catchment:'',partner:'',sector:'',severity:'',q:''};
const gfActive=()=>['state','region','district','catchment','partner','sector','severity','q'].filter(k=>GF[k]);

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
  const ld=$('#mapLoading'); if(ld) ld.hidden=false;   // shown until first tiles arrive
  const tiles=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    maxZoom:17,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
  }).addTo(map);
  tiles.on('load',()=>{ const l=$('#mapLoading'); if(l) l.hidden=true; });
  // Safety: never leave the overlay stuck if the 'load' event is missed.
  setTimeout(()=>{ const l=$('#mapLoading'); if(l) l.hidden=true; },6000);
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
    applyGlobalFilter();
  };
  const fi=$('#mapFilter');
  if(fi) fi.oninput=()=>applyMapFilter(fi.value);
  const rb=$('#mapReset');
  if(rb) rb.onclick=()=>{ if(fi) fi.value=''; $('#mapFilterMsg').textContent='';
                          if(MAP_HOME) map.fitBounds(MAP_HOME); };
}

/* ---------------- global cross-filter wiring ---------------- */
function wireGlobalFilter(){
  const map={state:'#gfState',region:'#gfRegion',district:'#gfDistrict',catchment:'#gfCatchment',
             partner:'#gfPartner',sector:'#gfSector',severity:'#gfSeverity'};
  Object.entries(map).forEach(([key,sel])=>{
    const el=$(sel);
    if(el) el.onchange=async()=>{
      GF[key]=el.value;
      // cascading: a broader change clears narrower geographic selections
      if(key==='state'){ GF.region=''; GF.district=''; GF.catchment=''; }
      if(key==='region'){ GF.district=''; GF.catchment=''; }
      if(key==='district'){ GF.catchment=''; }
      await ensureOperational();
      if(gfActive().length) SHOW_SITES=true;
      buildGlobalFilterOptions(); applyGlobalFilter(true);
    };
  });
  const ss=$('#gfSite');
  if(ss) ss.oninput=()=>{ GF.q=ss.value; if(GF.q) SHOW_SITES=true; applyGlobalFilter(false); };
  const rs=$('#gfReset');
  if(rs) rs.onclick=()=>{ GF={state:'',region:'',district:'',catchment:'',partner:'',sector:'',severity:'',q:''};
    if(ss) ss.value=''; buildGlobalFilterOptions(); applyGlobalFilter(true);
    if(MAP_HOME&&window.__pubMap) window.__pubMap.fitBounds(MAP_HOME); };
  const tg=$('#gfToggle');
  if(tg && !tg._wired){ tg._wired=true; tg.addEventListener('click',()=>{
    const body=$('#gfBody'), open=!body.hidden;
    body.hidden=open; tg.setAttribute('aria-expanded', open?'false':'true');
    tg.querySelector('.cr').style.transform=open?'':'rotate(90deg)';
  }); }
  const dl=$('#gfDownload');
  if(dl) dl.onclick=downloadFilteredSites;
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
    <div class="meta">${esc(s.d)}, ${esc(s.r)}${s.c&&s.c!=='(catchment not recorded)'?' · '+esc(t('tip.ca'))+' '+esc(catShow(s.c)):''}</div>
    ${esc(t('tip.severity'))}: <span class="badge ${esc(s.b)}">${s.v}%</span> <b>${esc(t('band.'+s.b))}</b><br>
    ${esc(t('tip.partner'))}: ${esc(s.p||'—')}<br>
    ${esc(t('tip.hh'))}: ${fmt(s.hh)} · ${esc(t('tip.ind'))}: ${fmt(s.ind)}
    <div class="secs">${secs}</div></div>`;
}
function gfMatch(s,order){
  if(GF.state && stateOf(s.r)!==GF.state) return false;
  if(GF.region && s.r!==GF.region) return false;
  if(GF.district && s.d!==GF.district) return false;
  if(GF.catchment && s.c!==GF.catchment) return false;
  if(GF.partner && s.p!==GF.partner) return false;
  if(GF.severity && s.b!==GF.severity) return false;
  if(GF.sector){ const i=(order||[]).indexOf(GF.sector); const d=(s.sc||[])[i]; if(d!=='R'&&d!=='K') return false; }
  if(GF.q && !String(s.n).toLowerCase().includes(GF.q.trim().toLowerCase())) return false;
  return true;
}
function gfFiltered(){ const {rows,order}=opSites(); return {list:rows.filter(s=>gfMatch(s,order)), order, all:rows}; }

// Cascading option lists — each select shows only values still reachable given the
// broader selections above it.
function buildGlobalFilterOptions(){
  const {rows}=opSites();
  const opt=(sel,vals,cur,allLabel,disp)=>{
    const el=$(sel); if(!el) return;
    if(cur && !vals.includes(cur)) cur='';
    el.innerHTML=`<option value="">${esc(allLabel)}</option>`
      +vals.map(v=>`<option value="${esc(v)}"${v===cur?' selected':''}>${esc(disp?disp(v):v)}</option>`).join('');
    el.value=cur;
  };
  const inGeo=s=>(!GF.state||stateOf(s.r)===GF.state)&&(!GF.region||s.r===GF.region)&&(!GF.district||s.d===GF.district);
  const uniq=(arr)=>[...new Set(arr.filter(Boolean))].sort();
  opt('#gfState', uniq(rows.map(s=>stateOf(s.r))), GF.state=GF.state, t('gf.allstates'));
  opt('#gfRegion', uniq(rows.filter(s=>!GF.state||stateOf(s.r)===GF.state).map(s=>s.r)), GF.region, t('gf.allregions'));
  opt('#gfDistrict', uniq(rows.filter(s=>(!GF.state||stateOf(s.r)===GF.state)&&(!GF.region||s.r===GF.region)).map(s=>s.d)), GF.district, t('gf.alldistricts'));
  opt('#gfCatchment', uniq(rows.filter(inGeo).map(s=>s.c)).filter(c=>c!=='(catchment not recorded)'), GF.catchment, t('gf.allcatchments'), catShow);
  opt('#gfPartner', uniq(rows.filter(inGeo).map(s=>s.p)), GF.partner, t('gf.allpartners'));
  // sector + severity are fixed lists
  const se=$('#gfSector');
  if(se) se.innerHTML=`<option value="">${esc(t('gf.allsectors'))}</option>`
    +(DATA.sectors||[]).map(x=>`<option value="${esc(x.code)}"${x.code===GF.sector?' selected':''}>${esc(x.name)}</option>`).join('');
  const sv=$('#gfSeverity');
  if(sv) sv.innerHTML=`<option value="">${esc(t('gf.allseverity'))}</option>`
    +['Severe','High','Moderate','Low'].map(b=>`<option value="${b}"${b===GF.severity?' selected':''}>${esc(t('band.'+b))}</option>`).join('');
}

const GF_LABELS={state:'gf.state',region:'gf.region',district:'gf.district',catchment:'gf.catchment',
  partner:'gf.partner',sector:'gf.sector',severity:'gf.severity',q:'gf.search'};
function gfChipText(k){
  if(k==='sector'){ const x=(DATA.sectors||[]).find(s=>s.code===GF.sector); return x?x.name:GF.sector; }
  if(k==='severity') return t('band.'+GF.severity);
  if(k==='catchment') return catShow(GF.catchment);
  return GF[k];
}
function renderGfChips(){
  const keys=gfActive();
  $('#gfActiveCount').textContent=keys.length?`(${keys.length})`:'';
  $('#gfChips').innerHTML=keys.map(k=>
    `<span class="gf-chip">${esc(gfChipText(k))}<button data-k="${k}" aria-label="Remove">×</button></span>`).join('');
  $$('#gfChips .gf-chip button').forEach(b=>b.onclick=()=>{
    GF[b.dataset.k]=''; if(b.dataset.k==='q'){ const el=$('#gfSite'); if(el) el.value=''; }
    buildGlobalFilterOptions(); applyGlobalFilter(true);
  });
}

let GF_LAST=[];
function applyGlobalFilter(refit){
  const st=$('#sitesToggle'); if(st) st.classList.toggle('active',SHOW_SITES);
  renderGfChips();
  const {list,order,all}=gfFiltered();
  GF_LAST=list;
  // live KPI strip
  const cats=new Set(), parts=new Set(); let hh=0, ind=0, sev=0;
  list.forEach(s=>{ if(s.c && s.c!=='(catchment not recorded)') cats.add(s.c);
    if(s.p) parts.add(s.p); hh+=s.hh||0; ind+=s.ind||0; sev+=s.v; });
  const avg=list.length?Math.round(sev/list.length*10)/10:0;
  const kpi=(v,l)=>`<div class="kpi"><div class="k-val">${v}</div><div class="k-lab">${esc(l)}</div></div>`;
  // The catchment count is deliberately NOT shown here: on a historical period the live
  // field data covers fewer catchments than the published total, and an operational
  // count beside the published figure invites a false comparison. The catchment total
  // lives in the catchment-analysis table and the map banner, clearly labelled operational.
  $('#gfKpis').innerHTML=kpi(fmt(list.length),t('dk.sites'))
    +kpi(fmt(parts.size),t('kpi.partners'))+kpi(fmt(hh),t('dk.hh'))
    +kpi(list.length?`<span class="badge ${sevBand(avg)}">${avg}%</span>`:'—',t('dk.sev'));
  // map points (only when the layer is on)
  drawSitePoints(list,order,refit);
  // filtered site table
  renderGfTable(list);
}
function drawSitePoints(list,order,refit){
  const st=$('#sitesToggle'); if(st) st.classList.toggle('active',SHOW_SITES);
  if(!SITE_LAYER) return;
  SITE_LAYER.clearLayers();
  if(!SHOW_SITES) return;
  if(!SITE_RENDERER) SITE_RENDERER=L.canvas({padding:.3});
  const pts=[];
  list.forEach(s=>{
    if(s.la==null||s.lo==null) return;
    const m=L.circleMarker([s.la,s.lo],{renderer:SITE_RENDERER,radius:5,weight:1,
      color:'#fff',fillColor:bandColor(s.b),fillOpacity:.85});
    m.bindTooltip(siteTip(s,order),{sticky:true,opacity:1});
    m.addTo(SITE_LAYER); pts.push([s.la,s.lo]);
  });
  if(refit && gfActive().length && pts.length){
    let frame=pts;
    if(pts.length>20){
      const lats=pts.map(p=>p[0]).sort((a,b)=>a-b), lons=pts.map(p=>p[1]).sort((a,b)=>a-b);
      const lo=Math.floor(pts.length*.05), hi=Math.ceil(pts.length*.95)-1;
      frame=pts.filter(p=>p[0]>=lats[lo]&&p[0]<=lats[hi]&&p[1]>=lons[lo]&&p[1]<=lons[hi]);
      if(!frame.length) frame=pts;
    }
    const b=L.latLngBounds(frame);
    if(b.isValid()&&window.__pubMap) window.__pubMap.fitBounds(b.pad(0.2),{maxZoom:13});
  }
}
// back-compat shim: callers that used to call renderSitePoints now route through the filter
function renderSitePoints(){ applyGlobalFilter(false); }

function renderGfTable(list){
  const card=$('#gfTableCard'); if(!card) return;
  card.hidden = !(SHOW_SITES || gfActive().length);
  const {label}=opCatchments();
  const per=$('#gfTablePeriod'); if(per) per.textContent=label||'';
  const cap=300;
  $('#gfTableNote').textContent=t('gf.matchnote').replace('{n}',fmt(list.length));
  const rows=[...list].sort((a,b)=>b.v-a.v).slice(0,cap);
  $('#gfTable').innerHTML=rows.length?rows.map(s=>`<tr>
    <td style="font-weight:600">${esc(s.n)}</td><td>${esc(s.d)}</td><td>${esc(s.r)}</td>
    <td>${esc(catShow(s.c))}</td><td>${esc(s.p||'—')}</td>
    <td class="ctr"><span class="badge ${esc(s.b)}">${s.v}%</span></td></tr>`).join('')
    : `<tr><td colspan="6"><p class="empty-note">${esc(t('gf.nomatch'))}</p></td></tr>`;
  $('#gfTableMore').textContent = list.length>cap ? t('gf.capped').replace('{cap}',fmt(cap)).replace('{n}',fmt(list.length)) : '';
}
function downloadFilteredSites(){
  const {label}=opCatchments();
  const head=[['CCCM Cluster Somalia — Site Monitoring: filtered operational sites'],
    ['Status','OPERATIONAL — LIVE FIELD DATA (not IM-reviewed, not comparable with published figures)'],
    ['Reporting period', label||''],['Generated', DATA.generated],
    ['Filters', gfActive().map(k=>k+'='+gfChipText(k)).join('; ')||'(none)'],[],
    ['Site','District','Region','Catchment','Partner','Severity %','Severity band','Households','Individuals']];
  const body=GF_LAST.map(s=>[s.n,s.d,s.r,s.c||'',s.p||'',s.v,s.b,s.hh||'',s.ind||'']);
  csvDownload('cccm_operational_filtered_sites.csv', head.concat(body));
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
    ? 'Catchment severity from the live operational feed. Catchments with a published boundary are shaded as areas; the rest are shown as points at the centre of their assessed sites.'
    : 'District severity from published results. Grey districts were not individually reported.';

  if(caMode){
    await ensureOperational();
    const {rows,label}=opCatchments();
    const byKey={}; rows.forEach(r=>{ byKey[String(r.catchment).toUpperCase()]=r; });
    const chip=$('#caPeriodChip'); if(chip) chip.textContent=label||'—';
    const caTip=rec=>`<b>${esc(catShow(rec.catchment))} — ${esc(rec.district)}</b><br>${fmt(rec.n)} sites · Avg. severity ${rec.avgSeverity}%`
      +`<br>Severe ${rec.Severe} · High ${rec.High} · Moderate ${rec.Moderate} · Low ${rec.Low}`
      +'<br><i>Operational — live field data</i>';
    // 1) shade every catchment that has a published boundary polygon
    const shaded=new Set();
    let asPoly=0;
    (geo.catchments||[]).forEach(gc=>{
      const rec=byKey[caKey(gc.pc,gc.ca)];
      const poly=L.polygon(gc.rings.map(swapRing),{
        color:'#fff',weight:.8,
        fillColor:rec?bandColor(sevBand(rec.avgSeverity)):'#E2E5E0',
        fillOpacity:rec?.65:.22});
      poly.bindTooltip(rec?caTip(rec)
        :`<b>${esc(gc.ca)} — ${esc(gc.d)}</b><br>Not assessed in this period`,{sticky:true});
      poly.addTo(MAP_CA_LAYER);
      if(rec){ shaded.add(String(rec.catchment).toUpperCase()); asPoly++; MAP_FOCUS.push(poly.getBounds()); }
      MAP_INDEX.push({hay:`${gc.ca} ${gc.d}`.toLowerCase(),bounds:poly.getBounds()});
    });
    // 2) every remaining assessed catchment gets a centroid circle from its site GPS
    if(!SITE_RENDERER) SITE_RENDERER=L.canvas({padding:.3});
    let asPoint=0, noShape=0;
    rows.forEach(rec=>{
      if(shaded.has(String(rec.catchment).toUpperCase())) return;
      if(rec.la==null||rec.lo==null){ noShape++; return; }
      const r=Math.min(16,6+Math.sqrt(rec.n)*1.4);
      const m=L.circleMarker([rec.la,rec.lo],{renderer:SITE_RENDERER,radius:r,weight:1.5,
        color:'#fff',fillColor:bandColor(sevBand(rec.avgSeverity)),fillOpacity:.85});
      m.bindTooltip(caTip(rec),{sticky:true});
      m.addTo(MAP_CA_LAYER); asPoint++;
      MAP_FOCUS.push(L.latLngBounds([[rec.la,rec.lo],[rec.la,rec.lo]]));
      MAP_INDEX.push({hay:`${rec.catchment} ${rec.district}`.toLowerCase(),bounds:m.getBounds?m.getBounds():L.latLngBounds([[rec.la,rec.lo],[rec.la,rec.lo]])});
    });
    $('#caBanner').innerHTML='<b>Operational — live field data</b> — from the field data pipeline, not '
      +'Information-Management reviewed and not comparable with the published figures. '
      +`All ${rows.length} assessed catchments are on the map: ${asPoly} shaded as boundary areas, `
      +`${asPoint} shown as points (centre of their sites)`
      +(noShape?`; ${noShape} without GPS appear in the table only.`:'.');
    renderCatchmentPanel(rows,geo,label);
  }else if(!blocked){
    const byPc={}; PD().districts.forEach(d=>{ if(d.pc) byPc[d.pc]=d; });
    const fillFor=pc=>{
      const d=byPc[(alias[pc]||pc||'').toUpperCase()];
      if(!d || (MAP_FILL==='cov'?d.cov:d.gap)==null) return '#E2E5E0';
      return MAP_FILL==='cov' ? (d.cov>=60?'#104E5D':d.cov>=45?'#17677A':d.cov>=25?'#6FAEBD':'#C9E0E6')
                              : bandColor(sevBand(d.gap));
    };
    geo.districts.forEach(gd=>{
      const d=byPc[(alias[gd.pc]||gd.pc||'').toUpperCase()];
      const poly=L.polygon(gd.rings.map(swapRing),
        {color:'#fff',weight:.8,fillColor:fillFor(gd.pc),fillOpacity:.6});
      const gv=d&&d.gap!=null?`Gap ${d.gap}%`:'', cvv=d&&d.cov!=null?`Coverage ${d.cov}%`:'';
      poly.bindTooltip(d
        ? `<b>${esc(gd.n)}</b><br>${[gv,cvv].filter(Boolean).join(' / ')||'Ranked this period'}<br><i>Click for full profile</i>`
        : `<b>${esc(gd.n)}</b><br>Not individually reported this period<br><i>Click for operational detail</i>`,{sticky:true});
      // Clicking a district opens its profile drawer; strong border marks the selection.
      poly.on('mouseover',()=>poly.setStyle({weight:2.4,color:'#104E5D'}));
      poly.on('mouseout',()=>poly.setStyle({weight:.8,color:'#fff'}));
      poly.on('click',async()=>{ await ensureOperational(); openDistrictDrawer(gd.n, d, null); });
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
  await ensureOperational();
  buildGlobalFilterOptions();
  applyGlobalFilter(false);
  renderMapLegend();
  setTimeout(()=>map.invalidateSize(),60);
}

function renderCatchmentPanel(rows,geo,label){
  const hasGeo=k=>(geo.catchments||[]).some(gc=>caKey(gc.pc,gc.ca)===String(k).toUpperCase());
  const onMap=c=>hasGeo(c.catchment)?'Area':(c.la!=null?'Point':'<span class="dash">—</span>');
  const sorted=[...rows].sort((a,b)=>b.avgSeverity-a.avgSeverity);
  $('#caPanelNote').textContent=`${sorted.length} catchments assessed in ${label||'this period'}, `
    +'ranked by average severity. Severity is the share of applicable indicators scoring Red '
    +'across the sites in that catchment.';
  $('#caTable').innerHTML=sorted.length?sorted.map(c=>`<tr>
      <td style="font-weight:600">${esc(catShow(c.catchment))}</td><td>${esc(c.district)}</td><td>${esc(c.region)}</td>
      <td class="ctr">${fmt(c.n)}</td>
      <td class="ctr"><span class="badge ${sevBand(c.avgSeverity)}">${c.avgSeverity}%</span></td>
      <td class="ctr">${fmt(c.Severe)}</td><td class="ctr">${fmt(c.High)}</td>
      <td class="ctr">${fmt(c.Moderate)}</td><td class="ctr">${fmt(c.Low)}</td>
      <td class="ctr" style="font-size:11px">${onMap(c)}</td>
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
  const S=PD().sectors;
  SD_CUR=(SD_CUR&&S.some(x=>x.code===SD_CUR))?SD_CUR:S[0].code;
  $('#sdTabs').innerHTML=S.map(s=>{
    const icon=DATA.assets.icons[s.code]?`<img src="${DATA.assets.icons[s.code]}" alt="">`:'';
    return `<button class="sd-tab ${s.code===SD_CUR?'active':''}" data-c="${s.code}">${icon}${esc(s.name)}</button>`;
  }).join('');
  $$('#sdTabs .sd-tab').forEach(b=>b.addEventListener('click',()=>{SD_CUR=b.dataset.c;renderSectorTabs();renderSectorBody();}));
  renderSectorBody();
}
function renderSectorBody(){
  const s=PD().sectors.find(x=>x.code===SD_CUR);
  $('#sdTitle').innerHTML=`${esc(s.name)} <span class="hint">Gap ${s.gap}% · Coverage ${s.cov}%</span>`;
  const rows=PD().topRed.map(r=>({...r,kind:'red'})).concat(PD().topGreen.map(r=>({...r,kind:'green'})))
    .filter(r=>r.sector===SD_CUR);
  if(!rows.length){
    $('#sdBody').innerHTML='<p class="empty-note">No indicator-level detail published for this sector this quarter. '
      +'Sector-wide gap and coverage percentages are shown above.</p>';
    return;
  }
  $('#sdBody').innerHTML=rows.map(r=>`<div class="tri-row">
    <div class="l" title="${esc(r.indicator)}">${esc(r.indicator)}${r.lc?' <span style="color:var(--muted);font-size:10px">(LC)</span>':''}</div>
    <div class="tri-bar"><div class="tri-seg ${r.kind==='red'?'r':'g'}" style="width:${r.pct}%"></div></div>
    <div class="ctr" style="font-weight:700">${r.pct}%</div></div>`).join('')
    +(rows.some(r=>r.lc)&&PD().lcNote?`<p style="margin:10px 0 0;font-size:11px;color:var(--muted)">${esc(PD().lcNote)}</p>`:'');
}
function renderTopGaps(){
  if(!period().full) return;   // renderSectorTabs already wrote the unavailable note
  const rows=[...PD().topRed].sort((a,b)=>b.pct-a.pct);
  $('#topGapsList').innerHTML=rows.map(r=>`<div class="hbar-row">
    <div class="l" title="${esc(r.indicator)}">${esc(r.indicator)}</div>
    <div class="hbar-track"><div class="hbar-fill" style="width:${r.pct}%;background:var(--gap)"></div></div>
    <div class="v" style="color:var(--gap)">${r.pct}%</div></div>`).join('');
}

/* ================= DISTRICT ANALYSIS ================= */
let DSORT={k:'gap',dir:-1};   // default: highest gap first
function sortDistricts(rows){
  const num=k=>(k==='n'||k==='gap'||k==='cov');
  return [...rows].sort((a,b)=>{
    let av=a[DSORT.k], bv=b[DSORT.k];
    if(num(DSORT.k)){
      // nulls (values the report didn't publish for this district) always sort last.
      if(av==null && bv==null) return 0;
      if(av==null) return 1;
      if(bv==null) return -1;
      return (av-bv)*DSORT.dir;
    }
    return String(av).localeCompare(String(bv))*DSORT.dir;
  });
}
function paintSortArrows(){
  $$('#distHead th.sortable').forEach(th=>{
    const a=th.querySelector('.sarrow');
    a.textContent = th.dataset.k===DSORT.k ? (DSORT.dir<0?'▼':'▲') : '';
  });
}
const DIST_ROWS=()=>[...PD().districts];
function paintDistrictRows(rows){
  const dash='<span class="dash">—</span>';
  $('#distTable').innerHTML=rows.length?rows.map(d=>{
    const gapCell = d.gap==null ? dash : `<span class="badge ${sevBand(d.gap)}">${d.gap}%</span>`;
    const covCell = d.cov==null ? dash : `${d.cov}%`;
    return `<tr class="rowlink" data-dist="${esc(d.district)}">
      <td style="font-weight:600">${esc(d.district)}</td><td>${esc(d.region)}</td>
      <td class="ctr">${fmt(d.n)}</td>
      <td class="ctr">${gapCell}</td>
      <td class="ctr">${covCell}</td>
      <td class="ctr chev">›</td>
    </tr>`;
  }).join('') : `<tr><td colspan="6"><p class="empty-note">No districts match this filter.</p></td></tr>`;
  $$('#distTable tr.rowlink').forEach(tr=>{
    tr.tabIndex=0;
    const go=async()=>{ const name=tr.dataset.dist, pub=PD().districts.find(x=>x.district===name);
      await ensureOperational(); openDistrictDrawer(name, pub, tr); };
    tr.addEventListener('click',go);
    tr.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); go(); } });
  });
}
function renderDistricts(){
  // Partner names are published for Q2; the Q1 report gives only a count (9), not names.
  const pk=period().kpi.partners;
  $('#partnerChips').innerHTML = period().id==='Q2 2026'
    ? DATA.partners.map(p=>`<span class="pub-chip-sm" style="padding:5px 11px;font-size:12px">${esc(p)}</span>`).join('')
    : `<span style="font-size:12.5px;color:var(--ink-2)">${fmt(pk)} reporting partners assessed sites this period; individual partner names were not published in the ${esc(period().id)} report.</span>`;
  renderOperational().catch(e=>console.error('[public dashboard] "operational" failed:', e));
  if(periodBlocked('#distPeriodNote')){
    $('#distTable').innerHTML='<tr><td colspan="6"><p class="empty-note">District rankings are not '
      +'published for this reporting period. Open any district on the map for its live operational profile.</p></td></tr>';
    $('#distFootnote').textContent='';
    $('#distFilterCount').textContent='';
    const fi=$('#distFilter'); if(fi){ fi.value=''; fi.disabled=true; }
    return;
  }
  const fi=$('#distFilter'); if(fi) fi.disabled=false;
  const all=DIST_ROWS();
  const total=all.length;
  const input=$('#distFilter');
  const draw=()=>{
    const q=input.value.trim().toLowerCase();
    const rows=sortDistricts(q?all.filter(d=>d.district.toLowerCase().includes(q)||d.region.toLowerCase().includes(q)):all);
    paintDistrictRows(rows);
    $('#distFilterCount').textContent=q?`${rows.length} of ${total} districts`:'';
    paintSortArrows();
  };
  input.value=''; input.oninput=draw;
  $$('#distHead th.sortable').forEach(th=>{
    th.onclick=()=>{ const k=th.dataset.k;
      if(DSORT.k===k) DSORT.dir*=-1; else DSORT={k, dir:(k==='n'||k==='gap'||k==='cov')?-1:1};
      draw();
    };
  });
  draw();
  $('#distFootnote').innerHTML=PD().districtFootnote;
}

/* ================= DISTRICT PROFILE DRAWER ================= */
const SECNAME=Object.fromEntries((DATA.sectors||[]).map(s=>[s.code,s.name]));
function districtProfile(name){
  // Rich profile is computed from the live operational site records — the only dataset
  // granular enough for per-district sector/severity/partner detail. Clearly badged
  // operational; the published summary (gap/coverage) is shown alongside when it exists.
  const {rows,order}=opSites();
  const sites=rows.filter(s=>s.d===name);
  if(!sites.length) return {name,order,sites:[],period:opSites().label};
  const bands={Severe:0,High:0,Moderate:0,Low:0};
  let hh=0, ind=0, sevSum=0; const cas=new Set(), partners=new Set();
  sites.forEach(s=>{ bands[s.b]=(bands[s.b]||0)+1; hh+=s.hh||0; ind+=s.ind||0; sevSum+=s.v;
    if(s.c) cas.add(s.c); if(s.p) partners.add(s.p); });
  // per-sector gap = Red share of applicable (non-NA) site dots
  const gaps=order.map((code,i)=>{
    let appl=0, red=0;
    sites.forEach(s=>{ const d=(s.sc||[])[i]; if(!d||d==='NA') return; appl++; if(d==='R'||d==='K') red++; });
    return {code, name:SECNAME[code]||code, pct:appl?Math.round(red/appl*100):null, appl};
  }).filter(g=>g.pct!=null).sort((a,b)=>b.pct-a.pct);
  return {name, order, sites, cas:cas.size, hh, ind, partners:[...partners].sort(),
          avg:Math.round(sevSum/sites.length*10)/10, bands, gaps};
}
function q1q2ForDistrict(name){
  const out={};
  if(OP_DATA&&OP_DATA.quarters) Object.entries(OP_DATA.quarters).forEach(([k,q])=>{
    out[k]=(q.sites||[]).filter(s=>s.d===name).length;
  });
  return out;
}
// Builds the operational (live field data) detail block — revealed only on demand so it
// never sits mixed with the published figures by default.
function operationalDetailHTML(pr, name){
  const total=pr.sites.length;
  if(!total) return `<p class="empty-note" style="text-align:left;margin:0">${esc(t('d.nolive'))}</p>`;
  let html=`<div class="dk-grid" style="margin-bottom:12px">
    <div class="dk"><div class="v">${fmt(total)}</div><div class="l">${esc(t('dk.sites'))}</div></div>
    <div class="dk"><div class="v">${fmt(pr.cas)}</div><div class="l">${esc(t('dk.cas'))}</div></div>
    <div class="dk"><div class="v">${fmt(pr.hh)}</div><div class="l">${esc(t('dk.hh'))}</div></div>
    <div class="dk"><div class="v">${fmt(pr.ind)}</div><div class="l">${esc(t('dk.ind'))}</div></div>
    <div class="dk dk-full"><div class="v"><span class="badge ${sevBand(pr.avg)}">${pr.avg}%</span></div><div class="l">${esc(t('dk.sev'))}</div></div>
  </div>`;
  const segs=['Severe','High','Moderate','Low'].map(b=>{
    const n=pr.bands[b]||0; if(!n) return '';
    return `<span style="background:${bandColor(b)};flex:${n}" title="${esc(t('band.'+b))}: ${n}">${n}</span>`;
  }).join('');
  html+=`<h4>${esc(t('dh.sevdist'))}</h4><div class="sevbar">${segs}</div>`;
  html+=`<h4>${esc(t('dh.topgaps'))}</h4>`;
  pr.gaps.slice(0,5).forEach(g=>{
    html+=`<div class="gaprow"><div>${esc(g.name)}<div class="gt"><div class="gf" style="width:${g.pct}%"></div></div></div>
      <div class="gv">${g.pct}%</div></div>`;
  });
  const qq=q1q2ForDistrict(name), qk=Object.keys(qq);
  if(qk.length>1){
    html+=`<h4>${esc(t('dh.q1q2'))}</h4><div class="q1q2mini">`
      +qk.map(k=>`<div>${esc(k)}</div><div class="h"></div><div style="font-weight:700;text-align:right">${fmt(qq[k])}</div>`).join('')
      +`</div><p style="font-size:11px;color:var(--muted);margin:6px 0 0">Assessment coverage, not a change in conditions.</p>`;
  }
  html+=`<h4>${esc(t('dh.partners'))}</h4><div class="chips">`
    +pr.partners.map(p=>`<span class="pub-chip-sm" style="padding:4px 9px">${esc(p)}</span>`).join('')+`</div>`;
  html+=`<button class="btn sm" id="drawerGeo" style="margin-top:14px">${esc(t('d.opengeo'))}</button>`;
  return html;
}
function openDistrictDrawer(name, pub, trigger){
  DRAWER_TRIGGER=trigger||document.activeElement;
  const pr=districtProfile(name);
  $('#drawerTitle').textContent=name;
  $('#drawerSub').textContent=(pr.sites[0]?pr.sites[0].r:'')+(pub?' · '+t('d.published'):'');
  // ---- Published-only by default ----
  let html='';
  if(pub){
    html+=`<div style="margin-bottom:8px"><span class="op-badge" style="background:var(--teal-l);color:var(--teal-d);border-color:var(--teal)">${esc(t('d.published'))} · ${esc(period().id)}</span></div>`
      +`<div class="dk-grid"><div class="dk"><div class="v">${pub.gap}%</div><div class="l">${esc(t('dk.gap'))}</div></div>`
      +`<div class="dk"><div class="v">${pub.cov}%</div><div class="l">${esc(t('dk.cov'))}</div></div></div>`
      +`<p style="font-size:11.5px;color:var(--muted);margin:0">${esc(t('d.pubnote'))}</p>`;
  }else{
    html+=`<p class="empty-note" style="text-align:left">${esc(t('d.notpublished'))}</p>`;
  }
  // ---- Operational detail, behind an explicit opt-in button ----
  html+=`<div class="op-reveal" style="margin-top:16px">
      <button class="collapse-btn" id="opDetailToggle" aria-expanded="false" aria-controls="opDetailBody">
        <span><span class="cr">▸</span> ${esc(t('d.viewop'))}</span><span class="op-badge">OPERATIONAL</span></button>
      <div id="opDetailBody" hidden style="margin-top:12px">
        <div id="opDetailInner"></div>
      </div></div>`;
  $('#drawerBody').innerHTML=html;
  const tg=$('#opDetailToggle');
  if(tg) tg.onclick=()=>{
    const body=$('#opDetailBody'), open=body.hidden;
    if(open && !body.dataset.built){ $('#opDetailInner').innerHTML=operationalDetailHTML(pr,name); body.dataset.built='1'; wireDrawerGeo(name); }
    body.hidden=!open; tg.setAttribute('aria-expanded', open?'true':'false');
  };
  openDrawer();
}
function wireDrawerGeo(name){
  const gb=$('#drawerGeo');
  if(gb) gb.onclick=()=>{ closeDrawer();
    activateView('map');
    SHOW_SITES=true;
    GF={state:'',region:'',district:name,catchment:'',partner:'',sector:'',severity:'',q:''};
    renderMap().then(()=>{ buildGlobalFilterOptions(); applyGlobalFilter(true); });
  };
}
let DRAWER_TRIGGER=null;
function openDrawer(){
  const bk=$('#drawerBack'), d=$('#drawer');
  bk.classList.add('open'); bk.setAttribute('aria-hidden','false');
  d.classList.add('open'); d.setAttribute('aria-hidden','false'); d.removeAttribute('inert');
  const x=$('#drawerX'); if(x) x.focus();
}
function closeDrawer(){
  const bk=$('#drawerBack'), d=$('#drawer');
  if(!d.classList.contains('open')) return;
  bk.classList.remove('open'); bk.setAttribute('aria-hidden','true');
  d.classList.remove('open'); d.setAttribute('aria-hidden','true'); d.setAttribute('inert','');
  // restore focus to the row/element that opened the drawer
  if(DRAWER_TRIGGER && DRAWER_TRIGGER.focus){ try{ DRAWER_TRIGGER.focus(); }catch(e){} }
  DRAWER_TRIGGER=null;
}
function wireDrawer(){
  const x=$('#drawerX'), bk=$('#drawerBack'), d=$('#drawer');
  if(d) d.setAttribute('inert','');   // start inert (closed)
  if(x) x.onclick=closeDrawer;
  if(bk) bk.onclick=closeDrawer;
  document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeDrawer(); });
}

/* ================= OPERATIONAL SNAPSHOT (live field data) ================= */
let OP_Q=null, OP_DATA=null, OP_LIVE=false;
function paintOpRows(rows){
  $('#opTable').innerHTML=rows.length?rows.map(c=>`<tr>
      <td style="font-weight:600">${esc(catShow(c.catchment))}</td><td>${esc(c.district)}</td><td>${esc(c.region)}</td>
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
  // Provisional data stays collapsed under an opt-in button; it never renders directly
  // beneath the published results by default (donor/OCHA confusion risk).
  $('#opCollapse').hidden=false;
  const src=$('#opSourceNote');
  if(src) src.textContent=OP_LIVE
    ? 'Live — queried directly from Kobo/Zite'+(op.generatedAt?` as of ${esc(op.generatedAt)}`:'')+'.'
    : 'Live endpoint unreachable right now — showing the last snapshot generated at deploy time, not a real-time read.';
  if(Object.keys(op.quarters).includes(CUR_PERIOD)) OP_Q=CUR_PERIOD;
  paintOperational(op);
  const tg=$('#opToggle');
  if(tg && !tg._wired){
    tg._wired=true;
    tg.addEventListener('click',()=>{
      const open=$('#opSection').hidden;
      $('#opSection').hidden=!open;
      tg.setAttribute('aria-expanded', open?'true':'false');
    });
  }
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
    ['Data source', p.source||DATA.source],['Generated', DATA.generated],
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
        ...PD().districts.map(d=>[d.district,d.region,d.n==null?'':d.n,d.gap==null?'':d.gap,d.cov==null?'':d.cov,
          d.bands?d.bands.Severe:'',d.bands?d.bands.High:'',d.bands?d.bands.Moderate:'',d.bands?d.bands.Low:''])])],
      ['Sector-gap table',()=>csvDownload(slug+'_sector_gaps.csv',[...metaHeader('Sector gaps'),
        ['Sector','Gap %','Coverage %'],...PD().sectors.map(s=>[s.name,s.gap,s.cov])])]);
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
    <p><b>Source:</b> ${esc(period().source||DATA.source)}</p>
    <p><b>Data sources:</b> CCCM partner site-monitoring submissions, reported quarterly.</p>
    <p><b>Periods available:</b> ${PERIODS.map(p=>esc(p.id)).join(' · ')} — each shown from its own published national report. `
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
 ['language',wireLang],['drawer',wireDrawer],['global filter',wireGlobalFilter]
].forEach(([label,fn])=>{ try{ fn(); } catch(e){ console.error('[public dashboard] "'+label+'" failed:', e); } });
renderAll();
