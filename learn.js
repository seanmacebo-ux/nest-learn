// Nest Learn: menu, one-view-at-a-time switcher (anchorable by #hash), ✓ Done + checklist progress,
// library filters, and "Add a find" → Telegram. Progress lives on this phone (localStorage).
(() => {
  const KEY = 'learn_done';
  const get = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } };
  const put = v => { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} };

  // menu
  const btn = document.querySelector('.menubtn'), menu = document.getElementById('menu');
  const setMenu = open => { menu.hidden = !open; btn.setAttribute('aria-expanded', open); document.body.style.overflow = open ? 'hidden' : ''; };
  btn.addEventListener('click', () => setMenu(menu.hidden));
  menu.addEventListener('click', e => { if (e.target === menu || e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });

  // views: show one at a time, driven by the #hash so every view has its own link
  const tabs = [...document.querySelectorAll('.views a')], views = [...document.querySelectorAll('main .view[id]')];
  if (tabs.length) {
    document.body.classList.add('js-tabs');
    const show = id => {
      if (!views.some(v => v.id === id)) id = views[0].id;
      views.forEach(v => v.toggleAttribute('data-hide', v.id !== id));
      tabs.forEach(a => a.classList.toggle('on', a.dataset.v === id));
      const on = tabs.find(a => a.dataset.v === id); on && on.scrollIntoView({ block: 'nearest', inline: 'center' });
    };
    const fromHash = () => show(decodeURIComponent(location.hash.slice(1)));
    tabs.forEach(a => a.addEventListener('click', ev => {
      ev.preventDefault(); history.replaceState(null, '', '#' + a.dataset.v); show(a.dataset.v);
      window.scrollTo({ top: document.querySelector('.views').offsetTop - 60, behavior: 'smooth' });
    }));
    window.addEventListener('hashchange', fromHash);
    fromHash();
  }

  // ✓ Done on sources
  const paintRc = rc => {
    const on = !!get()[rc.dataset.rk];
    rc.classList.toggle('is-done', on);
    const b = rc.querySelector('.done'); b.textContent = on ? '✓ Done · undo' : '✓ Done'; b.setAttribute('aria-pressed', on);
  };
  document.querySelectorAll('.rc').forEach(rc => {
    paintRc(rc);
    rc.querySelector('.done').addEventListener('click', () => {
      const d = get(); d[rc.dataset.rk] ? delete d[rc.dataset.rk] : (d[rc.dataset.rk] = 1); put(d); paintRc(rc); progress();
    });
  });
  document.querySelectorAll('input[data-ck]').forEach(i => {
    i.checked = !!get()[i.dataset.ck];
    i.addEventListener('change', () => { const d = get(); i.checked ? (d[i.dataset.ck] = 1) : delete d[i.dataset.ck]; put(d); progress(); });
  });
  const progress = () => {
    const d = get();
    document.querySelectorAll('.tprog').forEach(p => {
      const t = p.dataset.track;
      const total = window.LEARN_TOTALS ? window.LEARN_TOTALS[t] : document.querySelectorAll('.rc, input[data-ck]').length;
      const done = Math.min(Object.keys(d).filter(k => k.startsWith(t + ':')).length, total);
      p.querySelector('.bar span').style.width = (total ? Math.round(100 * done / total) : 0) + '%';
      p.querySelector('.pc').textContent = done ? `${done} of ${total} done` : `${total} things to read, watch or do`;
    });
  };
  progress();

  // library filters
  const fb = [...document.querySelectorAll('.filt button')];
  fb.forEach(c => c.addEventListener('click', () => {
    fb.forEach(x => x.setAttribute('aria-pressed', x === c));
    document.querySelectorAll('.rc').forEach(rc => { rc.hidden = c.dataset.f !== 'all' && rc.dataset.type !== c.dataset.f; });
  }));

  // add a find → Telegram
  document.querySelectorAll('.addbox').forEach(box => {
    box.querySelectorAll('.qchips').forEach(g => g.addEventListener('click', ev => {
      const b = ev.target.closest('button'); if (!b) return;
      const on = b.getAttribute('aria-pressed') !== 'true';
      g.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', 'false'));
      b.setAttribute('aria-pressed', on);
    }));
    box.querySelector('.sendbtn').addEventListener('click', () => {
      const ta = box.querySelector('textarea'), txt = ta.value.trim();
      if (!txt) { ta.focus(); ta.placeholder = 'Paste a link or a name first 🙂'; return; }
      const tp = box.querySelector('.tpick [aria-pressed="true"]'), kb = box.querySelector('.kpick [aria-pressed="true"]');
      const t = box.dataset.track || (tp ? tp.dataset.t : 'Not sure which track');
      const msg = `📖 Nest Learn find\nTrack: ${t}${kb ? '\nType: ' + kb.textContent.trim() : ''}\n${txt}\n\nBreak it down and add it to Nest Learn please.`;
      try { navigator.clipboard && navigator.clipboard.writeText(msg).catch(() => {}); } catch (e) {}
      window.location.href = 'tg://resolve?domain=babybeanbot&text=' + encodeURIComponent(msg);
    });
  });
})();
