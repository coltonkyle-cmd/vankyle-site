/* VanKyle site widgets: state budget + county limits. Data: /data/states.json, /data/mtsp/<ST>.json (HUD FY2026 MTSP limits). */
(function(){
var cache={};
function j(u){if(!cache[u])cache[u]=fetch(u).then(function(r){if(!r.ok)throw r.status;return r.json()});return cache[u]}
function money(x){return '$'+Math.round(x).toLocaleString()}
function big(x){return x>=1e9?'$'+(x/1e9).toFixed(2)+' billion':'$'+(x/1e6).toFixed(1)+' million'}
var SAVE='vk_state';
function getSaved(){try{return localStorage.getItem(SAVE)}catch(e){return null}}
function setSaved(v){try{localStorage.setItem(SAVE,v)}catch(e){}}
function stateSelect(list,cur){return '<select class="w-st" aria-label="Pick your state"><option value="">Pick your state&hellip;</option>'+list.map(function(s){return '<option value="'+s.st+'"'+(s.st===cur?' selected':'')+'>'+s.name+'</option>'}).join('')+'</select>'}

function stateBudget(el){
  j('/data/states.json').then(function(d){
    var mode=el.getAttribute('data-show')||'both';
    el.innerHTML='<div class="w-head">Pick your state</div>'+stateSelect(d.states,getSaved())+'<div class="w-out"></div><p class="w-note">Estimate using 2027 IRS amounts and '+d.pop_source+'. The IRS sets official figures from its own population numbers. Not a primary source.</p>';
    var sel=el.querySelector('.w-st'),out=el.querySelector('.w-out');
    function show(){var s=d.states.filter(function(x){return x.st===sel.value})[0];if(!s){out.innerHTML='';return}
      setSaved(s.st);
      var p=s.pop, cr=p?Math.max(p*d.credit_pc,d.credit_min):d.credit_min, pab=p?Math.max(p*d.pab_pc,d.pab_min):d.pab_min;
      var crMin=!p||p*d.credit_pc<d.credit_min, pabMin=!p||p*d.pab_pc<d.pab_min;
      var h='<div class="w-cards">';
      if(mode!=='bonds')h+='<div class="w-card"><small>2027 9% credit budget</small><strong>'+big(cr)+'</strong><span>a year'+(crMin?' (small-state minimum)':'')+'. Awards are claimed for 10 years, so that’s about '+big(cr*10)+' of total credits.</span></div>';
      if(mode!=='credits')h+='<div class="w-card"><small>2027 private activity bond cap</small><strong>'+big(pab)+'</strong><span>'+(pabMin?'small-state minimum; ':'')+'shared with other bond uses, not just housing.</span></div>';
      h+='</div>'+(p?'<p class="w-sub">'+s.name+' population: '+p.toLocaleString()+'</p>':'');
      out.innerHTML=h}
    sel.addEventListener('change',show);show();
  }).catch(function(){el.innerHTML='<p class="w-note">State data couldn’t load.</p>'});
}

var BR=[['Studio',1,0],['1 bedroom',1.5,1],['2 bedrooms',3,2],['3 bedrooms',4.5,3],['4 bedrooms',6,4]];
function limFor(row,pct,size){var base=function(n){return row[2+n]};var v=(size%1)?(base(Math.floor(size))+base(Math.ceil(size)))/2:base(size);return v*pct/50}
function countyPicker(el,onPick){
  j('/data/states.json').then(function(d){
    el.innerHTML='<div class="w-pick">'+stateSelect(d.states,getSaved())+'<select class="w-co" aria-label="Pick your county" disabled><option>Pick your county&hellip;</option></select></div>';
    var ss=el.querySelector('.w-st'),cs=el.querySelector('.w-co'),rows=[];
    function loadCounties(keep){if(!ss.value){cs.disabled=true;return}setSaved(ss.value);
      j('/data/mtsp/'+ss.value+'.json').then(function(r){rows=r;cs.disabled=false;
        cs.innerHTML='<option value="">Pick your county&hellip;</option>'+r.map(function(x,i){return '<option value="'+i+'">'+x[0]+'</option>'}).join('');})}
    ss.addEventListener('change',function(){loadCounties()});
    cs.addEventListener('change',function(){var r=rows[+cs.value];if(r)onPick(r,ss.options[ss.selectedIndex].text)});
    if(ss.value)loadCounties();
  });
}
function countyLimits(el){
  el.innerHTML='<div class="w-head">Look up your county</div><div class="w-picker"></div><label class="w-lvl">Income level <select><option>30</option><option>50</option><option selected>60</option><option>80</option></select>% of AMI</label><div class="w-out"><p class="w-sub">Pick a state and county to see its income limits and maximum rents.</p></div><p class="w-note">HUD FY2026 MTSP income limits (effective May 1, 2026), regular limits. Older properties may use higher “hold harmless” or HERA Special limits. Max rent includes the utility allowance. Not a primary source; properties use the official HUD tables.</p>';
  var lvl=el.querySelector('.w-lvl select'),out=el.querySelector('.w-out'),cur=null,stn='';
  function show(){if(!cur)return;var pct=+lvl.value;
    var lim='<tr>'+[1,2,3,4,5,6].map(function(n){return '<td>'+money(limFor(cur,pct,n))+'</td>'}).join('')+'</tr>';
    var rent='<tr>'+BR.map(function(b){return '<td>'+money(Math.floor(limFor(cur,pct,b[1])*0.3/12))+'</td>'}).join('')+'</tr>';
    out.innerHTML='<p class="w-sub"><b>'+cur[0]+', '+stn+'</b> &middot; area median income '+money(cur[2])+' &middot; '+cur[1]+'</p>'+
     '<div class="table-wrap"><table class="cmp w-tbl"><caption>Income limits at '+pct+'% of AMI, by household size</caption><thead><tr>'+[1,2,3,4,5,6].map(function(n){return '<th>'+n+' '+(n>1?'people':'person')+'</th>'}).join('')+'</tr></thead><tbody>'+lim+'</tbody></table></div>'+
     '<div class="table-wrap"><table class="cmp w-tbl"><caption>Maximum gross rent at '+pct+'% of AMI (rent + utility allowance)</caption><thead><tr>'+BR.map(function(b){return '<th>'+b[0]+'</th>'}).join('')+'</tr></thead><tbody>'+rent+'</tbody></table></div>'}
  lvl.addEventListener('change',show);
  countyPicker(el.querySelector('.w-picker'),function(r,s){cur=r;stn=s;show()});
}
window.VK=window.VK||{};VK.countyPicker=countyPicker;VK.limFor=limFor;
/* number inputs with commas: <input type="text" inputmode="decimal" data-num> */
function fmtNum(el,live){
  var raw=String(el.value), caret=live&&el.selectionStart!=null?el.selectionStart:null;
  var before=caret==null?0:raw.slice(0,caret).replace(/[^0-9.]/g,'').length;
  var neg=/^\s*-/.test(raw), clean=raw.replace(/[^0-9.]/g,''), dot=clean.indexOf('.');
  var ip=dot<0?clean:clean.slice(0,dot), dp=dot<0?'':'.'+clean.slice(dot+1).replace(/\./g,'');
  ip=ip.replace(/^0+(?=\d)/,'').replace(/\B(?=(\d{3})+(?!\d))/g,',');
  var out=(neg?'-':'')+ip+dp; if(out===raw)return; el.value=out;
  if(caret!=null){var n=0,i=0;for(;i<out.length&&n<before;i++){if(/[0-9.]/.test(out[i]))n++}try{el.setSelectionRange(i,i)}catch(e){}}
}
function fmtAll(){document.querySelectorAll('input[data-num]').forEach(function(el){fmtNum(el,false)})}
document.addEventListener('input',function(e){if(e.target.matches&&e.target.matches('input[data-num]'))fmtNum(e.target,true)});
window.VK=window.VK||{};VK.fmtAll=fmtAll;VK.num=function(el){return parseFloat(String(el.value).replace(/,/g,''))};
fmtAll();

document.querySelectorAll('.w-state-budget').forEach(stateBudget);
document.querySelectorAll('.w-county-limits').forEach(countyLimits);
})();
