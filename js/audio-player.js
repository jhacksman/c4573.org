/* c4573.org blog audio player.
 *
 * Self-initializing. Any page that contains a `.audio-player-wrapper` holding an
 * `<audio>` element gets a custom transport; the native `controls` chrome cannot be
 * re-laid-out, so it is removed and replaced here.
 *
 * Progressive enhancement: the markup ships `<audio controls>`, which is fully usable
 * with JS disabled. This script retires it and builds the custom bar, so there is never
 * dead UI — JS off means native controls, JS on means the custom transport.
 *
 * Reads nothing from inline attributes. No globals.
 */
(function () {
  'use strict';

  var RATES = [0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3];
  var DEFAULT_RATE = 1;
  var DEFAULT_VOLUME = 1;
  var SKIP = 10;
  var LS_RATE = 'c4573:audio:rate';
  var LS_VOLUME = 'c4573:audio:volume';

  var ICON_PLAY = '<svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true" focusable="false">' +
    '<path fill="currentColor" d="M4 2.5v11l9-5.5z"/></svg>';
  var ICON_PAUSE = '<svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true" focusable="false">' +
    '<path fill="currentColor" d="M3.5 2.5h3.2v11H3.5zM9.3 2.5h3.2v11H9.3z"/></svg>';
  var ICON_BACK = '<svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true" focusable="false">' +
    '<path fill="currentColor" d="M8.2 3.3V1L4 4.2l4.2 3.2V5.1a3.6 3.6 0 1 1-3.6 3.6H2.9a5.3 5.3 0 1 0 5.3-5.4z"/></svg>';
  var ICON_FWD = '<svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true" focusable="false">' +
    '<path fill="currentColor" d="M7.8 3.3V1L12 4.2 7.8 7.4V5.1a3.6 3.6 0 1 0 3.6 3.6h1.7a5.3 5.3 0 1 1-5.3-5.4z"/></svg>';
  var ICON_VOLUME = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false">' +
    '<path fill="currentColor" d="M8.3 1.8 4.6 4.9H1.8v6.2h2.8l3.7 3.1zM10.6 5.1a4 4 0 0 1 0 5.8l1.1 1.2a5.6 5.6 0 0 0 0-8.2z"/></svg>';

  /* ---------- small helpers ---------- */

  function el(tag, className, html) {
    var node = document.createElement(tag);
    if (className) { node.className = className; }
    if (html != null) { node.innerHTML = html; }
    return node;
  }

  function clamp(value, low, high) {
    return value < low ? low : (value > high ? high : value);
  }

  function readStore(key, fallback) {
    try {
      var raw = window.localStorage.getItem(key);
      if (raw === null) { return fallback; }
      var num = parseFloat(raw);
      return isFinite(num) ? num : fallback;
    } catch (err) {
      return fallback;
    }
  }

  function writeStore(key, value) {
    try {
      window.localStorage.setItem(key, String(value));
    } catch (err) { /* private mode / storage disabled: not fatal */ }
  }

  /* Formats seconds as M:SS, MM:SS or H:MM:SS. Unknown duration reads as --:--. */
  function formatTime(seconds) {
    if (seconds == null || !isFinite(seconds) || seconds < 0) { return '--:--'; }
    var total = Math.floor(seconds);
    var hrs = Math.floor(total / 3600);
    var mins = Math.floor((total % 3600) / 60);
    var secs = total % 60;
    var pad = secs < 10 ? '0' + secs : String(secs);
    if (hrs > 0) {
      return hrs + ':' + (mins < 10 ? '0' + mins : String(mins)) + ':' + pad;
    }
    return mins + ':' + pad;
  }

  /* Nearest option the <select> actually offers, so a stale stored rate still selects. */
  function nearestRate(rate) {
    var best = DEFAULT_RATE;
    var bestGap = Infinity;
    for (var i = 0; i < RATES.length; i++) {
      var gap = Math.abs(RATES[i] - rate);
      if (gap < bestGap) { bestGap = gap; best = RATES[i]; }
    }
    return best;
  }

  /* A range input over a painted track: real <input type=range> so arrow keys work,
   * with the visible track drawn by sibling divs (cross-browser, and lets the seek bar
   * show buffered and played ranges at once). */
  function buildRange(wrapClass, ariaLabel, withBuffered) {
    var wrap = el('div', 'ap-range-wrap ' + wrapClass);
    var track = el('div', 'ap-range-track');
    track.setAttribute('aria-hidden', 'true');
    var buffered = null;
    if (withBuffered) {
      buffered = el('div', 'ap-range-buffered');
      track.appendChild(buffered);
    }
    var fill = el('div', 'ap-range-fill');
    track.appendChild(fill);

    var input = document.createElement('input');
    input.type = 'range';
    input.className = 'ap-range';
    input.setAttribute('aria-label', ariaLabel);

    wrap.appendChild(track);
    wrap.appendChild(input);
    return { wrap: wrap, input: input, fill: fill, buffered: buffered };
  }

  /* ---------- player ---------- */

  function setupPlayer(wrapper) {
    var audio = wrapper.querySelector('audio');
    var card = wrapper.querySelector('.audio-player') || wrapper;
    if (!audio || card.classList.contains('ap-ready')) { return; }

    var uid = (audio.id || 'blogAudio') + '-' + Math.random().toString(36).slice(2, 8);

    /* Row 1: play, current time, seek (flex:1), duration, -10, +10, volume. */
    var transport = el('div', 'ap-transport');

    var playBtn = el('button', 'ap-btn ap-play', ICON_PLAY);
    playBtn.type = 'button';
    playBtn.setAttribute('aria-label', 'Play');

    var currentEl = el('span', 'ap-time ap-current', '0:00');
    var durationEl = el('span', 'ap-time ap-duration', '--:--');

    var seek = buildRange('ap-seek-wrap', 'Seek', true);
    seek.input.min = '0';
    seek.input.max = '0';
    seek.input.step = '1';
    seek.input.value = '0';
    seek.input.disabled = true;

    var backBtn = el('button', 'ap-btn ap-skip', ICON_BACK);
    backBtn.type = 'button';
    backBtn.setAttribute('aria-label', 'Back ' + SKIP + ' seconds');

    var fwdBtn = el('button', 'ap-btn ap-skip', ICON_FWD);
    fwdBtn.type = 'button';
    fwdBtn.setAttribute('aria-label', 'Forward ' + SKIP + ' seconds');

    var volIcon = el('span', 'ap-vol-icon', ICON_VOLUME);
    var vol = buildRange('ap-vol-wrap', 'Volume', false);
    vol.input.min = '0';
    vol.input.max = '1';
    vol.input.step = '0.05';

    transport.appendChild(playBtn);
    transport.appendChild(currentEl);
    transport.appendChild(seek.wrap);
    transport.appendChild(durationEl);
    transport.appendChild(backBtn);
    transport.appendChild(fwdBtn);
    transport.appendChild(volIcon);
    transport.appendChild(vol.wrap);

    /* Row 2: playback speed, right-aligned. */
    var rateRow = el('div', 'ap-rate-row');
    var rateLabel = el('label', 'ap-rate-label', 'Speed');
    rateLabel.setAttribute('for', uid + '-rate');
    var rateSelect = document.createElement('select');
    rateSelect.className = 'ap-rate';
    rateSelect.id = uid + '-rate';
    for (var i = 0; i < RATES.length; i++) {
      var option = document.createElement('option');
      option.value = String(RATES[i]);
      option.textContent = RATES[i] + '×';
      rateSelect.appendChild(option);
    }
    rateRow.appendChild(rateLabel);
    rateRow.appendChild(rateSelect);

    /* Stand the transport up before revealing it, so JS-off never sees a dead bar. */
    audio.removeAttribute('controls');
    card.appendChild(transport);
    card.appendChild(rateRow);
    card.classList.add('ap-ready');

    /* ---------- state ---------- */

    var storedRate = nearestRate(readStore(LS_RATE, DEFAULT_RATE));
    var storedVolume = clamp(readStore(LS_VOLUME, DEFAULT_VOLUME), 0, 1);
    var scrubbing = false;

    function applyRate() {
      audio.playbackRate = storedRate;
    }

    function duration() {
      var d = audio.duration;
      return (d != null && isFinite(d) && d > 0) ? d : 0;
    }

    function paintFill(range, ratio) {
      range.fill.style.width = (clamp(ratio, 0, 1) * 100).toFixed(3) + '%';
    }

    function paintBuffered() {
      var total = duration();
      if (!total || !seek.buffered) { return; }
      var end = 0;
      try {
        for (var b = 0; b < audio.buffered.length; b++) {
          if (audio.buffered.start(b) <= audio.currentTime + 0.5) {
            end = Math.max(end, audio.buffered.end(b));
          }
        }
      } catch (err) { return; }
      paintFill({ fill: seek.buffered }, end / total);
    }

    function paintTime() {
      var total = duration();
      currentEl.textContent = formatTime(audio.currentTime);
      if (total) {
        if (seek.input.disabled) { seek.input.disabled = false; }
        if (seek.input.max !== String(Math.floor(total))) {
          seek.input.max = String(Math.floor(total));
        }
        durationEl.textContent = formatTime(total);
        if (document.activeElement !== seek.input || !scrubbing) {
          seek.input.value = String(Math.min(audio.currentTime, total));
        }
        paintFill(seek, audio.currentTime / total);
      } else {
        durationEl.textContent = '--:--';
        paintFill(seek, 0);
      }
    }

    function paintVolume() {
      vol.input.value = String(audio.volume);
      paintFill(vol, audio.volume);
      vol.input.setAttribute('aria-valuetext', Math.round(audio.volume * 100) + '%');
    }

    function setPlayingIcon(playing) {
      playBtn.innerHTML = playing ? ICON_PAUSE : ICON_PLAY;
      playBtn.setAttribute('aria-label', playing ? 'Pause' : 'Play');
    }

    function skipBy(delta) {
      var total = duration();
      var limit = total || audio.currentTime;
      audio.currentTime = clamp(audio.currentTime + delta, 0, limit);
      paintTime();
    }

    function markUnavailable() {
      card.classList.add('ap-error');
      playBtn.disabled = true;
      backBtn.disabled = true;
      fwdBtn.disabled = true;
      seek.input.disabled = true;
      durationEl.textContent = '--:--';
      var label = card.querySelector('.audio-label');
      if (label && !label.dataset.apError) {
        label.dataset.apError = '1';
        label.textContent = label.textContent + ' — audio unavailable';
      }
    }

    /* ---------- wiring ---------- */

    playBtn.addEventListener('click', function () {
      if (audio.paused) {
        var started = audio.play();
        if (started && typeof started.catch === 'function') {
          started.catch(function () { /* autoplay policy or missing file */ });
        }
      } else {
        audio.pause();
      }
    });

    backBtn.addEventListener('click', function () { skipBy(-SKIP); });
    fwdBtn.addEventListener('click', function () { skipBy(SKIP); });

    seek.input.addEventListener('pointerdown', function () { scrubbing = true; });
    seek.input.addEventListener('pointerup', function () { scrubbing = false; });
    seek.input.addEventListener('keydown', function () { scrubbing = true; });
    seek.input.addEventListener('keyup', function () { scrubbing = false; });
    seek.input.addEventListener('input', function () {
      var total = duration();
      if (!total) { return; }
      audio.currentTime = clamp(parseFloat(seek.input.value) || 0, 0, total);
      currentEl.textContent = formatTime(audio.currentTime);
      paintFill(seek, audio.currentTime / total);
    });
    seek.input.addEventListener('change', function () { scrubbing = false; });

    vol.input.addEventListener('input', function () {
      var level = clamp(parseFloat(vol.input.value), 0, 1);
      audio.volume = level;
      audio.muted = level === 0;
      writeStore(LS_VOLUME, level);
      paintVolume();
    });

    rateSelect.addEventListener('change', function () {
      storedRate = nearestRate(parseFloat(rateSelect.value) || DEFAULT_RATE);
      applyRate();
      writeStore(LS_RATE, storedRate);
    });

    audio.addEventListener('play', function () { setPlayingIcon(true); applyRate(); });
    audio.addEventListener('pause', function () { setPlayingIcon(false); });
    audio.addEventListener('ended', function () { setPlayingIcon(false); });
    audio.addEventListener('timeupdate', paintTime);
    audio.addEventListener('seeked', paintTime);
    audio.addEventListener('loadedmetadata', function () { paintTime(); applyRate(); });
    audio.addEventListener('durationchange', paintTime);
    audio.addEventListener('progress', paintBuffered);
    audio.addEventListener('volumechange', paintVolume);
    audio.addEventListener('error', markUnavailable);
    if (audio.error) { markUnavailable(); }

    /* ---------- initial paint ---------- */

    rateSelect.value = String(storedRate);
    applyRate();
    audio.volume = storedVolume;
    paintVolume();
    paintTime();
    paintBuffered();
    setPlayingIcon(!audio.paused);

    /* Sticky header: unchanged behavior, toggles .stuck on the wrapper. */
    if (typeof window.IntersectionObserver === 'function') {
      var observer = new window.IntersectionObserver(
        function (entries) {
          wrapper.classList.toggle('stuck', entries[0].intersectionRatio < 1);
        },
        { threshold: [1], rootMargin: '-1px 0px 0px 0px' }
      );
      observer.observe(wrapper);
    }
  }

  function init() {
    var wrappers = document.querySelectorAll('.audio-player-wrapper');
    for (var i = 0; i < wrappers.length; i++) {
      setupPlayer(wrappers[i]);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
