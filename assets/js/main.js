/* Younkwan Lee — homepage behaviour: theme toggle, mobile nav, publication
   filtering/search, BibTeX dialog, active-section highlighting. */
(function () {
  'use strict';

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ---------------------------------------------------------------- theme */
  var root = document.documentElement;
  var themeBtn = $('#theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var dark = root.getAttribute('data-theme') === 'dark';
      if (dark) { root.removeAttribute('data-theme'); } else { root.setAttribute('data-theme', 'dark'); }
      try { localStorage.setItem('theme', dark ? 'light' : 'dark'); } catch (e) { /* storage unavailable */ }
    });
  }

  /* ----------------------------------------------------------- mobile nav */
  var navToggle = $('#nav-toggle');
  var navLinks = $('#nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      var open = navLinks.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    $$('a', navLinks).forEach(function (a) {
      a.addEventListener('click', function () { navLinks.classList.remove('is-open'); navToggle.setAttribute('aria-expanded', 'false'); });
    });
  }

  /* ------------------------------------------------- publication filtering */
  var dialog = null;
  var pubs = $$('.pub');
  var groups = $$('.year-group');
  var filters = $$('.filter');
  var search = $('#pub-search');
  var empty = $('#pub-empty');
  var activeFilter = 'all';

  function applyFilters() {
    var q = (search && search.value || '').trim().toLowerCase();
    var terms = q ? q.split(/\s+/) : [];
    var shown = 0;
    pubs.forEach(function (p) {
      var okType = activeFilter === 'all' || p.dataset.type === activeFilter;
      var hay = p.dataset.search || '';
      var okSearch = terms.every(function (t) { return hay.indexOf(t) !== -1; });
      var visible = okType && okSearch;
      p.classList.toggle('is-hidden', !visible);
      if (visible) { shown++; }
    });
    groups.forEach(function (g) {
      var any = $$('.pub', g).some(function (p) { return !p.classList.contains('is-hidden'); });
      g.classList.toggle('is-hidden', !any);
    });
    if (empty) { empty.hidden = shown !== 0; }
    var emptyQ = $('#pub-empty-q');
    if (emptyQ) { emptyQ.textContent = q ? '"' + (search.value || '').trim() + '"' : 'the current filter'; }
    var countEl = $('#pub-count');
    if (countEl) {
      var label = activeFilter === 'all' ? 'publications' : activeFilter + ' papers';
      countEl.textContent = (shown === pubs.length ? 'Showing all ' : 'Showing ' + shown + ' of ') + pubs.length + ' ' + (shown === pubs.length ? 'publications' : label) + (q ? ' matching "' + (search.value || '').trim() + '"' : '');
    }
    var clearBtn = $('#pub-clear');
    if (clearBtn) { clearBtn.hidden = !q; }
  }

  filters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filters.forEach(function (b) { b.classList.remove('is-active'); });
      btn.classList.add('is-active');
      activeFilter = btn.dataset.filter;
      applyFilters();
    });
  });
  if (search) { search.addEventListener('input', applyFilters); }
  function resetSearch() {
    if (search) { search.value = ''; }
    filters.forEach(function (b) { b.classList.toggle('is-active', b.dataset.filter === 'all'); });
    activeFilter = 'all';
    applyFilters();
    if (search) { search.focus(); }
  }
  var clearBtn = $('#pub-clear');
  if (clearBtn) { clearBtn.addEventListener('click', function () { if (search) { search.value = ''; } applyFilters(); if (search) { search.focus(); } }); }
  var resetBtn = $('#pub-reset');
  if (resetBtn) { resetBtn.addEventListener('click', resetSearch); }
  // "/" focuses the publication search from anywhere on the page.
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && search && !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName) && !(dialog && dialog.open)) {
      e.preventDefault();
      search.scrollIntoView({ block: 'center' });
      search.focus();
    }
    if (e.key === 'Escape' && document.activeElement === search) { search.blur(); }
  });

  /* ------------------------------------------------------------- news */
  var newsToggle = $('#news-toggle');
  if (newsToggle) {
    var moreItems = $$('.news-more');
    var moreLabel = newsToggle.textContent;
    newsToggle.addEventListener('click', function () {
      var open = newsToggle.getAttribute('aria-expanded') === 'true';
      moreItems.forEach(function (li) { li.hidden = open; });
      newsToggle.setAttribute('aria-expanded', open ? 'false' : 'true');
      newsToggle.textContent = open ? moreLabel : 'Show less';
    });
  }

  /* ---------------------------------------------------------- back to top */
  var toTop = $('#to-top');
  if (toTop) {
    var onScroll = function () { toTop.classList.toggle('is-visible', window.scrollY > 700); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* -------------------------------------------------------- cite dialog */
  dialog = $('#cite-dialog');
  var citeText = $('#cite-text');
  var citePaper = $('#cite-paper');
  var copyBtn = $('#cite-copy');
  var closeBtn = $('#cite-close');

  function openCite(bibId, title) {
    var src = document.getElementById(bibId);
    if (!src || !dialog) { return; }
    citeText.textContent = src.textContent;
    citePaper.textContent = title || '';
    if (copyBtn) { copyBtn.querySelector('span').textContent = 'Copy BibTeX'; }
    if (typeof dialog.showModal === 'function') { dialog.showModal(); } else { dialog.setAttribute('open', ''); }
  }
  function closeCite() { if (!dialog) { return; } if (typeof dialog.close === 'function') { dialog.close(); } else { dialog.removeAttribute('open'); } }

  $$('.btn-cite').forEach(function (b) {
    b.addEventListener('click', function () { openCite(b.dataset.bib, b.dataset.title); });
  });
  if (closeBtn) { closeBtn.addEventListener('click', closeCite); }
  if (dialog) {
    dialog.addEventListener('click', function (e) { if (e.target === dialog) { closeCite(); } });
  }
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      var text = citeText.textContent;
      var done = function () { copyBtn.querySelector('span').textContent = 'Copied!'; setTimeout(function () { copyBtn.querySelector('span').textContent = 'Copy BibTeX'; }, 1600); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text); done(); });
      } else { fallbackCopy(text); done(); }
    });
  }
  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e) { /* ignore */ }
    document.body.removeChild(ta);
  }

  /* --------------------------------------------- active nav highlighting */
  var sections = $$('main section[id]');
  var links = $$('.nav-links a[href^="#"]');
  if ('IntersectionObserver' in window && sections.length && links.length) {
    var current = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { current = en.target.id; }
      });
      links.forEach(function (a) { a.classList.toggle('is-active', a.getAttribute('href') === '#' + current); });
    }, { rootMargin: '-25% 0px -65% 0px', threshold: 0 });
    sections.forEach(function (s) { io.observe(s); });
  }
})();
