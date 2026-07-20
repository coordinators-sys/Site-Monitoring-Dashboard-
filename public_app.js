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

/* ================= TAB NAV ================= */
$$('.tab').forEach(b=>b.addEventListener('click',()=>{
  $$('.tab').forEach(x=>x.classList.remove('active'));b.classList.add('active');
  $$('.view').forEach(v=>v.classList.remove('active'));
  $('#view-'+b.dataset.view).classList.add('active');
  if(b.dataset.view==='map'){renderMap();if(window.__pubMap)setTimeout(()=>window.__pubMap.invalidateSize(),60);}
  window.scrollTo({top:0,behavior:'smooth'});
}));

/* ================= OVERVIEW ================= */
function renderOverview(){
  const K=DATA.kpi;
  $('#ovIntro').textContent=DATA.intro;
  const cards=[
    {v:fmt(K.sites),l:'Sites assessed'},
    {v:fmt(K.catchments),l:'Catchment areas assessed'},
    {v:fmt(K.districts),l:'Districts assessed'},
    {v:fmt(K.partners),l:'Reporting partners'},
    {v:fmt(K.hhs),l:'Households'},
    {v:fmt(K.individuals),l:'Individuals'},
  ];
  $('#kpiRow').innerHTML=cards.map(c=>`<div class="kpi">
    <div class="k-val">${c.v}</div><div class="k-lab">${esc(c.l)}</div></div>`).join('');

  $('#findingsList').innerHTML=DATA.keyFindings.map(f=>`<div class="finding">
    <div class="flab">${esc(f[0])}</div>
    <div class="fval">${esc(f[1])}</div>
    <div class="fsub">${esc(f[2])}</div></div>`).join('');

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
  renderSectorDiverge();
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
let MAP_FILL='sev';
function renderMap(){
  const geo=DATA.geo;
  if(window.__pubMap||!geo||typeof L==='undefined') { if(window.__pubMap) return; }
  if(!geo||typeof L==='undefined'){
    $('#pubMap').innerHTML='<p class="empty-note">Map not available in this build.</p>'; return;
  }
  const alias=geo.pcodeAlias||{};
  const byPc={}; DATA.districts.forEach(d=>{ if(d.pc) byPc[d.pc]=d; });
  const fillFor=pc=>{
    const rp=(alias[pc]||pc||'').toUpperCase();
    const d=byPc[rp];
    if(!d) return '#E2E5E0';
    return MAP_FILL==='cov' ? (d.cov>=60?'#104E5D':d.cov>=45?'#17677A':d.cov>=25?'#6FAEBD':'#C9E0E6')
                            : bandColor(sevBand(d.gap));
  };
  const map=L.map('pubMap',{zoomSnap:.5});
  window.__pubMap=map;
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    maxZoom:17,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
  }).addTo(map);
  const swap=r=>r.map(([x,y])=>[y,x]);
  const polys=[];
  geo.districts.forEach(gd=>{
    const rp=(alias[gd.pc]||gd.pc||'').toUpperCase();
    const d=byPc[rp];
    const poly=L.polygon(gd.rings.map(swap),{color:'#fff',weight:.8,fillColor:fillFor(gd.pc),fillOpacity:.6});
    poly._pc=gd.pc;
    poly.bindTooltip(d
      ? `<b>${esc(gd.n)}</b><br>${fmt(d.n)} sites assessed · Gap ${d.gap}% / Coverage ${d.cov}%`
      : `<b>${esc(gd.n)}</b><br>Not individually reported this quarter`, {sticky:true});
    poly.addTo(map); polys.push(poly);
  });
  map.fitBounds(L.featureGroup(polys).getBounds());
  $$('.map-layer').forEach(b=>{
    b.classList.toggle('active',b.dataset.layer===MAP_FILL);
    b.onclick=()=>{ MAP_FILL=b.dataset.layer;
      polys.forEach(p=>p.setStyle({fillColor:fillFor(p._pc)}));
      $$('.map-layer').forEach(x=>x.classList.toggle('active',x.dataset.layer===MAP_FILL));
      renderMapLegend(); };
  });
  renderMapLegend();
}
function renderMapLegend(){
  const it=(c,l)=>`<span class="it"><span class="dot" style="background:${c}"></span>${l}</span>`;
  $('#mapLegend').innerHTML = MAP_FILL==='sev'
    ? it('#D9534F','Severe ≥55%')+it('#EC6B4D','High 40–55%')+it('#E9A23B','Moderate 25–40%')+it('#3A8D68','Low <25%')+it('#E2E5E0','Not reported')
    : it('#104E5D','60%+ coverage')+it('#17677A','45–59%')+it('#6FAEBD','25–44%')+it('#C9E0E6','<25%')+it('#E2E5E0','Not reported');
}

/* ================= SECTOR GAPS ================= */
let SD_CUR=null;
function renderSectorTabs(){
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
  $('#partnerChips').innerHTML=DATA.partners.map(p=>
    `<span class="pub-chip-sm" style="padding:5px 11px;font-size:12px">${esc(p)}</span>`).join('');
  renderOperational();
}

/* ================= OPERATIONAL SNAPSHOT (unreconciled) ================= */
let OP_Q=null;
function paintOpRows(rows){
  $('#opTable').innerHTML=rows.length?rows.map(c=>`<tr>
      <td style="font-weight:600">${esc(c.catchment)}</td><td>${esc(c.district)}</td><td>${esc(c.region)}</td>
      <td class="ctr">${fmt(c.n)}</td>
      <td class="ctr"><span class="badge ${sevBand(c.avgSeverity)}">${c.avgSeverity}%</span></td>
      <td class="ctr">${fmt(c.Severe)}</td><td class="ctr">${fmt(c.High)}</td>
      <td class="ctr">${fmt(c.Moderate)}</td><td class="ctr">${fmt(c.Low)}</td>
    </tr>`).join('') : `<tr><td colspan="9"><p class="empty-note">No catchments match this filter.</p></td></tr>`;
}
function renderOperational(){
  const op=DATA.operational;
  if(!op||!op.available||!Object.keys(op.quarters).length){ return; }
  $('#opSection').hidden=false;
  const qkeys=Object.keys(op.quarters);
  OP_Q=OP_Q&&qkeys.includes(OP_Q)?OP_Q:qkeys[qkeys.length-1];
  $('#opQuarterTabs').innerHTML=qkeys.map(k=>
    `<button class="op-tab ${k===OP_Q?'active':''}" data-q="${esc(k)}">${esc(k)}</button>`).join('');
  $$('#opQuarterTabs .op-tab').forEach(b=>b.addEventListener('click',()=>{OP_Q=b.dataset.q;renderOperational();}));
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

/* ================= DOWNLOADS ================= */
function csvDownload(name, rows){
  const csv=rows.map(r=>r.map(x=>`"${String(x??'').replace(/"/g,'""')}"`).join(',')).join('\n');
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob(['﻿'+csv],{type:'text/csv;charset=utf-8'}));
  a.download=name; a.click(); toast('Downloaded '+name);
}
function metaHeader(title){
  return [['CCCM Cluster Somalia — Site Monitoring Dashboard'],[title],
    ['Status','PUBLISHED'],['Reporting period', DATA.period],
    ['Data source', DATA.source],['Generated', DATA.generated],
    ['Contact', DATA.contact.im],['Methodology','See the About the Data page'],[]];
}
function renderDownloads(){
  const items=[
    ['Published Q2 KPI summary',()=>csvDownload('cccm_q2_2026_kpi_summary.csv',[...metaHeader('KPI summary'),
      ['Metric','Value'],['Sites assessed',DATA.kpi.sites],['Catchment areas',DATA.kpi.catchments],
      ['Districts',DATA.kpi.districts],['Reporting partners',DATA.kpi.partners],
      ['Households',DATA.kpi.hhs],['Individuals',DATA.kpi.individuals],['National severity %',DATA.kpi.severity]])],
    ['Published district summary',()=>csvDownload('cccm_q2_2026_district_summary.csv',[...metaHeader('District summary'),
      ['District','Region','Sites','Gap %','Coverage %','Severe','High','Moderate','Low'],
      ...DATA.districts.map(d=>[d.district,d.region,d.n,d.gap,d.cov,
        d.bands?d.bands.Severe:'',d.bands?d.bands.High:'',d.bands?d.bands.Moderate:'',d.bands?d.bands.Low:''])])],
    ['Published sector-gap table',()=>csvDownload('cccm_q2_2026_sector_gaps.csv',[...metaHeader('Sector gaps'),
      ['Sector','Gap %','Coverage %'],...DATA.sectors.map(s=>[s.name,s.gap,s.cov])])],
    ['Methodology note',()=>csvDownload('cccm_q2_2026_methodology_note.csv',[...metaHeader('Methodology note'),
      ['Section','Content'],['Purpose',DATA.about.purpose],['Severity definition',DATA.about.severity],
      ...DATA.about.limits.map((l,i)=>['Limitation '+(i+1),l])])],
  ];
  $('#dlList').innerHTML=items.map(([t],i)=>`<button class="dl-btn" data-di="${i}">
    <span>⬇ ${esc(t)}</span><span class="dmeta"><span class="pub-chip-sm">PUBLISHED</span> · Q2 2026</span></button>`).join('');
  $$('#dlList .dl-btn').forEach(b=>b.addEventListener('click',()=>items[+b.dataset.di][1]()));
}

/* ================= ABOUT THE DATA ================= */
function renderAbout(){
  const a=DATA.about;
  $('#mPurpose').innerHTML=`<p>${esc(a.purpose)}</p>`;
  $('#mSources').innerHTML=`<p><b>Reporting period:</b> ${esc(DATA.period)}</p>
    <p><b>Source:</b> ${esc(DATA.source)}</p>
    <p><b>Data sources:</b> CCCM partner site-monitoring submissions, reported quarterly.</p>`;
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
[['brand',renderBrand],['overview',renderOverview],['sector tabs',renderSectorTabs],
 ['top gaps',renderTopGaps],['districts',renderDistricts],['downloads',renderDownloads],
 ['about',renderAbout],['help modal',wireHelp]
].forEach(([label,fn])=>{ try{ fn(); } catch(e){ console.error('[public dashboard] "'+label+'" failed:', e); } });
