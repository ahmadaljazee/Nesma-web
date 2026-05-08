self.addEventListener('install', (e) => {
  console.log('Nesma Service Worker Installed');
});

self.addEventListener('fetch', (e) => {
  // هذا الجزء يسمح للتطبيق بطلب البيانات من السيرفر (رندر)
  e.respondWith(fetch(e.request));
});
