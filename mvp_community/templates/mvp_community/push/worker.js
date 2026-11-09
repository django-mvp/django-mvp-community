self.addEventListener("push", (event) => {
  const message = event.data ? event.data.json() : {};
  event.waitUntil(
    self.registration.showNotification(message.title || "", {
      body: message.body || "",
      icon: message.icon,
      data: { url: message.url || "/" },
    }),
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = new URL(event.notification.data.url, self.location.origin);
  event.waitUntil(clients.openWindow(url.href));
});
