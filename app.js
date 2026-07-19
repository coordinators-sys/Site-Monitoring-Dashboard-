/* ================= CCCM Somalia Site Monitoring Dashboard ================= */
const SECT = DATA.sectors_order;                 // codes
const META = DATA.sectorMeta;                    // code -> [short,long,count]
const IS_KEY = {CCCM:"CCCM",Prot:"Protection",CP:"CP",GBV:"GBV",HLP:"HLP",NFI:"NFI",
  Shel:"Shelter",WASH:"WASH",Hlth:"Health",FSL:"FSL",Nutr:"Nutrition",Educ:"Education"};
const SD_ORDER = ["CCCM","Protection","CP","GBV","HLP","NFI","Shelter","WASH","Health","FSL","Nutrition","Education"];
const SD_LABEL = {CCCM:"CCCM",Protection:"Protection",CP:"Child Protection",GBV:"GBV",
  HLP:"Housing, Land & Property",NFI:"Non-Food Items",Shelter:"Shelter",WASH:"WASH",
  Health:"Health",FSL:"Food Security & Livelihoods",Nutrition:"Nutrition",Education:"Education"};
const BANDS=["Severe","High","Moderate","Low"];
const BANDCLASS={Severe:"K",High:"R",Moderate:"Y",Low:"G"};
const SCORELAB={G:"0–25% Red (Low)",Y:"26–50% Red (Moderate)",R:"51–90% Red (High)",K:"91–100% Red (Critical)",NA:"Not assessed"};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const fmt=n=>n.toLocaleString('en-US');
const el=(t,c,h)=>{const e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e;};

/* ---------- tooltip ---------- */
const tt=$('#tt');
function tip(node,html){
  node.addEventListener('mousemove',e=>{tt.innerHTML=html();tt.classList.add('show');
    let x=e.clientX+14,y=e.clientY+14; if(x>innerWidth-240)x=e.clientX-234; tt.style.left=x+'px';tt.style.top=y+'px';});
  node.addEventListener('mouseleave',()=>tt.classList.remove('show'));
}
function toast(m){const t=$('#toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),1900);}

/* ================= TAB NAV ================= */
$$('.tab').forEach(b=>b.addEventListener('click',()=>{
  $$('.tab').forEach(x=>x.classList.remove('active'));b.classList.add('active');
  $$('.view').forEach(v=>v.classList.remove('active'));
  $('#view-'+b.dataset.view).classList.add('active');
  if(b.dataset.view==='map'){renderMap();if(MAP)setTimeout(()=>MAP.invalidateSize(),60);}
  window.scrollTo({top:0,behavior:'smooth'});
}));

/* ================= OVERVIEW ================= */
function renderKPIs(){
  const k=DATA.kpi;
  // Inline stroke icons — consistent weight and colour, unlike emoji which render
  // differently on every OS and look informal in a cluster product.
  const svg=(p,accent)=>`<svg viewBox="0 0 24 24" fill="none" stroke="${accent?'var(--orange)':'var(--teal)'}"
    stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">${p}</svg>`;
  const I={
    site:'<path d="M12 21s7-5.4 7-11a7 7 0 1 0-14 0c0 5.6 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
    catch:'<path d="M3 7.5 9 4.5l6 3 6-3v12l-6 3-6-3-6 3Z"/><path d="M9 4.5v12M15 7.5v12"/>',
    hh:'<path d="M3.5 10.5 12 3.5l8.5 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5.5h4V20"/>',
    ind:'<circle cx="9" cy="8" r="3.2"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17.5" cy="9.5" r="2.4"/><path d="M16 14.6a5.6 5.6 0 0 1 5.5 5.4"/>',
    partner:'<path d="M12 20.5s-7.5-4.6-7.5-9.6a4.3 4.3 0 0 1 7.5-2.9 4.3 4.3 0 0 1 7.5 2.9c0 5-7.5 9.6-7.5 9.6Z"/>',
    dist:'<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    sev:'<path d="M12 3.5 22 20H2L12 3.5Z"/><path d="M12 10v4.5"/><circle cx="12" cy="17.4" r=".9" fill="currentColor" stroke="none"/>',
  };
  // KPI cards show the PUBLISHED figures (authoritative for external use), each with its
  // coverage denominator. The live-rebuild figures appear only in labelled Draft views.
  const P=DATA.published, pk=P?P.kpi:k, pd_=P?P.denominators:null;
  const pct=(a,b)=>b?Math.round(100*a/b)+'%':'';
  const cards=[
    {ic:svg(I.site),v:fmt(pk.sites),l:'Sites assessed',
     s:pd_?`of ${fmt(pd_.eligibleSites)} Master List sites · ${pct(pk.sites,pd_.eligibleSites)} coverage`:(k.quarter||'')},
    {ic:svg(I.catch),v:pk.catchments,l:'Catchment areas',
     s:pd_?`of ${pd_.totalCatchments} CCCM-covered CAs · ${pct(pk.catchments,pd_.totalCatchments)}`:'partner-covered'},
    {ic:svg(I.hh),v:fmt(pk.hhs),l:'Households',
     s:pd_?`of ${fmt(pd_.totalHHs)} · ${pct(pk.hhs,pd_.totalHHs)}`:''},
    {ic:svg(I.ind),v:fmt(pk.individuals),l:'Individuals',
     s:pd_?`of ${fmt(pd_.totalIndividuals)} · ${pct(pk.individuals,pd_.totalIndividuals)}`:''},
    {ic:svg(I.partner),v:pk.partners,l:'Reporting partners',s:''},
    {ic:svg(I.dist),v:pk.districts,l:'Districts',s:'across '+(k.regions||10)+' regions'},
    {ic:svg(I.sev,true),v:pk.severity+'%',l:'National severity',s:'avg red-indicator share',accent:true},
  ];
  $('#kpiRow').innerHTML=`<div style="grid-column:1/-1;margin-bottom:-6px">
      <span class="pub-chip">PUBLISHED · Q2 2026 official figures</span>
      <span style="font-size:11px;color:var(--muted);margin-left:8px">${P?P.source:''}</span>
      <span style="font-size:11px;color:var(--muted);margin-left:8px">· live draft rebuild: ${fmt(k.sites)} sites — see Data Quality tab</span>
    </div>`+cards.map(c=>`<div class="kpi ${c.accent?'accent':''}"><div class="bar-top"></div>
    <div class="k-ic">${c.ic}</div><div class="k-val">${c.v}</div><div class="k-lab">${c.l}</div>
    ${c.s?`<div class="k-sub">${c.s}</div>`:''}</div>`).join('');
  $('#findingsList').innerHTML=((P&&P.keyFindings)||DATA.keyFindings).map(f=>`<li>${f}</li>`).join('');
  $('#covNote').textContent=DATA.coverageNotes;
  // Q1 vs Q2
  const q=DATA.q1;
  // If no prior-quarter baseline was supplied, q1 mirrors q2 and every delta is 0 — which
  // renders as "coverage unchanged", a finding we have not established. Show the current
  // figures and say plainly that no baseline exists.
  const hasBaseline = DATA.hasQ1Baseline === true;
  $('#q1q2').innerHTML=Object.entries(q).map(([m,[q2,q1]])=>{
    const d=q2-q1, up=d>=0;
    return `<div class="hbar-row" style="grid-template-columns:120px 1fr 1fr 70px">
      <div class="l">${m}</div>
      <div style="font-weight:700" class="mono">${fmt(q2)}</div>
      <div style="color:var(--muted)" class="mono">${hasBaseline?fmt(q1)+' <span style="font-size:10px">Q1</span>':'<span style="font-size:11px">no baseline</span>'}</div>
      <div class="v" style="color:${hasBaseline?(up?'var(--good)':'var(--gap)'):'var(--muted)'}">${hasBaseline?(up?'▲':'▼')+' '+fmt(Math.abs(d)):'—'}</div></div>`;
  }).join('')+`<div class="note" style="margin-top:8px">${hasBaseline
      ? (DATA.q1Source||'')+(DATA.kpi.sites!==q.Sites[0]
          ? ` <b>Note:</b> this panel shows the <b>published</b> Q2 figures (${fmt(q.Sites[0])} sites).
              The KPI cards above show this <b>live rebuild</b> (${fmt(DATA.kpi.sites)} sites) — the two
              differ because the published round applied additional site-eligibility filtering.
              Reconciliation is pending; use the published figures for external reporting.`
          : '')
      : 'No Q1 2026 baseline is loaded, so no coverage change is shown.'}</div>`;
}

function renderSectorDiverge(){
  const max=Math.max(...DATA.sectors.map(s=>Math.max(s.gap,s.cov)));
  $('#sectorDiverge').innerHTML=DATA.sectors.map(s=>{
    const gw=s.gap/max*100, cw=s.cov/max*100;
    const den=s.nApplicable?`${fmt(s.nRed)} Red / ${fmt(s.nGreen)} Green of ${fmt(s.nApplicable)} applicable indicator-assessments`:'';
    return `<div class="dv-row" ${den?`data-t="<b>${s.name}</b><br>${den}"`:''}>
      <div class="lab">${s.name}</div>
      <div class="dv-left"><div class="dv-bar gap" style="width:${gw}%"><span>${s.gap}%</span></div></div>
      <div class="dv-right"><div class="dv-bar cov" style="width:${cw}%"><span>${s.cov}%</span></div></div>
    </div>`;
  }).join('');
  $$('#sectorDiverge .dv-row').forEach(r=>r.dataset.t&&tip(r,()=>r.dataset.t));
}

function renderTopLists(){
  const mk=(arr,cls,col)=>arr.map(([n,p])=>`<div class="hbar-row">
      <div class="l" title="${n}">${n}</div>
      <div class="hbar-track"><div class="hbar-fill" style="width:${p}%;background:${col}"></div></div>
      <div class="v" style="color:${col}">${p}%</div></div>`).join('');
  $('#topRed').innerHTML=mk(DATA.topRed,'r','var(--gap)');
  $('#topGreen').innerHTML=mk(DATA.topGreen,'g','var(--good)');
}

function renderDistrictGap(){
  const max=100;
  $('#districtGap').innerHTML=`<div class="dv-head"><div></div><div class="g">◀ Gap</div><div class="c">Coverage ▶</div></div>`+
  DATA.districtGap.map(([d,n,g,c])=>`<div class="dv-row">
    <div class="lab">${d}<div style="font-weight:500;color:var(--muted);font-size:10.5px">${n} sites</div></div>
    <div class="dv-left"><div class="dv-bar gap" style="width:${g}%"><span>${g}%</span></div></div>
    <div class="dv-right"><div class="dv-bar cov" style="width:${c}%"><span>${c}%</span></div></div></div>`).join('');
}

function renderPyramid(){
  const d=DATA.demographics;
  // headings are computed, never literals baked into the template
  const sh=$('#sevHint'); if(sh) sh.textContent=fmt(DATA.kpi.sites)+' assessed sites';
  ['sevCount2','exCount2'].forEach(id=>{const n=$('#'+id); if(n) n.textContent=fmt(DATA.kpi.sites);});
  // Source is named as CCCM Cluster Site Monitoring: IOM reports through the same cluster
  // instrument, so naming the underlying platforms (Kobo / Zite) misrepresents provenance.
  const pd=$('#pubDate');
  if(pd&&DATA.generated) pd.textContent='Generated '+DATA.generated+' · CCCM Cluster Site Monitoring';
  const dh=$('#demoHint');
  if(dh&&d&&d.total) dh.textContent='Age & sex · '+fmt(d.total)+' individuals, '
                        +fmt(d.matchedSites)+' matched sites';
  // Neither the Kobo form nor the Zite feed collects age/sex disaggregation (they carry
  // household and individual totals only), and the Master List does not either. Render an
  // explicit "not collected" state — an empty pyramid showing 0% reads as a real finding
  // of zero, which is worse than showing nothing.
  const total=(d&&d.bands)?d.bands.reduce((a,b)=>a+(b.mN||0)+(b.fN||0),0):0;
  if(!d||!d.bands||!d.bands.length||total===0){
    $('#pyramid').innerHTML=`<div style="padding:26px 14px;text-align:center;color:var(--muted);font-size:12.5px;line-height:1.6">
      <div style="font-weight:700;margin-bottom:6px">Age &amp; sex breakdown not collected</div>
      The site monitoring instruments record household and individual totals only.
      No age/sex disaggregation is available for this quarter.</div>`;
    $('#pyrTotals').innerHTML='';
    return;
  }
  const max=Math.max(...d.bands.flatMap(b=>[b.mN,b.fN]));
  $('#pyramid').innerHTML=d.bands.map(b=>`<div class="pyr-row">
    <div class="pyr-side m"><div class="pyr-bar m" style="width:${b.mN/max*100}%" data-t="Male ${b.age}: ${fmt(b.mN)} (${b.mP}%)">${b.mP}%</div></div>
    <div class="pyr-age">${b.age}</div>
    <div class="pyr-side f"><div class="pyr-bar f" style="width:${b.fN/max*100}%" data-t="Female ${b.age}: ${fmt(b.fN)} (${b.fP}%)">${b.fP}%</div></div>
  </div>`).join('');
  const figure=(c)=>`<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="${c}"
      stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:4px">
      <circle cx="12" cy="4.6" r="2.6"/><path d="M12 7.4v7.2"/><path d="M8 9.6h8"/>
      ${c==='var(--female)'?'<path d="M9.2 14.6h5.6l-1.3 6.6h-3Z"/>':'<path d="M9.6 14.6V21M14.4 14.6V21"/>'}</svg>`;
  $('#pyrTotals').innerHTML=
    `<span style="color:var(--male);font-weight:700">${figure('var(--male)')}Male ${d.malePct}% (${fmt(d.bands.reduce((a,b)=>a+b.mN,0))})</span>
     <span style="color:var(--female);font-weight:700">${figure('var(--female)')}Female ${d.femalePct}% (${fmt(d.bands.reduce((a,b)=>a+b.fN,0))})</span>`;
  $$('#pyramid .pyr-bar').forEach(b=>tip(b,()=>b.dataset.t));
  if(d.source){
    const n=document.createElement('div');
    n.style.cssText='margin-top:10px;font-size:11px;color:var(--muted);line-height:1.5';
    n.textContent=d.source;
    $('#pyramid').appendChild(n);
  }
}

/* Brand: CCCM Cluster logo + per-sector icons, embedded base64 so the file stays offline. */
function renderBrand(){
  const a=DATA.assets||{};
  const lg=$('#brandLogo');
  if(lg&&a.logo) lg.src=a.logo; else if(lg) lg.remove();
  const ic=a.icons||{};
  // sector icon in the gap/coverage rows
  $$('#sectorDiverge .dv-row .lab').forEach(lab=>{
    const name=lab.childNodes[0]&&lab.childNodes[0].textContent.trim();
    const code=SECT.find(c=>META[c][1]===name||META[c][0]===name);
    if(code&&ic[code]) lab.insertAdjacentHTML('afterbegin',
      `<img src="${ic[code]}" alt="" class="sec-ic">`);
  });
  // deep-dive tab icons are injected by renderSDTabs (it re-renders on every click)
}

function renderDonut(){
  const counts={}; BANDS.forEach(b=>counts[b]=0);
  DATA.sites.forEach(s=>counts[s.b]++);
  const total=DATA.sites.length, R=52, C=2*Math.PI*R; let off=0;
  const colors={Severe:'var(--s-crit)',High:'var(--s-high)',Moderate:'var(--s-mod)',Low:'var(--s-low)'};
  let segs='';
  BANDS.forEach(b=>{const frac=counts[b]/total, len=frac*C;
    segs+=`<circle r="${R}" cx="70" cy="70" fill="none" stroke="${colors[b]}" stroke-width="20"
      stroke-dasharray="${len} ${C-len}" stroke-dashoffset="${-off}" transform="rotate(-90 70 70)"></circle>`;
    off+=len;});
  $('#sevDonut').innerHTML=`<svg width="140" height="140" viewBox="0 0 140 140">${segs}
    <text x="70" y="64" text-anchor="middle" font-size="26" font-weight="800" fill="var(--ink)">${DATA.kpi.severity}%</text>
    <text x="70" y="82" text-anchor="middle" font-size="10.5" fill="var(--muted)">avg severity</text></svg>`;
  $('#sevDonutLegend').innerHTML=`<div class="grid" style="grid-template-columns:1fr 1fr;gap:6px 18px">`+
    BANDS.map(b=>`<div style="display:flex;align-items:center;gap:8px;font-size:12.5px">
      <span class="dot ${BANDCLASS[b]}"></span><b>${b}</b>
      <span style="color:var(--muted);margin-left:auto" class="mono">${fmt(counts[b])} · ${(counts[b]/total*100).toFixed(0)}%</span></div>`).join('')+`</div>`;
}

/* ================= SEVERITY BY DISTRICT ================= */
function renderSeverityView(){
  const ds=DATA.districtSev, colors={Severe:'var(--s-crit)',High:'var(--s-high)',Moderate:'var(--s-mod)',Low:'var(--s-low)'};
  $('#districtStacks').innerHTML=ds.map(d=>{
    const segs=BANDS.map(b=>{const v=d[b]; if(!v)return'';
      return `<div class="stk-seg" style="flex:${v};background:${colors[b]}" data-t="<b>${d.district}</b> · ${b}: ${v} sites (${(v/d.n*100).toFixed(0)}%)">${v/d.n>0.09?v:''}</div>`;}).join('');
    return `<div class="stk-row"><div class="l" title="${d.district}">${d.district}</div>
      <div class="stk-track">${segs}</div><div class="n mono">${d.n}</div></div>`;
  }).join('');
  $$('#districtStacks .stk-seg').forEach(s=>tip(s,()=>s.dataset.t));
  // Minimum-sample rule: districts with tiny samples must not be read alongside large
  // ones without warning. <5 insufficient; 5-9 interpret cautiously; >=10 rankable.
  const sample=n=>n>=10?'':n>=5?'<div style="font-size:10px;color:#9a5b13;font-weight:600">5–9 sites — interpret cautiously</div>'
                              :'<div style="font-size:10px;color:var(--gap);font-weight:600">&lt;5 sites — insufficient for ranking</div>';
  $('#districtTable').innerHTML=ds.map(d=>`<tr>
    <td class="site-nm">${d.district}${sample(d.n)}</td><td>${d.region}</td><td class="ctr mono">${d.n}</td>
    <td class="ctr"><span class="badge ${d.avg>=55?'Severe':d.avg>=40?'High':d.avg>=25?'Moderate':'Low'}">${d.avg}%</span></td>
    <td class="ctr mono">${d.Severe}</td><td class="ctr mono">${d.High}</td><td class="ctr mono">${d.Moderate}</td><td class="ctr mono">${d.Low}</td>
  </tr>`).join('');
  renderPartnerTable();
}

/* Partner coverage — the cluster-coordinator view: who reports where, caseload scale,
   and the severity mix of the sites each partner monitors. */
function renderPartnerTable(){
  const host=$('#partnerTable'); if(!host) return;
  const by={};
  DATA.sites.forEach(s=>{
    const p=s.p||'—';
    (by[p]=by[p]||{p,n:0,sev:0,d:new Set(),hh:0,ind:0,Severe:0,High:0,Moderate:0,Low:0});
    const o=by[p]; o.n++; o.sev+=s.v; o.d.add(s.d);
    o.hh+=(s.hh||0); o.ind+=(s.ind||0); o[s.b]=(o[s.b]||0)+1;
  });
  const rows=Object.values(by).sort((a,b)=>b.n-a.n);
  host.innerHTML=rows.map(o=>{
    const avg=(o.sev/o.n).toFixed(1);
    const cls=avg>=55?'Severe':avg>=40?'High':avg>=25?'Moderate':'Low';
    return `<tr>
      <td class="site-nm">${o.p}</td><td class="ctr mono">${fmt(o.n)}</td>
      <td class="ctr mono">${o.d.size}</td><td class="ctr mono">${fmt(o.hh)}</td>
      <td class="ctr mono">${fmt(o.ind)}</td>
      <td class="ctr"><span class="badge ${cls}">${avg}%</span></td>
      <td class="ctr mono">${o.Severe}</td><td class="ctr mono">${o.High}</td>
      <td class="ctr mono">${o.Moderate}</td><td class="ctr mono">${o.Low}</td></tr>`;
  }).join('');
}

/* ================= SITE EXPLORER ================= */
let EX={region:'',district:'',band:'',sector:'',partner:'',search:'',sort:'v',dir:-1,page:0,per:40};
function uniq(arr){return [...new Set(arr)].sort();}
function populateSelects(){
  const regions=uniq(DATA.sites.map(s=>s.r)), districts=uniq(DATA.sites.map(s=>s.d));
  const regOpts='<option value="">All regions</option>'+regions.map(r=>`<option>${r}</option>`).join('');
  const distOpts='<option value="">All districts</option>'+districts.map(d=>`<option>${d}</option>`).join('');
  const secOpts=SECT.map(c=>`<option value="${c}">${META[c][1]}</option>`).join('');
  $('#fRegion').innerHTML=regOpts; $('#fDistrict').innerHTML=distOpts;
  $('#fSector').innerHTML='<option value="">Any sector</option>'+secOpts;
  const partners=uniq(DATA.sites.map(s=>s.p||'').filter(Boolean));
  const pOpts='<option value="">All partners</option>'+partners.map(p=>`<option>${p}</option>`).join('');
  const fp=$('#fPartner'); if(fp) fp.innerHTML=pOpts;
}
function filterSites(f){
  return DATA.sites.filter(s=>{
    if(f.region&&s.r!==f.region)return false;
    if(f.district&&s.d!==f.district)return false;
    if(f.band&&s.b!==f.band)return false;
    if(f.partner&&(s.p||'')!==f.partner)return false;
    if(f.search){const q=f.search.toLowerCase();
      if(!s.s.toLowerCase().includes(q)&&!(s.code||'').toLowerCase().includes(q))return false;}
    if(f.sector){const i=SECT.indexOf(f.sector);const v=s.sc[i]; if(v!=='R'&&v!=='K')return false;}
    return true;
  });
}
function renderExplorer(){
  let list=filterSites(EX);
  // sort
  list.sort((a,b)=>{
    let av,bv;
    if(EX.sort==='v'){av=a.v;bv=b.v;}
    else if(EX.sort==='s'){av=a.s.toLowerCase();bv=b.s.toLowerCase();}
    else if(EX.sort==='p'){av=(a.p||'').toLowerCase();bv=(b.p||'').toLowerCase();}
    else if(EX.sort==='d'){av=a.d;bv=b.d;}
    else {const i=SECT.indexOf(EX.sort);const rank={K:4,R:3,Y:2,G:1,NA:0};av=rank[a.sc[i]];bv=rank[b.sc[i]];}
    if(av<bv)return -EX.dir; if(av>bv)return EX.dir; return 0;
  });
  const avg=list.length?(list.reduce((a,s)=>a+s.v,0)/list.length).toFixed(1):'—';
  $('#explorerCount').textContent=fmt(list.length)+' sites';
  $('#explorerAvg').innerHTML=list.length?`avg severity <b>${avg}%</b> · Severe ${list.filter(s=>s.b==='Severe').length} · High ${list.filter(s=>s.b==='High').length}`:'';
  // header
  $('#sitesHead').innerHTML=`
    <th class="sortable" data-s="s">Site</th><th class="sortable" data-s="p">Partner</th><th class="sortable" data-s="d">District</th><th>Region</th><th>CA</th>`+
    SECT.map(c=>`<th class="sect sortable" data-s="${c}" title="${META[c][1]} (${META[c][2]} indicators)">${META[c][0]}</th>`).join('')+
    `<th class="sortable ctr" data-s="v">Sev.</th>`;
  // page
  const pages=Math.max(1,Math.ceil(list.length/EX.per));
  if(EX.page>=pages)EX.page=0;
  const slice=list.slice(EX.page*EX.per,(EX.page+1)*EX.per);
  $('#sitesBody').innerHTML=slice.map(s=>`<tr>
    <td class="site-nm">${s.s}${s.code&&s.code!==s.s?`<div style="font-weight:500;color:var(--muted);font-size:10px;font-family:ui-monospace,monospace">${s.code}</div>`:''}</td>
    <td style="font-size:11.5px">${s.p||'—'}</td><td>${s.d}</td><td style="color:var(--ink-2)">${s.r}</td>
    <td style="color:var(--muted)">${s.c||'—'}</td>`+
    s.sc.map((v,i)=>`<td class="ctr"><span class="dot ${v} ${v==='NA'?'sq':''}" data-t="${META[SECT[i]][1]}: ${SCORELAB[v]}"></span></td>`).join('')+
    `<td class="ctr"><span class="badge ${s.b}">${s.v}%</span></td></tr>`).join('');
  $$('#sitesBody .dot').forEach(d=>d.dataset.t&&tip(d,()=>d.dataset.t));
  $('#pagerInfo').textContent=`Showing ${list.length?EX.page*EX.per+1:0}–${Math.min((EX.page+1)*EX.per,list.length)} of ${fmt(list.length)}`;
  $('#pgNum').textContent=`${EX.page+1} / ${pages}`;
  $$('#sitesHead .sortable').forEach(th=>th.addEventListener('click',()=>{
    const s=th.dataset.s; if(EX.sort===s)EX.dir*=-1; else{EX.sort=s;EX.dir=(s==='s'||s==='d'||s==='p')?1:-1;}
    EX.page=0; renderExplorer();
  }));
}
function wireExplorer(){
  $('#fRegion').addEventListener('change',e=>{EX.region=e.target.value;EX.page=0;renderExplorer();});
  $('#fDistrict').addEventListener('change',e=>{EX.district=e.target.value;EX.page=0;renderExplorer();});
  $('#fBand').addEventListener('change',e=>{EX.band=e.target.value;EX.page=0;renderExplorer();});
  $('#fSector').addEventListener('change',e=>{EX.sector=e.target.value;EX.page=0;renderExplorer();});
  const fp=$('#fPartner');
  if(fp) fp.addEventListener('change',e=>{EX.partner=e.target.value;EX.page=0;renderExplorer();});
  $('#fSearch').addEventListener('input',e=>{EX.search=e.target.value;EX.page=0;renderExplorer();});
  $('#prevPg').addEventListener('click',()=>{if(EX.page>0){EX.page--;renderExplorer();}});
  $('#nextPg').addEventListener('click',()=>{EX.page++;renderExplorer();});
  $('#clearFilters').addEventListener('click',()=>{
    EX={...EX,region:'',district:'',band:'',sector:'',partner:'',search:'',page:0};
    $('#fRegion').value='';$('#fDistrict').value='';$('#fBand').value='';$('#fSector').value='';$('#fSearch').value='';
    if($('#fPartner'))$('#fPartner').value='';
    renderExplorer();
  });
  $('#exportCsv').addEventListener('click',exportCsv);
  
}
function exportCsv(){
  const list=filterSites(EX);
  const head=['Site','Site code','Partner','District','Region','CA','Households','Individuals',
              'Severity%','Band',...SECT.map(c=>META[c][1])];
  const rows=list.map(s=>[s.s,s.code||'',s.p||'',s.d,s.r,s.c,s.hh??'',s.ind??'',s.v,s.b,...s.sc]
    .map(x=>`"${(''+x).replace(/"/g,'""')}"`).join(','));
  const csv=head.join(',')+'\n'+rows.join('\n');
  const blob=new Blob([csv],{type:'text/csv'}),a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download='cccm_sites_q2_2026_filtered.csv';a.click();
  toast('Exported '+list.length+' sites to CSV');
}

/* ================= SECTOR DEEP DIVE ================= */
const BD_BY_SECTOR={
  CCCM:["CMC site improvement (# sites)"],
  NFI:["NFI last received (# sites)","NFI type distributed (# sites)"],
  Shelter:["Shelter last received (# sites)"],
  WASH:["Water per person/day (# sites)","Time to water point (# sites)","Primary water source (# sites)","Primary barrier to water (# sites)","Latrines (totals)"],
  Health:["Distance to health facility (# sites)"],
  FSL:["Last food/cash on-site (# sites)","Food/cash assistance type (# sites)"],
  Nutrition:["Community access to nutrition (# sites)","Nutrition services (# sites)"],
  Education:["Distance to learning centre (# sites)"]
};
let SD_CUR="WASH";
function renderSDTabs(){
  const ic=(DATA.assets&&DATA.assets.icons)||{}, LONG2CODE=Object.fromEntries(Object.entries(IS_KEY).map(([c,l])=>[l,c]));
  $('#sdTabs').innerHTML=SD_ORDER.map(k=>{
    const code=LONG2CODE[k], img=code&&ic[code]?`<img src="${ic[code]}" alt="" class="sec-ic">`:'';
    return `<button class="sd-tab ${k===SD_CUR?'active':''}" data-k="${k}">${img}${SD_LABEL[k]}</button>`;
  }).join('');
  $$('#sdTabs .sd-tab').forEach(b=>b.addEventListener('click',()=>{SD_CUR=b.dataset.k;renderSDTabs();renderSD();}));
}
function renderSD(){
  const rows=DATA.indicatorScoring[SD_CUR];
  $('#sdTitle').innerHTML=`${SD_LABEL[SD_CUR]} <span class="hint" style="font-weight:500;color:var(--muted)">${rows.length} indicators, sorted by gap</span>`;
  const sorted=[...rows].sort((a,b)=>b[3]-a[3]);
  $('#sdIndicators').innerHTML=sorted.map(([name,g,y,r])=>`<div class="tri-row">
    <div class="l">${name}</div>
    <div class="tri-bar" data-t="Green ${g}% · Yellow ${y}% · Red ${r}%">
      ${g?`<div class="tri-seg g" style="width:${g}%"></div>`:''}
      ${y?`<div class="tri-seg y" style="width:${y}%"></div>`:''}
      ${r?`<div class="tri-seg r" style="width:${r}%"></div>`:''}</div>
    <div class="rp">${r}%</div></div>`).join('');
  $$('#sdIndicators .tri-bar').forEach(b=>tip(b,()=>b.dataset.t));
  // breakdowns
  const bds=BD_BY_SECTOR[SD_CUR]||[];
  // aggregates/breakdowns may be absent for a given build — render only what exists
  const AG=DATA.aggregates||{}, BD=DATA.breakdowns||{};
  const agCard=(title,rows)=>{
    const have=rows.filter(([,v])=>v!=null);
    return have.length?`<div class="card p bd-card" style="box-shadow:none;border-color:var(--line-2)"><h4>${title}</h4>
      <table class="mini-tbl">${have.map(([k,v])=>`<tr><td>${k}</td><td>${fmt(v)}</td></tr>`).join('')}</table></div>`:'';
  };
  let extra='';
  if(SD_CUR==='Nutrition')extra=agCard('Acute malnutrition (children)',
    [['Moderate (MAM)',AG.childMAM],['Severe (SAM)',AG.childSAM]]);
  if(SD_CUR==='Shelter') extra=agCard('Households reached',[['HHs receiving shelter assistance',AG.hhShelter]]);
  if(SD_CUR==='NFI')     extra=agCard('Households reached',[['HHs receiving NFI assistance',AG.hhNFI]]);
  if(SD_CUR==='FSL')     extra=agCard('Households reached',[['HHs receiving food/cash',AG.hhFoodCash]]);
  const cards=bds.map(key=>{const obj=BD[key];
    if(!obj||!Object.keys(obj).length) return '';
    return `<div class="card p bd-card" style="box-shadow:none;border-color:var(--line-2)"><h4>${key}</h4>
      <table class="mini-tbl">${Object.entries(obj).map(([k,v])=>`<tr><td>${k}</td><td>${fmt(v)}</td></tr>`).join('')}</table></div>`;}).join('');
  $('#sdBreakdowns').innerHTML=(extra+cards)|| '<p style="color:var(--muted);font-size:12.5px">No operational breakdown tables for this sector.</p>';
}

/* ================= MAP (Leaflet + OpenStreetMap) ================= */
const MAPST={fill:'sev',sites:true,ca:false};
let MAP=null, MAPLAYERS=null;
function bandColor(v){return v>=55?'#c0392b':v>=40?'#ee6a3a':v>=25?'#f4a929':'#2ba24d';}
function covColor(n){return n>=200?'#1f6b72':n>=50?'#2f8f97':n>=10?'#6fb3b9':n>=1?'#b7d8db':'#d5dbd9';}
function renderMap(){
  const geo=DATA.geo, host=$('#somMap');
  if(!host) return;
  if(!geo||typeof L==='undefined'){
    host.innerHTML='<p style="padding:30px;color:var(--muted)">Map not available in this build.</p>';return;
  }
  if(MAP) return;
  const alias=geo.pcodeAlias||{};
  const agg={};
  DATA.sites.forEach(s=>{
    const pc=(alias[s.pc]||s.pc||'').toUpperCase(); if(!pc) return;
    (agg[pc]=agg[pc]||{n:0,sev:0}); agg[pc].n++; agg[pc].sev+=s.v;
  });
  const distFill=pc=>{
    const a=agg[pc];
    if(MAPST.fill==='cov') return covColor(a?a.n:0);
    return a?bandColor(a.sev/a.n):'#d5dbd9';
  };
  MAP=L.map('somMap',{zoomSnap:.5,attributionControl:true});
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    maxZoom:17,
    attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
  }).addTo(MAP);
  const swap=r=>r.map(([x,y])=>[y,x]);   // geo.json stores [lon,lat]; Leaflet wants [lat,lng]
  const distPolys=[];
  const gDist=L.layerGroup().addTo(MAP);
  geo.districts.forEach(d=>{
    const a=agg[d.pc];
    const poly=L.polygon(d.rings.map(swap),{color:'#fff',weight:.8,fillColor:distFill(d.pc),fillOpacity:.55});
    poly.bindTooltip(a?`<b>${d.n}</b> · ${d.r}<br>${a.n} sites assessed · avg severity ${(a.sev/a.n).toFixed(1)}%`
                      :`<b>${d.n}</b> · ${d.r}<br>Not assessed this quarter`,{sticky:true});
    poly._pc=d.pc; distPolys.push(poly); poly.addTo(gDist);
  });
  const gCA=L.layerGroup();
  geo.catchments.forEach(c=>{
    L.polygon(c.rings.map(swap),{color:'#1f6b72',weight:1,dashArray:'4 3',fill:false})
     .bindTooltip(`<b>${c.ca}</b> · ${c.d}<br>${c.agency||'—'} · HH ${fmt(c.hh)} · ind ${fmt(c.ind)}`,{sticky:true})
     .addTo(gCA);
  });
  const gSites=L.layerGroup().addTo(MAP);
  DATA.sites.forEach(s=>{
    if(s.lat==null||s.lon==null) return;
    if(s.lat<-2||s.lat>12.5||s.lon<40||s.lon>52) return;
    const m=L.circleMarker([s.lat,s.lon],{radius:4.5,color:'#fff',weight:.8,
      fillColor:s.b==='Severe'?'#c0392b':s.b==='High'?'#ee6a3a':s.b==='Moderate'?'#f4a929':'#2ba24d',fillOpacity:.95});
    m.bindTooltip(`<b>${s.s}</b>${s.code&&s.code!==s.s?' · <span style="font-family:monospace;font-size:10px">'+s.code+'</span>':''}
      <br>${s.d} · ${s.c||'—'} · ${s.p||'—'}
      <br>HH ${s.hh!=null?fmt(Math.round(s.hh)):'—'} · Individuals ${s.ind!=null?fmt(Math.round(s.ind)):'—'}
      <br>Severity <b>${s.v}%</b> (${s.b}) · <i>draft — pending validation</i>`,{sticky:true});
    m.on('click',()=>{
      EX={...EX,region:'',district:'',band:'',sector:'',partner:'',search:s.code||s.s,page:0};
      $('#fSearch').value=EX.search;
      ['fRegion','fDistrict','fBand','fSector','fPartner'].forEach(id=>{const e=$('#'+id);if(e)e.value='';});
      renderExplorer();
      $$('.tab').forEach(x=>x.classList.remove('active'));
      document.querySelector('.tab[data-view=explorer]').classList.add('active');
      $$('.view').forEach(v=>v.classList.remove('active'));
      $('#view-explorer').classList.add('active');
      window.scrollTo({top:0});
    });
    m.addTo(gSites);
  });
  MAPLAYERS={gSites,gCA,distPolys,distFill};
  MAP.fitBounds(gDist.getLayers()[0]?L.featureGroup(distPolys).getBounds():[[ -1.7,41],[12,51.4]]);
  $$('.map-layer').forEach(b=>{
    const Lr=b.dataset.layer;
    b.classList.toggle('active',Lr===MAPST.fill||(Lr==='sites'&&MAPST.sites)||(Lr==='ca'&&MAPST.ca));
    b.onclick=()=>{
      if(Lr==='sev'||Lr==='cov'){MAPST.fill=Lr;
        distPolys.forEach(p=>p.setStyle({fillColor:distFill(p._pc)}));
        $$('.map-layer').forEach(x=>{if(['sev','cov'].includes(x.dataset.layer))x.classList.toggle('active',x.dataset.layer===Lr);});
      }else if(Lr==='sites'){MAPST.sites=!MAPST.sites;MAPST.sites?gSites.addTo(MAP):MAP.removeLayer(gSites);b.classList.toggle('active',MAPST.sites);}
      else if(Lr==='ca'){MAPST.ca=!MAPST.ca;MAPST.ca?gCA.addTo(MAP):MAP.removeLayer(gCA);b.classList.toggle('active',MAPST.ca);}
      renderMapLegend();
    };
  });
  renderMapLegend();
}
function renderMapLegend(){
  const it=(c,l)=>`<span class="it"><span class="dot" style="background:${c}"></span>${l}</span>`;
  $('#mapLegend').innerHTML = MAPST.fill==='sev'
    ? it('#c0392b','Severe ≥55%')+it('#ee6a3a','High 40–55%')+it('#f4a929','Moderate 25–40%')
      +it('#2ba24d','Low <25%')+it('#d5dbd9','Not assessed')
    : it('#1f6b72','200+ sites')+it('#2f8f97','50–199')+it('#6fb3b9','10–49')+it('#b7d8db','1–9')+it('#d5dbd9','None');
}

/* ================= PRIORITY GAPS ================= */
function renderGaps(){
  const g=DATA.priorityGaps; if(!g||!$('#gapsTable')) return;
  $('#gapsFormula').textContent=g.formula||'';
  $('#gapsActiveNote').textContent=g.activeNote||'';
  const dn=$('#draftN'); if(dn) dn.textContent=fmt(DATA.kpi.sites);
  $('#gapsTable').innerHTML=g.rows.map((r,i)=>`<tr>
    <td class="ctr mono">${i+1}</td>
    <td class="site-nm">${r.indicator}</td>
    <td style="font-size:11.5px">${r.sector}</td>
    <td class="ctr"><b style="color:var(--gap)">${r.redPct}%</b>
      <div style="font-size:10px;color:var(--muted)">${fmt(r.nRed)} of ${fmt(r.nApplicable)}</div></td>
    <td class="ctr mono">${fmt(r.hhAffected)}</td>
    <td class="ctr mono">${fmt(r.indAffected)}</td>
    <td class="ctr mono">${r.districtsAffected}</td>
    <td class="ctr"><b>${r.priorityScore}</b><span style="font-size:10px;color:var(--muted)">/75</span></td>
  </tr>`).join('');
}

/* ================= DATA QUALITY ================= */
function renderQuality(){
  const rc=DATA.recon, q=DATA.quality;
  if(!rc||!$('#reconTable')) return;
  const row=(k,v,strong)=>`<tr><td>${k}</td><td style="text-align:right;${strong?'font-weight:700':''}">${v}</td></tr>`;
  $('#reconTable').innerHTML=[
    row('Kobo submissions in Q2 window',fmt(rc.kobo_submissions_q2)),
    row('&nbsp;&nbsp;duplicate submissions collapsed','−'+fmt(rc.kobo_duplicates_collapsed)),
    row('Kobo sites',fmt(rc.kobo_sites)),
    row('IOM sites (Q2 window)',fmt(rc.iom_sites_q2)),
    row('Union before resolution',fmt(rc.union_before_resolution)),
    row('&nbsp;&nbsp;free-text names resolved to CCCM codes',fmt(rc.freetext_resolved_to_codes)),
    row('&nbsp;&nbsp;cross-source duplicates collapsed','−'+fmt(rc.cross_source_duplicates_collapsed)),
    row('<b>Final draft sites</b>',fmt(rc.final_draft_sites),1),
    row('&nbsp;&nbsp;of which name-pending review',fmt(rc.name_pending_review)),
    row('<b>Published Q2 sites (official)</b>',fmt(rc.published_sites),1),
    row('Draft minus published',(rc.delta_vs_published>0?'+':'')+rc.delta_vs_published),
  ].join('');
  $('#reconNote').textContent=rc.delta_explanation||'';
  const mm=q.masterlist_match_methods||{};
  $('#qualityTable').innerHTML=[
    row('Master List matched (population source)',`${fmt(q.masterlist_matched)} of ${fmt(DATA.kpi.sites)}`),
    row('&nbsp;&nbsp;by CCCM code',fmt(mm.code||0)),
    row('&nbsp;&nbsp;by verified name',fmt(mm.name||0)),
    row('&nbsp;&nbsp;by GPS + name agreement',fmt(mm['gps+name']||0)),
    row('Site Verification matched (age/sex source)',`${fmt(q.siteverif_matched)} of ${fmt(DATA.kpi.sites)}`),
    row('Missing GPS coordinates',fmt(q.missing_gps)),
    row('Population from Master List / from form',`${fmt(q.population_from_masterlist)} / ${fmt(q.population_from_form)}`),
    row('Site names pending verification',fmt(q.name_pending)),
  ].join('');
  $('#qualityPartners').innerHTML=(q.partners||[]).map(p=>`<tr>
    <td class="site-nm">${p.partner}</td><td class="ctr mono">${fmt(p.sites)}</td>
    <td class="ctr mono">${p.latest||'—'}</td></tr>`).join('');
}

/* ================= INIT =================
   Each renderer runs independently. Previously these were chained on one line, so a single
   throw (a stale selector left behind when a panel was removed) silently killed every
   renderer after it — filters, sector tabs and branding all vanished with no console error
   visible to the user. Isolate failures and surface them. */
[['KPIs',renderKPIs],['sector gap/coverage',renderSectorDiverge],['top lists',renderTopLists],
 ['district gap',renderDistrictGap],['demographics',renderPyramid],['severity donut',renderDonut],
 ['severity view',renderSeverityView],['filter options',populateSelects],
 ['explorer wiring',wireExplorer],['explorer table',renderExplorer],
 ['sector tabs',renderSDTabs],['sector deep-dive',renderSD],['branding',renderBrand],
 ['priority gaps',renderGaps],['data quality',renderQuality]
].forEach(([label,fn])=>{
  try{ fn(); }
  catch(e){ console.error('[dashboard] "'+label+'" failed:',e); }
});
