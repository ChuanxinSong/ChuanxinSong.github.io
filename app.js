/* Progressive enhancement: the full page is readable without JavaScript. */
(() => {
  const dialog = document.querySelector('#image-dialog');
  const fullImage = document.querySelector('#enlarged-image');
  let trigger;
  document.querySelectorAll('[data-image]').forEach(button => {
    button.addEventListener('click', () => {
      trigger = button;
      dialog.querySelector('.dialog-toolbar span').textContent = button.classList.contains('competition-photo') ? 'Competition photo' : 'Method overview';
      fullImage.src = button.dataset.image;
      fullImage.alt = button.dataset.caption;
      document.querySelector('#image-dialog-caption').textContent = button.dataset.caption;
      document.querySelector('#original-image').href = button.dataset.image;
      dialog.showModal();
      document.body.classList.add('dialog-open');
    });
  });
  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    const r = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('dialog-open');
    trigger?.focus();
  });

  const videoDialog = document.querySelector('#video-dialog');
  const fullVideo = videoDialog.querySelector('video');
  const videoError = videoDialog.querySelector('.dialog-video-error');
  let videoTrigger;
  document.querySelectorAll('[data-competition-video], [data-full-video]').forEach(anchor => {
    anchor.addEventListener('click', event => {
      event.preventDefault();
      videoTrigger = anchor;
      document.querySelector('#video-dialog-title').textContent = anchor.dataset.title;
      videoError.hidden = true;
      videoError.querySelector('a').href = anchor.href;
      fullVideo.src = anchor.href;
      fullVideo.loop = anchor.hasAttribute('data-full-video');
      fullVideo.muted = anchor.hasAttribute('data-full-video');
      videoDialog.showModal();
      document.body.classList.add('dialog-open');
      states.forEach(update);
      fullVideo.play().catch(() => {});
    });
  });
  fullVideo.addEventListener('error', () => { videoError.hidden = false; });
  videoDialog.querySelector('.dialog-close').addEventListener('click', () => videoDialog.close());
  videoDialog.addEventListener('click', event => {
    const r = videoDialog.getBoundingClientRect();
    if (event.target === videoDialog && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) videoDialog.close();
  });
  videoDialog.addEventListener('close', () => {
    fullVideo.pause();
    fullVideo.removeAttribute('src');
    fullVideo.load();
    document.body.classList.remove('dialog-open');
    videoTrigger?.focus();
    states.forEach(update);
  });

  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const states = [...document.querySelectorAll('video[data-src]')].map(video => ({
    video, button: video.closest('.video-preview').querySelector('.video-toggle'),
    visible: false, userPaused: false, manualPlay: false
  }));
  const ensureLoaded = video => {
    if (!video.getAttribute('src')) {
      video.src = video.dataset.src;
      video.load();
    }
  };
  const play = state => {
    ensureLoaded(state.video);
    state.video.muted = true;
    state.video.play().catch(() => {
      state.button.textContent = 'Play';
      state.button.setAttribute('aria-label', 'Play video preview');
    });
  };
  const update = state => {
    if (!document.hidden && !videoDialog.open && state.visible && !state.userPaused && (!reducedMotion.matches || state.manualPlay)) play(state);
    else state.video.pause();
  };
  states.forEach(state => {
    const { video, button } = state;
    video.addEventListener('play', () => {
      button.textContent = 'Pause'; button.setAttribute('aria-label', 'Pause video preview');
    });
    video.addEventListener('pause', () => {
      button.textContent = 'Play'; button.setAttribute('aria-label', 'Play video preview');
    });
    video.addEventListener('error', () => {
      video.closest('.video-preview').querySelector('.video-error').textContent = 'Preview unavailable. Please open the video or project directly.';
    });
    button.addEventListener('click', () => {
      if (video.paused) {
        state.userPaused = false; state.manualPlay = true; play(state);
      } else {
        state.userPaused = true; state.manualPlay = false; video.pause();
      }
    });
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const state = states.find(s => s.video === entry.target);
        state.visible = entry.isIntersecting && entry.intersectionRatio >= 0.25;
        update(state);
      });
    }, { threshold: [0, 0.25] });
    states.forEach(state => observer.observe(state.video));
  }
  document.addEventListener('visibilitychange', () => states.forEach(update));
  reducedMotion.addEventListener('change', () => {
    states.forEach(state => { state.manualPlay = false; update(state); });
  });
})();
