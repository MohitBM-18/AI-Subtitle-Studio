/* processing.js – polls job status and drives the stage checklist */
(function () {
  'use strict';

  const jobId = sessionStorage.getItem('job_id');
  if (!jobId) { window.location.href = '/upload.html'; return; }

  /* ── Stage map ── */
  const STAGE_ELS = {
    'Extracting audio':    document.getElementById('st-audio'),
    'Transcribing speech': document.getElementById('st-transcribe'),
    'Generating subtitles':document.getElementById('st-timestamps'),
    'Rendering video':     document.getElementById('st-render'),
    'Complete':            document.getElementById('st-finalise'),
  };

  // Mark the first stage done immediately
  markDone(document.getElementById('st-upload'));

  const procBar   = document.getElementById('proc-bar');
  const procPct   = document.getElementById('proc-pct');
  const procStage = document.getElementById('proc-stage');
  const procIcon  = document.getElementById('proc-icon');
  const procTitle = document.getElementById('proc-title');
  const procError = document.getElementById('proc-error');
  const cancelBtn = document.getElementById('cancel-btn');

  /* ── Polling ── */
  let previousStage = null;
  const POLL_MS = 2000;

  async function poll() {
    try {
      const r    = await fetch(`/api/jobs/${encodeURIComponent(jobId)}`);
      const data = await r.json();

      // Update progress bar
      procBar.style.width = (data.progress || 0) + '%';
      procPct.textContent = (data.progress || 0) + '%';

      // Update stage label
      if (data.stage) {
        procStage.textContent = data.stage;

        // Mark stages done in order
        if (data.stage !== previousStage) {
          const el = STAGE_ELS[data.stage];
          if (el) {
            // Mark all previous stages done
            Object.values(STAGE_ELS).forEach(e => {
              if (e && !e.classList.contains('done') && e !== el) {
                // only mark done if visually before current
              }
            });
            markActive(el);
          }
          if (previousStage && STAGE_ELS[previousStage]) {
            markDone(STAGE_ELS[previousStage]);
          }
          previousStage = data.stage;
        }
      }

      /* ── Terminal states ── */
      if (data.status === 'done') {
        // Mark all stages done
        Object.values(STAGE_ELS).forEach(e => e && markDone(e));
        procIcon.textContent = '🎉';
        procTitle.textContent = 'Video is Ready!';
        procStage.textContent = 'Processing complete.';
        procBar.style.width = '100%';
        procPct.textContent = '100%';
        if (data.result) {
          sessionStorage.setItem('output_video', data.result.output_video);
          sessionStorage.setItem('download_url', data.result.download_url);
          sessionStorage.setItem('detected_language', data.result.language || '');
        }
        setTimeout(() => { window.location.href = '/results.html'; }, 1200);
        return; // stop polling
      }

      if (data.status === 'failed') {
        procIcon.textContent = '❌';
        procTitle.textContent = 'Processing Failed';
        procError.textContent = data.error || 'An unknown error occurred.';
        procError.classList.remove('hidden');
        return; // stop polling
      }

      // Keep polling
      setTimeout(poll, POLL_MS);

    } catch (err) {
      procError.textContent = 'Could not reach the server: ' + err.message;
      procError.classList.remove('hidden');
    }
  }

  /* ── Cancel ── */
  cancelBtn.addEventListener('click', async () => {
    try {
      await fetch(`/api/jobs/${encodeURIComponent(jobId)}`, { method: 'DELETE' });
    } catch {}
    window.location.href = '/upload.html';
  });

  /* ── Helpers ── */
  function markDone(el)   { if (el) { el.classList.remove('active','error'); el.classList.add('done'); } }
  function markActive(el) { if (el) { el.classList.remove('done','error');   el.classList.add('active'); } }

  // Start polling
  poll();
})();
