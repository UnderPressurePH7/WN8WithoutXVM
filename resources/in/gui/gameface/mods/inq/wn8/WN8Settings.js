import { ModelObserver } from "../../libs/model.js";

const observer = ModelObserver();
const PANEL_W = 980;
const PANEL_H = 640;
const VIEWPORT_H = 560;
let state = {settings:{}, options:{}, meta:{}, i18n:{}};
let lastPayload = null;
let draggingSlider = null;
let draggingScroll = false;
let scrollGrabY = 0;
let scrollGrabTop = 0;
let scrollY = 0;

function model(){ return observer.model; }
function parsePayload(raw){ try{return JSON.parse(String(raw||'{}'));}catch(e){return {settings:{},options:{},meta:{},i18n:{}};} }
function text(key,fallback){const map=state.i18n||{};const value=map[key];return value==null?fallback:String(value);}
function applyTranslations(){
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    const key=el.getAttribute('data-i18n');
    el.textContent=text(key,el.textContent||'');
  });
  document.querySelectorAll('[data-i18n-aria]').forEach(function(el){
    const key=el.getAttribute('data-i18n-aria');
    el.setAttribute('aria-label',text(key,el.getAttribute('aria-label')||''));
  });
}
function centerPanel(vm){
  const root=document.querySelector('.inq-root');if(!root||!vm)return;
  const w=Math.max(PANEL_W,Math.round(Number(vm.surfaceWidth)||PANEL_W));
  const h=Math.max(PANEL_H,Math.round(Number(vm.surfaceHeight)||PANEL_H));
  root.style.left=Math.max(0,Math.round((w-PANEL_W)/2))+'px';
  root.style.top=Math.max(0,Math.round((h-PANEL_H)/2))+'px';
}
function contentHeight(){
  const content=document.getElementById('inq-scroll-content');
  if(!content)return VIEWPORT_H;
  const cols=content.querySelectorAll('.inq-column');
  let max=VIEWPORT_H;
  for(let i=0;i<cols.length;i++)max=Math.max(max,Number(cols[i].scrollHeight)||Number(cols[i].offsetHeight)||0);
  return Math.max(VIEWPORT_H,max+40);
}
function maxScroll(){return Math.max(0,contentHeight()-VIEWPORT_H);}
function updateScrollbar(){
  const content=document.getElementById('inq-scroll-content');
  const bar=document.getElementById('inq-scrollbar');
  const thumb=document.getElementById('inq-scroll-thumb');
  if(!content||!bar||!thumb)return;
  const max=maxScroll();
  scrollY=Math.max(0,Math.min(max,scrollY));
  content.style.top=(-scrollY)+'px';
  const barH=Number(bar.clientHeight)||532;
  const total=VIEWPORT_H+max;
  const thumbH=max<=0?barH:Math.max(54,Math.round(barH*(VIEWPORT_H/total)));
  thumb.style.height=thumbH+'px';
  thumb.style.top=(max<=0?0:Math.round((barH-thumbH)*(scrollY/max)))+'px';
  bar.style.display=max<=0?'none':'block';
}
function scrollBy(delta){scrollY=Math.max(0,Math.min(maxScroll(),scrollY+delta));updateScrollbar();}
function wheelDelta(e){if(typeof e.deltaY==='number'&&e.deltaY!==0)return e.deltaY;if(typeof e.wheelDelta==='number'&&e.wheelDelta!==0)return e.wheelDelta;return 0;}
function sendSetting(key,value){try{const vm=model();if(vm&&typeof vm.onSet==='function')vm.onSet({key:key,value:value});}catch(e){console.error('WN8 setting update failed',e);}}
function closeWindow(){try{const vm=model();if(vm&&typeof vm.onClose==='function')vm.onClose({});}catch(e){}}
function optionLabel(key,value){const list=(state.options&&state.options[key])||[];for(let i=0;i<list.length;i++)if(String(list[i].value)===String(value))return String(list[i].label);return value==null?'':String(value);}
function renderToggle(el,value){el.classList.toggle('is-on',!!value);}
function closeSelects(except){
  document.querySelectorAll('.inq-select.is-open').forEach(function(el){
    if(el!==except){
      el.classList.remove('is-open');
      const row=el.closest('.inq-row');if(row)row.style.zIndex='';
      const section=el.closest('.inq-section');if(section)section.style.zIndex='';
    }
  });
}
function openSelect(select){
  closeSelects(select);
  select.classList.add('is-open');
  const row=select.closest('.inq-row');if(row)row.style.zIndex='120';
  const section=select.closest('.inq-section');if(section)section.style.zIndex='110';
}
function closeSelect(select){
  if(!select)return;
  select.classList.remove('is-open');
  const row=select.closest('.inq-row');if(row)row.style.zIndex='';
  const section=select.closest('.inq-section');if(section)section.style.zIndex='';
}
function renderSelect(el,key,value){
  const out=el.querySelector('.inq-select-value'),menu=el.querySelector('.inq-select-menu');if(out)out.textContent=optionLabel(key,value);if(!menu)return;
  menu.innerHTML='';const list=(state.options&&state.options[key])||[];
  list.forEach(function(item){
    const row=document.createElement('div');
    row.className='inq-option'+(String(item.value)===String(value)?' is-selected':'');
    row.setAttribute('data-value',String(item.value));
    const label=document.createElement('span');
    label.className='inq-option-text';
    label.textContent=String(item.label==null?'':item.label);
    row.appendChild(label);
    menu.appendChild(row);
  });
}
function sliderMeta(key){const m=(state.meta&&state.meta[key])||{};return {min:Number(m.minimum!=null?m.minimum:0),max:Number(m.maximum!=null?m.maximum:100),step:Number(m.step!=null?m.step:1)};}
function normalizeSlider(key,value){const m=sliderMeta(key);let v=Number(value);if(!isFinite(v))v=m.min;v=Math.max(m.min,Math.min(m.max,v));if(m.step>0)v=Math.round((v-m.min)/m.step)*m.step+m.min;return v;}
function sliderValueText(key,value){const v=Math.round(Number(value)||0);if(key==='panelHorizontalOffset'&&v>0)return '+'+String(v);return String(v);}
function renderSlider(el,key,value){const m=sliderMeta(key),v=normalizeSlider(key,value),ratio=m.max>m.min?(v-m.min)/(m.max-m.min):0;const fill=el.querySelector('.inq-slider-fill'),knob=el.querySelector('.inq-slider-knob');if(fill)fill.style.width=(ratio*100)+'%';if(knob)knob.style.left=(ratio*100)+'%';const out=document.querySelector('[data-value-for="'+key+'"]');if(out)out.textContent=sliderValueText(key,v);}
function updateDependencies(){const row=document.querySelector('[data-dependent="panelHorizontalOffset"]');if(row)row.classList.toggle('inq-hidden',!(state.meta&&state.meta.showPanelHorizontalOffset));setTimeout(updateScrollbar,0);}
function render(vm){
  if(!vm)return;
  centerPanel(vm);
  const raw=String(vm.payload||'{}');if(raw===lastPayload){updateScrollbar();return;}
  lastPayload=raw;state=parsePayload(raw);const settings=state.settings||{};
  applyTranslations();
  document.querySelectorAll('[data-control][data-setting]').forEach(function(el){const key=el.getAttribute('data-setting'),type=el.getAttribute('data-control');if(type==='toggle')renderToggle(el,settings[key]);else if(type==='select')renderSelect(el,key,settings[key]);else if(type==='slider')renderSlider(el,key,settings[key]);});
  updateDependencies();updateScrollbar();
}
function setLocal(key,value){state.settings=state.settings||{};state.settings[key]=value;}
function setSliderFromClientX(el,clientX,commit){const key=el.getAttribute('data-setting'),track=el.querySelector('.inq-slider-track');if(!track)return;const r=track.getBoundingClientRect(),ratio=Math.max(0,Math.min(1,(clientX-r.left)/Math.max(1,r.width))),m=sliderMeta(key),value=normalizeSlider(key,m.min+ratio*(m.max-m.min));setLocal(key,value);renderSlider(el,key,value);if(commit)sendSetting(key,value);}

document.addEventListener('click',function(e){
  const close=e.target&&e.target.closest?e.target.closest('[data-action="close"]'):null;if(close){closeWindow();return;}
  const toggle=e.target&&e.target.closest?e.target.closest('[data-control="toggle"]'):null;if(toggle){const key=toggle.getAttribute('data-setting'),value=!toggle.classList.contains('is-on');setLocal(key,value);renderToggle(toggle,value);sendSetting(key,value);return;}
  const option=e.target&&e.target.closest?e.target.closest('.inq-option'):null;if(option){const select=option.closest('.inq-select'),key=select.getAttribute('data-setting'),raw=option.getAttribute('data-value'),list=(state.options&&state.options[key])||[];let value=raw;for(let i=0;i<list.length;i++)if(String(list[i].value)===String(raw)){value=list[i].value;break;}setLocal(key,value);renderSelect(select,key,value);closeSelect(select);sendSetting(key,value);updateDependencies();return;}
  const select=e.target&&e.target.closest?e.target.closest('[data-control="select"]'):null;if(select){if(select.classList.contains('is-open'))closeSelect(select);else openSelect(select);return;}closeSelects(null);
});
document.addEventListener('wheel',function(e){
  const root=e.target&&e.target.closest?e.target.closest('.inq-shell'):null;if(!root)return;
  closeSelects(null);
  const d=wheelDelta(e);if(!d)return;
  scrollBy(d>0?-72:72);
  if(e.preventDefault)e.preventDefault();if(e.stopPropagation)e.stopPropagation();return false;
});
document.addEventListener('mousedown',function(e){
  const thumb=e.target&&e.target.closest?e.target.closest('#inq-scroll-thumb'):null;if(thumb){draggingScroll=true;scrollGrabY=e.clientY;scrollGrabTop=parseInt(thumb.style.top||'0',10)||0;e.preventDefault();return;}
  const slider=e.target&&e.target.closest?e.target.closest('[data-control="slider"]'):null;if(!slider)return;draggingSlider=slider;setSliderFromClientX(slider,e.clientX,false);e.preventDefault();
});
document.addEventListener('mousemove',function(e){
  if(draggingSlider)setSliderFromClientX(draggingSlider,e.clientX,false);
  if(draggingScroll){const bar=document.getElementById('inq-scrollbar'),thumb=document.getElementById('inq-scroll-thumb');if(!bar||!thumb)return;const barH=Number(bar.clientHeight)||532,thumbH=Number(thumb.clientHeight)||80,maxTop=Math.max(1,barH-thumbH),top=Math.max(0,Math.min(maxTop,scrollGrabTop+(e.clientY-scrollGrabY)));scrollY=(top/maxTop)*maxScroll();updateScrollbar();}
});
document.addEventListener('mouseup',function(e){if(draggingSlider){const slider=draggingSlider;draggingSlider=null;setSliderFromClientX(slider,e.clientX,true);}draggingScroll=false;});
document.addEventListener('keydown',function(e){if(e.key==='Escape'||e.keyCode===27)closeWindow();});

observer.onUpdate(render);
observer.subscribe();
render(observer.model);
setTimeout(updateScrollbar,0);
