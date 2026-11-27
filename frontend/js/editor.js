/* editor.js – subtitle configuration, live preview & job submission */
(function () {
  'use strict';

  const videoId  = sessionStorage.getItem('video_id');
  if (!videoId) { window.location.href = '/upload.html'; return; }

  /* ── State ── */
  let subtitleMode  = 'sentence';   // 'sentence' | 'karaoke'
  let outputType    = 'original';   // 'original' | 'translated' | 'both'
  let segments      = [];           // transcription segments from server
  let activeSegIdx  = -1;
  let karaokeTimer  = null;

  /* ── DOM refs ── */
  const detectedLang  = document.getElementById('detected-lang');
  const previewVideo  = document.getElementById('preview-video');
  const subtitleOver  = document.getElementById('subtitle-overlay');
  const transcriptList= document.getElementById('transcript-list');
  const procBtn       = document.getElementById('process-btn');
  const outputSel     = document.getElementById('output-type');
  const targetLangRow = document.getElementById('translation-row');
  const targetLangSel = document.getElementById('target-lang');
  const resolutionSel = document.getElementById('resolution');
  const fontSizeIn    = document.getElementById('font-size');
  const fontSizeVal   = document.getElementById('font-size-val');
  const textColorIn   = document.getElementById('text-color');
  const hlColorIn     = document.getElementById('highlight-color');
  const bgColorIn     = document.getElementById('bg-color');
  const bgOpacIn      = document.getElementById('bg-opacity');
  const bgOpacVal     = document.getElementById('bg-opacity-val');
  const positionSel   = document.getElementById('position');

  /* ── Load video into preview ── */
  previewVideo.src = '';  // no original video preview without server endpoint

  /* ── Mode toggles ── */
  document.getElementById('btn-sentence').addEventListener('click', () => setMode('sentence'));
  document.getElementById('btn-karaoke').addEventListener('click',  () => setMode('karaoke'));

  function setMode(m) {
    subtitleMode = m;
    document.getElementById('btn-sentence').classList.toggle('active', m === 'sentence');
    document.getElementById('btn-karaoke').classList.toggle('active',  m === 'karaoke');
  }

  /* ── Output type ── */
  outputSel.addEventListener('change', () => {
    outputType = outputSel.value;
    targetLangRow.classList.toggle('hidden', outputType === 'original');
  });

  /* ── Style inputs ── */
  fontSizeIn.addEventListener('input', () => {
    fontSizeVal.textContent = fontSizeIn.value + 'px';
    applyStyle();
  });
  bgOpacIn.addEventListener('input', () => {
    bgOpacVal.textContent = bgOpacIn.value + '%';
    applyStyle();
  });
  [textColorIn, hlColorIn, bgColorIn, positionSel].forEach(el =>
    el.addEventListener('change', applyStyle)
  );

  function applyStyle() {
    const fs = fontSizeIn.value;
    const tc = textColorIn.value;
    const bc = hexToRgba(bgColorIn.value, bgOpacIn.value / 100);
    subtitleOver.style.fontSize       = fs + 'px';
    subtitleOver.style.color          = tc;
    subtitleOver.style.background     = bc;
    const pos = positionSel.value;
    subtitleOver.style.bottom = pos === 'top'    ? 'auto' : (pos === 'middle' ? '45%' : '10%');
    subtitleOver.style.top    = pos === 'top'    ? '5%'   : 'auto';
  }

  /* ── Presets ── */
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      applyPreset(btn.dataset.preset);
    });
  });

  const PRESETS = {
    youtube:    { fontSize: 28, textColor: '#ffffff', bgColor: '#000000', bgOpacity: 70 },
    instagram:  { fontSize: 32, textColor: '#ffcc00', bgColor: '#000000', bgOpacity: 80 },
    tiktok:     { fontSize: 34, textColor: '#ffffff', bgColor: '#ff2d55', bgOpacity: 85 },
    cinematic:  { fontSize: 24, textColor: '#e8e8e8', bgColor: '#000000', bgOpacity: 0  },
    corporate:  { fontSize: 26, textColor: '#ffffff', bgColor: '#003366', bgOpacity: 90 },
    karaoke:    { fontSize: 36, textColor: '#ffffff', bgColor: '#000000', bgOpacity: 75 },
  };

  function applyPreset(name) {
    const p = PRESETS[name]; if (!p) return;
    fontSizeIn.value  = p.fontSize;   fontSizeVal.textContent = p.fontSize + 'px';
    textColorIn.value = p.textColor;
    bgColorIn.value   = p.bgColor;
    bgOpacIn.value    = p.bgOpacity;  bgOpacVal.textContent = p.bgOpacity + '%';
    applyStyle();
  }

  /* ── Subtitle overlay during preview ── */
  previewVideo.addEventListener('timeupdate', onTimeUpdate);

  function onTimeUpdate() {
    const t = previewVideo.currentTime;
    if (!segments.length) return;

    if (subtitleMode === 'sentence') {
      const seg = segments.find(s => t >= s.start && t <= s.end);
      subtitleOver.textContent = seg ? seg.text : '';
    } else {
      // Karaoke – find current word
      let found = '';
      for (const seg of segments) {
        if (!seg.words) continue;
        for (const w of seg.words) {
          if (t >= w.start && t <= w.end) { found = w.word; break; }
        }
        if (found) break;
      }
      subtitleOver.textContent = found;
    }
  }

  /* ── Render transcript list ── */
  function renderTranscript() {
    transcriptList.innerHTML = '';
    segments.forEach((seg, i) => {
      const div = document.createElement('div');
      div.className = 'segment-item';
      div.dataset.idx = i;
      div.innerHTML = `
        <span class="segment-time">${fmtTime(seg.start)}</span>
        <span class="segment-text" contenteditable="true">${seg.text}</span>
      `;
      div.querySelector('.segment-text').addEventListener('blur', e => {
        segments[i].text = e.target.textContent.trim();
      });
      transcriptList.appendChild(div);
    });
  }

  /* ── Load transcription on page load (if already done) ── */
  async function loadTranscription() {
    detectedLang.textContent = 'Processing transcription…';
    try {
      const r = await fetch(`/api/transcribe/${encodeURIComponent(videoId)}?style=${subtitleMode}`, { method: 'POST' });
      if (!r.ok) throw new Error(await r.text());
      const data = await r.json();
      segments = data.segments || [];
      detectedLang.textContent = (data.language || 'Unknown').toUpperCase();
      renderTranscript();
    } catch (e) {
      detectedLang.textContent = 'Detection failed';
      console.error(e);
    }
  }

  loadTranscription();

  /* ── Process button ── */
  procBtn.addEventListener('click', async () => {
    procBtn.disabled = true;
    procBtn.textContent = 'Starting…';

    const style      = subtitleMode;
    const targetLang = outputType !== 'original' ? targetLangSel.value : null;
    const resolution = resolutionSel.value;

    // Build query string
    let url = `/api/jobs/process?video_id=${encodeURIComponent(videoId)}&style=${style}&resolution=${resolution}`;
    if (targetLang) url += `&target_lang=${encodeURIComponent(targetLang)}`;

    try {
      const r    = await fetch(url, { method: 'POST' });
      const data = await r.json();
      sessionStorage.setItem('job_id', data.job_id);
      window.location.href = '/processing.html';
    } catch (e) {
      procBtn.disabled = false;
      procBtn.textContent = '🚀 Process Video';
      alert('Failed to start processing: ' + e.message);
    }
  });

  /* ── Helpers ── */
  function fmtTime(s) {
    const m = Math.floor(s / 60);
    const sec = (s % 60).toFixed(1);
    return `${m}:${sec.padStart(4,'0')}`;
  }
  function hexToRgba(hex, opacity) {
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    return `rgba(${r},${g},${b},${opacity})`;
  }
})();
