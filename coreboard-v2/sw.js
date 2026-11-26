const CACHE = 'qixun-coreboard-v2-20261127-therapist-piper-2';
const FILES = ['./', './index.html', './manifest.webmanifest', './games/', './games/index.html', './icons.js', './print/qixun-coreboard-school-a3.pdf', '../icon-192.png', '../icon-512.png'];
const audioFiles = [
  ...Array.from({length:7},(_,r)=>Array.from({length:11},(_,c)=>'./audio/core/'+r+'-'+c+'.mp3')).flat(),
  ...'m1 m2 m3 m4 m5 s1 s2 s3 s4 s5 p1 p2 p3 p4 p5 e1 e2 e3 e4 e5'.split(' ').map(id=>'./audio/task/'+id+'.mp3'),
  ...'yes 1 2 3 4 5 no'.split(' ').map(id=>'./audio/number/'+id+'.mp3'),
  ...'my-turn your-turn go-wash dont-flush make-muffins too-big hello'.split(' ').map(id=>'./audio/phrase/'+id+'.mp3'),
  './audio/choice/0.mp3','./audio/choice/1.mp3', ...'write play brush snack tidy'.split(' ').map(id=>'./audio/first/'+id+'.mp3')
];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(async cache => {
    await cache.addAll(FILES);
    for(let i=0;i<audioFiles.length;i+=15)await cache.addAll(audioFiles.slice(i,i+15));
  }).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(names => Promise.all(names.filter(n => n.startsWith('qixun-coreboard-v2-') && n !== CACHE).map(n => caches.delete(n)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  // Online HTML prefers a fresh copy; installed iPads still work when offline.
  if(event.request.mode==='navigate') {
    event.respondWith(fetch(event.request).then(response=>{
      if(response.ok){const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(event.request,copy));}
      return response;
    }).catch(()=>caches.match(event.request).then(cached=>cached||caches.match('./index.html'))));
    return;
  }
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
    if (response.ok) { const clone = response.clone(); caches.open(CACHE).then(cache => cache.put(event.request, clone)); }
    return response;
  })));
});
