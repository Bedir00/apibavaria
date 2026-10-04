/**
 * API Bavaria motion layer.
 *
 * - Scroll reveals: matching elements below the fold fade and rise in when they enter
 *   the viewport, staggered among siblings. Elements already visible at load are left
 *   untouched so nothing flashes. Without JavaScript everything stays visible.
 * - Line drawing: outlined SVG icons inside revealed elements draw their strokes in.
 * - Honeycomb graphics (snippets/apibavaria-motion-hive.liquid) pause while off screen
 *   or while the tab is hidden.
 *
 * Respects `prefers-reduced-motion: reduce`. Re-initialises after theme editor section
 * re-renders. Configured through data attributes on its own script tag.
 */
(() => {
  const script = document.currentScript;
  const revealEnabled = script?.dataset.reveal !== 'false';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  const REVEAL_SELECTOR = [
    '[data-apb-reveal]',
    '.apbf-build-notice',
    '.apbf-heading',
    '.apbf-category',
    '.apbf-product',
    '.apbf-trust__brand',
    '.apbf-trust__item',
    '.apb-motion-banner__copy > *',
    '.product-grid__item',
  ].join(',');

  /** Revealed elements whose outlined SVG icons draw their strokes in. */
  const DRAW_SELECTOR = '[data-apb-draw], .apbf-trust__item';

  const STAGGER_MS = 80;
  const MAX_STAGGER_STEPS = 6;
  const CLEANUP_MS = 1900;

  /** @type {IntersectionObserver | undefined} */
  let revealObserver;
  /** @type {IntersectionObserver | undefined} */
  let hiveObserver;
  /** @type {Set<Element>} */
  const visibleHives = new Set();

  /** @param {Element} element */
  const finishReveal = (element) => {
    element.classList.remove('apb-reveal', 'is-revealed');
    if (element instanceof HTMLElement) element.style.removeProperty('--apb-reveal-delay');
  };

  /** @param {Element} element */
  const reveal = (element) => {
    element.classList.add('is-revealed');
    const delay = Number.parseInt(
      element instanceof HTMLElement ? element.style.getPropertyValue('--apb-reveal-delay') : '0',
      10
    );
    window.setTimeout(() => finishReveal(element), CLEANUP_MS + (Number.isNaN(delay) ? 0 : delay));
  };

  const getRevealObserver = () => {
    revealObserver ??= new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          revealObserver?.unobserve(entry.target);
          reveal(entry.target);
        }
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.12 }
    );
    return revealObserver;
  };

  /** @param {ParentNode} root */
  const initReveals = (root) => {
    if (!revealEnabled || reducedMotion.matches) return;

    const viewportBottom = window.innerHeight;
    /** @type {Map<Element | null, number>} */
    const siblingIndex = new Map();

    for (const element of root.querySelectorAll(REVEAL_SELECTOR)) {
      if (!(element instanceof HTMLElement) || element.dataset.apbRevealBound) continue;
      element.dataset.apbRevealBound = 'true';

      // Already on screen at load: keep it as rendered.
      if (element.getBoundingClientRect().top < viewportBottom) continue;

      const parent = element.parentElement;
      const index = siblingIndex.get(parent) ?? 0;
      siblingIndex.set(parent, index + 1);

      element.style.setProperty('--apb-reveal-delay', `${Math.min(index, MAX_STAGGER_STEPS) * STAGGER_MS}ms`);
      if (element.matches(DRAW_SELECTOR)) {
        for (const path of element.querySelectorAll('svg path')) {
          if (!path.hasAttribute('pathLength')) path.setAttribute('pathLength', '1');
        }
      }
      element.classList.add('apb-reveal');
      getRevealObserver().observe(element);
    }
  };

  const syncHivePlayback = () => {
    for (const hive of document.querySelectorAll('.apb-hive')) {
      const playing = visibleHives.has(hive) && !document.hidden && !reducedMotion.matches;
      hive.classList.toggle('is-paused', !playing);

      const svg = hive.querySelector('svg');
      if (!(svg instanceof SVGSVGElement)) continue;
      if (playing) svg.unpauseAnimations();
      else svg.pauseAnimations();
    }
  };

  /** @param {ParentNode} root */
  const initHives = (root) => {
    hiveObserver ??= new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) visibleHives.add(entry.target);
          else visibleHives.delete(entry.target);
        }
        syncHivePlayback();
      },
      { rootMargin: '80px 0px' }
    );

    for (const hive of root.querySelectorAll('.apb-hive')) {
      if (!(hive instanceof HTMLElement) || hive.dataset.apbHiveBound) continue;
      hive.dataset.apbHiveBound = 'true';
      hiveObserver.observe(hive);
    }
  };

  /** @param {ParentNode} root */
  const init = (root) => {
    initReveals(root);
    initHives(root);
  };

  init(document);

  document.addEventListener('visibilitychange', syncHivePlayback);

  reducedMotion.addEventListener('change', () => {
    if (reducedMotion.matches) {
      for (const element of document.querySelectorAll('.apb-reveal')) finishReveal(element);
      revealObserver?.disconnect();
    }
    syncHivePlayback();
  });

  document.addEventListener('shopify:section:load', (event) => {
    if (event.target instanceof Element) init(event.target);
  });

  document.addEventListener('shopify:section:unload', (event) => {
    if (!(event.target instanceof Element)) return;
    for (const hive of event.target.querySelectorAll('.apb-hive')) {
      hiveObserver?.unobserve(hive);
      visibleHives.delete(hive);
    }
  });
})();
