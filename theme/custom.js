(function () {
  const supportUrl = "https://www.buymeacoffee.com/YOUR_USERNAME";

  const link = document.createElement("a");
  link.href = supportUrl;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.className = "book-support-button";
  link.textContent = "☕ Support this book";
  document.body.appendChild(link);
})();
