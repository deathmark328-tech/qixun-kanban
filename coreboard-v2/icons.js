(function(){
'use strict';
// Clear, consistent pictograms for the therapist-requested AAC contrast pairs.
const ink='#213f47',blue='#568fc8',gold='#f7c450',green='#64b899',red='#e67967',grey='#f1f5f3';
function svg(s){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 96" role="img" aria-hidden="true" focusable="false"><g stroke="${ink}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">${s}</g></svg>`;}
function ball(x,y,c=gold,r=7){return `<circle cx="${x}" cy="${y}" r="${r}" fill="${c}"/>`;}
function bowl(full){let balls=full?[[38,44],[54,43],[70,43],[45,33],[62,31],[77,34]]:[[45,42],[64,42]];return svg(`${balls.map(x=>ball(...x)).join('')}<path d="M24 50 Q60 88 96 50 Z" fill="#f8e4b7"/><path d="M24 50 H96" fill="none"/>`)}
function compare(same){return svg(`<circle cx="36" cy="45" r="19" fill="${blue}"/>${same?`<circle cx="85" cy="45" r="19" fill="${blue}"/>`:`<path d="M85 24 L107 65 H63 Z" fill="${gold}"/>`}<path d="M19 77H105" stroke="#98b6ae" stroke-width="2"/>`)}
function size(focusBig){return svg(`<circle cx="37" cy="47" r="25" fill="${blue}"/><circle cx="88" cy="58" r="11" fill="${blue}"/><ellipse cx="${focusBig?37:88}" cy="${focusBig?47:58}" rx="${focusBig?31:17}" ry="${focusBig?31:17}" fill="none" stroke="${red}" stroke-width="5"/>`)}
function table(above){return svg(`<rect x="20" y="42" width="80" height="10" rx="3" fill="#f4c18a"/><path d="M30 52v31M90 52v31" fill="none"/>${ball(60,above?27:68,red,12)}`)}
function sock(dirty){return svg(`<path d="M46 12h28v44q0 8 8 10l11 6q6 3 3 11q-2 6-9 7H37q-14 0-16-12q-1-8 10-13l15-7z" fill="${dirty?'#d0b9a1':'#fff'}"/><path d="M46 25h28" fill="none"/>${dirty?`<path d="M27 72q11-13 20 1M58 62q9-9 18 0" stroke="#8c684d" fill="none"/><circle cx="77" cy="78" r="5" fill="#8c684d"/>`:`<path d="M80 10v-7M87 16l6-7M94 24l9-2" stroke="${gold}" fill="none"/>`}`)}
function boxes(){return svg(`<rect x="8" y="45" width="46" height="36" rx="3" fill="#f7d6a1"/><path d="M8 46L43 19L59 30L54 46" fill="#ffebc6"/><path d="M64 43h48v38H64z" fill="#f7d6a1"/><rect x="60" y="30" width="56" height="13" rx="2" fill="#ffebc6"/><path d="M60 89h57" stroke="${blue}" fill="none"/>`)}
function actionIcon(type){if(type==='get')return svg(`<rect x="13" y="25" width="36" height="39" rx="4" fill="#f5e2bd"/><path d="M55 45h36M80 33l12 12-12 12" fill="none" stroke="${blue}" stroke-width="7"/><path d="M86 70q11-15 24-3v16H69" fill="${green}"/>`);
if(type==='take')return svg(`<circle cx="31" cy="32" r="14" fill="${gold}"/><path d="M64 75V51q0-9 8-9t7 9V38q0-8 8-8t7 8v10q9-5 14 2t-3 15l-13 22H73z" fill="${green}"/><path d="M26 57L48 42M41 39l9 3-2 9" fill="none" stroke="${blue}"/>`);
if(type==='want')return svg(`<path d="M14 17h79q12 0 12 11v29q0 10-12 10H51L31 83V67H14q-8 0-8-10V29q0-12 8-12z" fill="#fff"/><path d="M56 55L37 38Q28 27 39 24Q49 21 56 33Q63 21 73 24Q84 27 75 38z" fill="${red}"/>`);
return svg(`<rect x="23" y="14" width="74" height="68" rx="6" fill="#fff"/><path d="M38 31h18m-18 19h18m-18 19h18" fill="none"/><path d="M67 25l8 7 16-17M67 47l8 7 16-17M66 67l8 7 16-17" fill="none" stroke="${green}" stroke-width="6"/>`);}
const icons={
 '0-7':bowl(true),'0-8':bowl(false),'3-8':compare(false),'5-9':compare(true),
 '2-9':size(true),'4-10':size(false),'6-7':table(true),'6-8':table(false),
 '2-10':sock(false),'3-9':sock(true),'4-2':boxes(),
 '1-4':actionIcon('do'),'2-4':actionIcon('get'),'6-0':actionIcon('take'),'6-3':actionIcon('want')
};
window.QixunIcons={render:function(id,fallback){return icons[id]||fallback},specialIds:Object.keys(icons)};
})();
