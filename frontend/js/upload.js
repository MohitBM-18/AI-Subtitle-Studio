/* upload.js – drag-and-drop upload with XHR progress */
(function () {
  'use strict';

  const dropZone  = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const idleView  = document.getElementById('drop-idle');
  const prevView  = document.getElementById('drop-preview');
  const videoEl   = document.getElementById('video-preview');
  const fileNameEl= document.getElementById('file-name');
  const fileSizeEl= document.getElementById('file-size');
  const changeBtn = document.getElementById('change-file');
  const progressW = document.getElementById('upload-progress-wrap');
  const progressB = document.getElementById('progress-bar');
  const progressP = document.getElementById('progress-pct');
  const errorEl   = document.getElementById('upload-error');
  const uploadBtn = document.getElementById('upload-btn');

  let selectedFile = null;

  /* ── File selection ── */
  fileInput.addEventListener('change', e => selectFile(e.target.files[0]));

  dropZone.addEventListener('click', () => {
    if (!selectedFile) fileInput.click();
  });
  dropZone.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') fileInput.click();
  });

  changeBtn.addEventListener('click', e => {
    e.stopPropagation();
    selectedFile = null;
    fileInput.value = '';
    idleView.classList.remove('hidden');
    prevView.classList.add('hidden');
    uploadBtn.disabled = true;
  });

  /* ── Drag & drop ── */
  ['dragenter','dragover'].forEach(evt =>
    dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.add('drag-over'); })
  );
  ['dragleave','drop'].forEach(evt =>
    dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.remove('drag-over'); })
  );
  dropZone.addEventListener('drop', e => {
    const f = e.dataTransfer.files[0];
    if (f) selectFile(f);
  });

  function selectFile(file) {
    if (!file) return;
    selectedFile = file;

    // Show preview
    const url = URL.createObjectURL(file);
    videoEl.src = url;
    fileNameEl.textContent = file.name;
    fileSizeEl.textContent = formatSize(file.size);
    idleView.classList.add('hidden');
    prevView.classList.remove('hidden');
    uploadBtn.disabled = false;
    hideError();
  }

  /* ── Upload ── */
  uploadBtn.addEventListener('click', () => {
    if (!selectedFile) return;
    doUpload(selectedFile);
  });

  function doUpload(file) {
    const form = new FormData();
    form.append('file', file);

    uploadBtn.disabled = true;
    progressW.classList.remove('hidden');
    hideError();

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/upload');

    xhr.upload.onprogress = e => {
      if (e.lengthComputable) {
        const pct = Math.round((e.loaded / e.total) * 100);
        progressB.style.width = pct + '%';
        progressP.textContent = pct + '%';
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText);
        sessionStorage.setItem('video_id', data.video_id);
        sessionStorage.setItem('original_filename', data.original_filename);
        window.location.href = '/editor.html';
      } else {
        const msg = tryParseError(xhr.responseText);
        showError('Upload failed: ' + msg);
        uploadBtn.disabled = false;
      }
    };

    xhr.onerror = () => {
      showError('Network error – could not reach the server.');
      uploadBtn.disabled = false;
    };

    xhr.send(form);
  }

  /* ── Helpers ── */
  function formatSize(bytes) {
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
  function showError(msg) {
    errorEl.textContent = msg;
    errorEl.classList.remove('hidden');
  }
  function hideError() { errorEl.classList.add('hidden'); }
  function tryParseError(text) {
    try { return JSON.parse(text).detail || text; } catch { return text; }
  }
})();
