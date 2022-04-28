self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open('mellomlager').then( function (cache) {
            return cache.addAll([
                '../index.html',
		'css/gotstyle.css',
                './manifest.json',
                './mp5.js',
                'css/mp5.css',
                './mp5.html',
		'./response.dtd',
		'./diktbase.dtd',
                'http://localhost:8081/cgi-bin/api.cgi/Dikt/',
              ]);
        })
    );
});

self.addEventListener('fetch', function (event) {
    let online = navigator.onLine;
    if(!online){
    event.respondWith(
        caches.match(event.request)
    );
    }
});
