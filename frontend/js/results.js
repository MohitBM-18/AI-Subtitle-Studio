/* results.js – display final video and download link */
(function () {
  'use strict';

  const outputVideo  = sessionStorage.getItem('output_video');
  const downloadUrl  = sessionStorage.getItem('download_url');
  const detectedLang = sessionStorage.getItem('detected_language');

  if (!outputVideo || !downloadUrl) {
    document.querySelector('.results-card').innerHTML = `
      <p style="color:#ef4444;font-size:1.1rem;">
        No processed video found. 
        <a href="/upload.html" style="color:#a78bfa;">Start over</a>
      </p>`;
    return;
  }

  /* ── Set video source ── */
  const videoEl = document.getElementById('result-video');
  videoEl.src   = downloadUrl;
  videoEl.load();

  /* ── Set download link ── */
  const dlBtn = document.getElementById('download-btn');
  dlBtn.href  = downloadUrl;
  dlBtn.setAttribute('download', outputVideo);

  /* ── Meta info ── */
  const metaEl = document.getElementById('video-meta');
  if (detectedLang) {
    metaEl.textContent = `Detected language: ${detectedLang.toUpperCase()}`;
  }
})();
