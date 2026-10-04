/**
 * API Bavaria offers: quantity tiers, accessory sets and the add-to-cart pop-up.
 *
 * Offer data per product is rendered by snippets/apibavaria-offer-data.liquid as
 * <script type="application/json" data-apb-offer="<product id>">.
 *
 * Discounts are calculated by Shopify, never here:
 * - quantity tiers: automatic discounts per collection (mix & match),
 * - sets: discount codes APB-SET10-<id> / APB-SET15-<id>, applied in the background
 *   through /cart/update.js when the customer adds a set.
 *
 * Pop-up flow: when a product with an offer is added to the cart, the cart drawer's
 * auto-open is held back for that add, the pop-up shows the offer, and the drawer opens
 * once the pop-up closes. Each product shows the pop-up at most once per session.
 */
import { StandardEvents, CartLinesUpdateEvent } from '@shopify/events';
import { formatMoney } from '@theme/money-formatting';

const SEEN_KEY = 'apb-offer-seen';

/** True while this module dispatches its own cart events, so the pop-up ignores them. */
let dispatchingOwnEvent = false;

/* -------------------------------------------------------------------------- */
/* Helpers                                                                     */
/* -------------------------------------------------------------------------- */

/**
 * @param {string | number} productId
 * @returns {any | null}
 */
function readOffer(productId) {
  const element = document.querySelector(`script[data-apb-offer="${productId}"]`);
  if (!element?.textContent) return null;
  try {
    return JSON.parse(element.textContent);
  } catch {
    return null;
  }
}

/**
 * @param {number} cents
 * @param {any} offer
 */
function money(cents, offer) {
  return formatMoney(Math.round(cents), offer.moneyFormat || '{{amount_with_comma_separator}} €', offer.currency || 'EUR');
}

/** @param {unknown} value */
function escapeHtml(value) {
  return String(value ?? '').replace(
    /[&<>"']/g,
    (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character] ?? character
  );
}

/** @param {number} cents @param {number} percent */
function discounted(cents, percent) {
  return Math.round((cents * (100 - percent)) / 100);
}

function readSeen() {
  try {
    return new Set(JSON.parse(sessionStorage.getItem(SEEN_KEY) || '[]'));
  } catch {
    return new Set();
  }
}

/** @param {string | number} productId */
function markSeen(productId) {
  try {
    const seen = readSeen();
    seen.add(String(productId));
    sessionStorage.setItem(SEEN_KEY, JSON.stringify([...seen]));
  } catch {
    /* Storage unavailable: the pop-up may show again, which is acceptable. */
  }
}

/** @param {string | number} productId */
function hasSeen(productId) {
  return readSeen().has(String(productId));
}

function cartSectionIds() {
  return [...document.querySelectorAll('cart-items-component')]
    .map((element) => (element instanceof HTMLElement ? element.dataset.sectionId : ''))
    .filter(Boolean);
}

/**
 * @param {string} url
 * @param {Record<string, unknown>} body
 */
async function postCart(url, body) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok || data.status) {
    throw new Error(data.description || data.message || 'Der Warenkorb konnte nicht aktualisiert werden.');
  }
  return data;
}

async function getCart() {
  const response = await fetch(`${Theme.routes.cart_url}.js`, {
    headers: { Accept: 'application/json' },
    credentials: 'same-origin',
  });
  if (!response.ok) throw new Error(`Warenkorb nicht erreichbar (${response.status})`);
  return response.json();
}

/** @param {any} cart */
function cartDiscountCodes(cart) {
  return Array.isArray(cart?.discount_codes) ? cart.discount_codes.map((entry) => entry.code).filter(Boolean) : [];
}

/**
 * @param {any} cart
 * @param {number[]} productIds
 */
function quantityInCart(cart, productIds) {
  const ids = new Set(productIds.map(Number));
  return (cart?.items ?? []).reduce((sum, item) => (ids.has(Number(item.product_id)) ? sum + item.quantity : sum), 0);
}

/**
 * @param {any} cart
 * @param {number} productId
 */
function inCart(cart, productId) {
  return (cart?.items ?? []).some((item) => Number(item.product_id) === Number(productId));
}

function cartDrawerComponent() {
  return document.querySelector('cart-drawer-component');
}

function openCartDrawer() {
  const drawer = /** @type {any} */ (document.querySelector('theme-drawer#cart-drawer'));
  drawer?.open?.();
}

/**
 * Runs `callback` while the cart drawer's auto-open is switched off, so cart events
 * dispatched inside it don't open the drawer.
 * @template T
 * @param {() => T} callback
 * @returns {T}
 */
function withoutDrawerAutoOpen(callback) {
  const component = cartDrawerComponent();
  const hadAutoOpen = component?.hasAttribute('auto-open');
  if (hadAutoOpen) component?.removeAttribute('auto-open');
  try {
    return callback();
  } finally {
    if (hadAutoOpen) setTimeout(() => component?.setAttribute('auto-open', ''), 0);
  }
}

/**
 * Tells the theme (cart drawer, cart count, cart page) that lines were added.
 * @param {EventTarget} source
 * @param {Array<{variantId: number, quantity: number}>} lines
 * @param {any} cart - Full cart JSON after the change
 * @param {Record<string, string> | undefined} sections
 */
function announceCartAdd(source, lines, cart, sections) {
  const deferred = CartLinesUpdateEvent.createPromise();
  dispatchingOwnEvent = true;
  try {
    source.dispatchEvent(
      new CartLinesUpdateEvent({
        action: 'add',
        context: 'product',
        lines: lines.map((line) => ({ merchandiseId: String(line.variantId), quantity: line.quantity })),
        promise: deferred.promise,
      })
    );
  } finally {
    dispatchingOwnEvent = false;
  }
  deferred.resolve({
    cart: CartLinesUpdateEvent.createCartFromAjaxResponse(cart),
    detail: { sections, items: cart.items, didError: false, source: 'apb-offers' },
  });
}

/**
 * Adds items and optionally applies the set code. Returns the final cart and whether
 * the code was accepted.
 * @param {Array<{variantId: number, quantity: number}>} lines
 * @param {{ add?: string, remove?: string[] }} [codes]
 */
async function addToCart(lines, codes = {}) {
  const sections = cartSectionIds();
  const items = lines.map((line) => ({ id: line.variantId, quantity: line.quantity }));

  if (!codes.add) {
    const added = await postCart(Theme.routes.cart_add_url, {
      items,
      sections: sections.join(','),
      sections_url: window.location.pathname,
    });
    const cart = await getCart();
    return { cart, sections: added.sections, codeAccepted: true };
  }

  await postCart(Theme.routes.cart_add_url, { items });
  const before = await getCart();
  const remove = new Set((codes.remove ?? []).map((code) => code.toUpperCase()));
  const nextCodes = cartDiscountCodes(before).filter((code) => !remove.has(code.toUpperCase()));
  if (!nextCodes.some((code) => code.toUpperCase() === codes.add?.toUpperCase())) nextCodes.push(codes.add);

  const cart = await postCart(`${Theme.routes.cart_update_url}.js`, {
    discount: nextCodes.join(','),
    sections: sections.join(','),
    sections_url: window.location.pathname,
  });
  const applied = (cart.discount_codes ?? []).find(
    (/** @type {any} */ entry) => entry.code?.toUpperCase() === codes.add?.toUpperCase()
  );
  return { cart, sections: cart.sections, codeAccepted: applied ? applied.applicable !== false : true };
}

/**
 * Picks the set code for the partners now in the cart.
 * @param {any} offer
 * @param {any} cart
 */
function setCodesFor(offer, cart) {
  const partnersInCart = offer.bundle.partners.filter((/** @type {any} */ partner) => inCart(cart, partner.productId));
  const both = partnersInCart.length >= 2;
  return {
    add: both ? offer.bundle.codeTwo : offer.bundle.codeOne,
    remove: [both ? offer.bundle.codeOne : offer.bundle.codeTwo],
    percent: both ? offer.bundle.percentTwo : offer.bundle.percentOne,
  };
}

/* -------------------------------------------------------------------------- */
/* PDP: quantity tiers                                                         */
/* -------------------------------------------------------------------------- */

class OfferTiers extends HTMLElement {
  #abort = new AbortController();

  connectedCallback() {
    const { signal } = this.#abort;
    this.addEventListener('click', this.#onClick, { signal });
    document.addEventListener('quantity-selector:update', this.#sync, { signal });
    this.#quantityInput()?.addEventListener('input', this.#sync, { signal });
    this.#quantityInput()?.addEventListener('change', this.#sync, { signal });
    this.#sync();
  }

  disconnectedCallback() {
    this.#abort.abort();
    this.#abort = new AbortController();
  }

  #quantitySelector() {
    const scope = this.closest('.product-details, product-form-component, section') ?? document;
    return /** @type {any} */ (scope.querySelector('quantity-selector-component'));
  }

  #quantityInput() {
    return /** @type {HTMLInputElement | null} */ (this.#quantitySelector()?.querySelector('input[name="quantity"], input'));
  }

  /** @param {MouseEvent} event */
  #onClick = (event) => {
    const tier = event.target instanceof Element ? event.target.closest('[data-quantity]') : null;
    if (!(tier instanceof HTMLElement)) return;

    const quantity = tier.dataset.quantity ?? '1';
    const selector = this.#quantitySelector();
    if (selector?.setValue) {
      selector.setValue(quantity);
      selector.updateButtonStates?.();
      selector.onQuantityChange?.();
    } else {
      const input = this.#quantityInput();
      if (input) {
        input.value = quantity;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    this.#sync();
  };

  #sync = () => {
    const value = Number.parseInt(this.#quantityInput()?.value ?? '1', 10) || 1;
    const tiers = [...this.querySelectorAll('[data-quantity]')];
    const highest = Math.max(...tiers.map((tier) => Number(tier.getAttribute('data-quantity'))));
    for (const tier of tiers) {
      const tierQuantity = Number(tier.getAttribute('data-quantity'));
      const active = tierQuantity === Math.min(value, highest);
      tier.setAttribute('aria-checked', String(active));
      tier.setAttribute('tabindex', active ? '0' : '-1');
    }
  };
}

/* -------------------------------------------------------------------------- */
/* PDP: accessory set                                                          */
/* -------------------------------------------------------------------------- */

class OfferSet extends HTMLElement {
  #abort = new AbortController();

  connectedCallback() {
    const { signal } = this.#abort;
    this.addEventListener('change', this.#render, { signal });
    this.querySelector('[data-apb-set-add]')?.addEventListener('click', this.#onAdd, { signal });
    this.#render();
  }

  disconnectedCallback() {
    this.#abort.abort();
    this.#abort = new AbortController();
  }

  get #offer() {
    return readOffer(this.dataset.productId ?? '');
  }

  #selectedPartners() {
    return /** @type {HTMLInputElement[]} */ ([...this.querySelectorAll('.api-offer__set-input:checked')]);
  }

  #mainVariantId() {
    const form = document.querySelector(`product-form-component[data-product-id="${this.dataset.productId}"]`);
    const input = /** @type {HTMLInputElement | null} */ (form?.querySelector('input[name="id"]'));
    return Number(input?.value) || Number(this.#offer?.variantId);
  }

  #render = () => {
    const offer = this.#offer;
    if (!offer?.bundle) return;

    const selected = this.#selectedPartners();
    const percent = selected.length >= 2 ? offer.bundle.percentTwo : selected.length === 1 ? offer.bundle.percentOne : 0;
    // Rounded per item, like Shopify allocates the discount per cart line.
    const partnerTotal = selected.reduce((sum, input) => sum + Number(input.dataset.price || 0), 0);
    const partnerDiscounted = selected.reduce((sum, input) => sum + discounted(Number(input.dataset.price || 0), percent), 0);
    const full = offer.price + partnerTotal;
    const total = offer.price + partnerDiscounted;

    const fullElement = this.querySelector('[data-apb-set-full]');
    const totalElement = this.querySelector('[data-apb-set-total]');
    const savingElement = this.querySelector('[data-apb-set-saving]');
    const button = this.querySelector('[data-apb-set-add]');

    if (fullElement) {
      fullElement.textContent = money(full, offer);
      fullElement.toggleAttribute('hidden', percent === 0);
    }
    if (totalElement) totalElement.textContent = money(total, offer);
    if (savingElement) {
      savingElement.textContent = percent > 0 ? `Du sparst ${money(full - total, offer)} (−${percent} % aufs Zubehör)` : '';
    }
    if (button) {
      button.textContent = selected.length > 0 ? `Set in den Warenkorb – ${money(total, offer)}` : 'In den Warenkorb';
    }
  };

  /** @param {MouseEvent} event */
  #onAdd = async (event) => {
    const offer = this.#offer;
    const button = /** @type {HTMLButtonElement} */ (event.currentTarget);
    const status = this.querySelector('[data-apb-set-status]');
    if (!offer?.bundle || button.getAttribute('aria-busy') === 'true') return;

    const selected = this.#selectedPartners();
    const lines = [
      { variantId: this.#mainVariantId(), quantity: 1 },
      ...selected.map((input) => ({ variantId: Number(input.dataset.variantId), quantity: 1 })),
    ];

    button.setAttribute('aria-busy', 'true');
    if (status) status.textContent = '';

    try {
      markSeen(offer.productId);
      let result;
      if (selected.length > 0) {
        const codes =
          selected.length >= 2
            ? { add: offer.bundle.codeTwo, remove: [offer.bundle.codeOne] }
            : { add: offer.bundle.codeOne, remove: [offer.bundle.codeTwo] };
        result = await addToCart(lines, codes);
      } else {
        result = await addToCart(lines);
      }
      announceCartAdd(this, lines, result.cart, result.sections);
      if (status) {
        status.textContent = result.codeAccepted
          ? 'Set hinzugefügt – der Rabatt ist im Warenkorb aktiv.'
          : 'Set hinzugefügt. Der Rabatt konnte leider nicht angewendet werden.';
      }
    } catch (error) {
      if (status) status.textContent = error instanceof Error ? error.message : 'Das hat leider nicht geklappt.';
    } finally {
      button.removeAttribute('aria-busy');
    }
  };
}

/* -------------------------------------------------------------------------- */
/* Add-to-cart pop-up                                                          */
/* -------------------------------------------------------------------------- */

class OfferPopup {
  /** @type {HTMLDialogElement | null} */
  dialog = document.getElementById('apb-offer-dialog') instanceof HTMLDialogElement
    ? /** @type {HTMLDialogElement} */ (document.getElementById('apb-offer-dialog'))
    : null;

  /** @type {any} */
  offer = null;
  /** @type {any} */
  cart = null;
  /** @type {number} */
  addedVariantId = 0;
  openDrawerOnClose = false;
  /** @type {string} */
  message = '';

  constructor() {
    if (!this.dialog) return;
    this.dialog.addEventListener('click', this.#onClick);
    this.dialog.addEventListener('close', this.#onClose);
  }

  get enabled() {
    return Boolean(this.dialog);
  }

  /**
   * @param {any} offer
   * @param {{ cart: any, variantId: number, openDrawerOnClose: boolean }} options
   */
  show(offer, { cart, variantId, openDrawerOnClose }) {
    if (!this.dialog) return;
    this.offer = offer;
    this.cart = cart;
    this.addedVariantId = variantId || offer.variantId;
    this.openDrawerOnClose = openDrawerOnClose;
    this.message = '';
    this.#render();
    this.dialog.showModal();
    /** @type {HTMLElement | null} */ (this.dialog.querySelector('[data-apb-primary]'))?.focus();
  }

  #onClose = () => {
    if (this.openDrawerOnClose) openCartDrawer();
  };

  /** @param {MouseEvent} event */
  #onClick = async (event) => {
    const target = event.target instanceof Element ? event.target : null;
    if (!target || !this.dialog) return;

    // Click on the backdrop closes the dialog.
    if (target === this.dialog) {
      this.dialog.close();
      return;
    }

    const action = target.closest('[data-apb-action]');
    if (!(action instanceof HTMLButtonElement)) return;

    switch (action.dataset.apbAction) {
      case 'close':
        this.dialog.close();
        return;
      case 'add-quantity':
        await this.#run(action, () => this.#addQuantity(Number(action.dataset.variantId), Number(action.dataset.quantity)));
        return;
      case 'add-partner':
        await this.#run(action, () => this.#addPartners([Number(action.dataset.productId)]));
        return;
      case 'add-partners':
        await this.#run(action, () =>
          this.#addPartners(this.offer.bundle.partners.map((/** @type {any} */ partner) => partner.productId))
        );
        return;
    }
  };

  /**
   * @param {HTMLButtonElement} button
   * @param {() => Promise<void>} task
   */
  async #run(button, task) {
    if (button.getAttribute('aria-busy') === 'true') return;
    button.setAttribute('aria-busy', 'true');
    try {
      await task();
    } catch (error) {
      this.message = error instanceof Error ? error.message : 'Das hat leider nicht geklappt.';
    } finally {
      button.removeAttribute('aria-busy');
      this.#render();
    }
  }

  /**
   * @param {number} variantId
   * @param {number} quantity
   */
  async #addQuantity(variantId, quantity) {
    const lines = [{ variantId, quantity }];
    const result = await addToCart(lines);
    this.cart = result.cart;
    withoutDrawerAutoOpen(() => announceCartAdd(this.dialog ?? document, lines, result.cart, result.sections));
    const tiers = this.offer.quantity.tiers;
    const count = quantityInCart(this.cart, this.offer.quantity.productIds);
    const reached = [...tiers].reverse().find((/** @type {any} */ tier) => count >= tier.min);
    this.message = reached ? `−${reached.percent} % auf alle ${this.offer.quantity.unitOther} sind jetzt aktiv.` : 'Hinzugefügt.';
  }

  /** @param {number[]} productIds */
  async #addPartners(productIds) {
    const partners = this.offer.bundle.partners.filter(
      (/** @type {any} */ partner) => productIds.includes(partner.productId) && partner.available && !inCart(this.cart, partner.productId)
    );
    if (partners.length === 0) return;

    const lines = partners.map((/** @type {any} */ partner) => ({ variantId: partner.variantId, quantity: 1 }));
    const projected = {
      items: [...(this.cart?.items ?? []), ...partners.map((/** @type {any} */ partner) => ({ product_id: partner.productId, quantity: 1 }))],
    };
    const codes = setCodesFor(this.offer, projected);
    const result = await addToCart(lines, { add: codes.add, remove: codes.remove });
    this.cart = result.cart;
    withoutDrawerAutoOpen(() => announceCartAdd(this.dialog ?? document, lines, result.cart, result.sections));
    this.message = result.codeAccepted
      ? `−${codes.percent} % aufs Zubehör sind jetzt aktiv.`
      : 'Hinzugefügt. Der Rabatt konnte leider nicht angewendet werden.';
  }

  #render() {
    const panel = this.dialog?.querySelector('[data-apb-offer-panel]');
    if (!panel || !this.offer) return;

    const offer = this.offer;
    const body = offer.type === 'quantity' ? this.#quantityMarkup() : this.#bundleMarkup();

    panel.innerHTML = `
      <div class="apb-popup__head">
        <p class="apb-popup__added">
          <span class="apb-popup__tick" aria-hidden="true"></span>
          Zum Warenkorb hinzugefügt
        </p>
        <button type="button" class="apb-popup__close" data-apb-action="close" aria-label="Schließen">
          <svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M3 3l10 10M13 3 3 13"/></svg>
        </button>
      </div>
      <div class="apb-popup__product">
        ${offer.image ? `<img src="${escapeHtml(offer.image)}" alt="" width="64" height="64" loading="lazy">` : ''}
        <p>${escapeHtml(offer.title)}</p>
      </div>
      ${body}
      <p class="apb-popup__message" role="status">${escapeHtml(this.message)}</p>
      <div class="apb-popup__footer">
        <button type="button" class="apb-popup__link" data-apb-action="close">Nein, danke</button>
        <button type="button" class="apb-popup__secondary button button-secondary" data-apb-action="close">Zum Warenkorb</button>
      </div>
      <p class="apb-popup__fine">Rabatte werden im Warenkorb automatisch abgezogen. Pro Artikel gilt der höhere Rabatt.</p>
    `;
  }

  #quantityMarkup() {
    const offer = this.offer;
    const { tiers, productIds, unitOne, unitOther, suggestions } = offer.quantity;
    const count = quantityInCart(this.cart, productIds);
    const unit = (/** @type {number} */ amount) => (amount === 1 ? unitOne : unitOther);
    const best = tiers[tiers.length - 1];

    const rows = tiers
      .map((/** @type {any} */ tier, /** @type {number} */ index) => {
        const missing = tier.min - count;
        const reached = missing <= 0;
        const primary = !reached && tiers.slice(0, index).every((/** @type {any} */ previous) => previous.min - count <= 0);
        return `
          <li class="apb-popup__tier${reached ? ' is-reached' : ''}">
            <div class="apb-popup__tier-copy">
              <strong>ab ${tier.min} ${escapeHtml(unit(tier.min))}</strong>
              <span class="apb-popup__badge">−${tier.percent} %</span>
            </div>
            ${
              reached
                ? '<span class="apb-popup__done">Aktiv ✓</span>'
                : `<button type="button" class="apb-popup__add button${primary ? '' : ' button-secondary'}"
                    ${primary ? 'data-apb-primary' : ''}
                    data-apb-action="add-quantity" data-variant-id="${this.addedVariantId}" data-quantity="${missing}">
                    +${missing} hinzufügen · ${money(discounted(offer.price, tier.percent) * missing, offer)}
                  </button>`
            }
          </li>`;
      })
      .join('');

    const mix =
      count < best.min && suggestions?.length
        ? `
          <div class="apb-popup__mix">
            <p class="apb-popup__label">Oder kombiniere mit</p>
            <ul class="apb-popup__cards">
              ${suggestions
                .map(
                  (/** @type {any} */ item) => `
                <li class="apb-popup__card">
                  ${item.image ? `<img src="${escapeHtml(item.image)}" alt="" width="48" height="48" loading="lazy">` : '<span class="apb-popup__ph"></span>'}
                  <span class="apb-popup__card-copy">
                    <a href="${escapeHtml(item.url)}">${escapeHtml(item.title)}</a>
                    ${item.variantTitle ? `<span>${escapeHtml(item.variantTitle)}</span>` : ''}
                    <span>${money(item.price, offer)}</span>
                  </span>
                  <button type="button" class="apb-popup__plus" data-apb-action="add-quantity"
                    data-variant-id="${item.variantId}" data-quantity="1"
                    aria-label="${escapeHtml(item.title)} hinzufügen">+</button>
                </li>`
                )
                .join('')}
            </ul>
          </div>`
        : '';

    const headline =
      count >= best.min
        ? `Bester Preis: −${best.percent} % auf alle ${escapeHtml(unitOther)}`
        : 'Mehr kaufen, mehr sparen';

    return `
      <div class="apb-popup__offer">
        <p class="apb-popup__eyebrow">Mengenrabatt</p>
        <h2 id="apb-offer-dialog-title" class="apb-popup__title">${headline}</h2>
        <p class="apb-popup__text">Im Warenkorb: <strong>${count} ${escapeHtml(unit(count))}</strong>. Alle ${escapeHtml(unitOther)} zählen zusammen – auch gemischt.</p>
        <ol class="apb-popup__tiers">${rows}</ol>
        ${mix}
      </div>`;
  }

  #bundleMarkup() {
    const offer = this.offer;
    const { partners, percentOne, percentTwo } = offer.bundle;
    const available = partners.filter((/** @type {any} */ partner) => partner.available);
    const missing = available.filter((/** @type {any} */ partner) => !inCart(this.cart, partner.productId));
    const both = available.length >= 2 && missing.length === available.length;

    const cards = available
      .map((/** @type {any} */ partner) => {
        const added = inCart(this.cart, partner.productId);
        const percent = available.filter((/** @type {any} */ item) => inCart(this.cart, item.productId) || item === partner).length >= 2 ? percentTwo : percentOne;
        return `
          <li class="apb-popup__card apb-popup__card--partner">
            ${partner.image ? `<img src="${escapeHtml(partner.image)}" alt="" width="56" height="56" loading="lazy">` : '<span class="apb-popup__ph"></span>'}
            <span class="apb-popup__card-copy">
              <a href="${escapeHtml(partner.url)}">${escapeHtml(partner.title)}</a>
              ${partner.variantTitle ? `<span>${escapeHtml(partner.variantTitle)}</span>` : ''}
              <span class="apb-popup__price"><s>${money(partner.price, offer)}</s> <strong>${money(discounted(partner.price, percent), offer)}</strong></span>
            </span>
            ${
              added
                ? '<span class="apb-popup__done">Im Warenkorb ✓</span>'
                : `<button type="button" class="apb-popup__add button button-secondary" data-apb-action="add-partner" data-product-id="${partner.productId}">
                    Hinzufügen · −${percent} %
                  </button>`
            }
          </li>`;
      })
      .join('');

    const bothTotal = available.reduce((sum, /** @type {any} */ partner) => sum + discounted(partner.price, percentTwo), 0);
    const bothFull = available.reduce((sum, /** @type {any} */ partner) => sum + partner.price, 0);

    const bothButton = both
      ? `<button type="button" class="apb-popup__add apb-popup__add--wide button" data-apb-primary data-apb-action="add-partners">
           Beide hinzufügen · spare ${percentTwo} % (${money(bothFull - bothTotal, offer)})
         </button>`
      : '';

    const headline = missing.length === 0 ? `Set komplett – −${available.length >= 2 ? percentTwo : percentOne} % aktiv` : 'Passt perfekt dazu';

    return `
      <div class="apb-popup__offer">
        <p class="apb-popup__eyebrow">Im Set günstiger</p>
        <h2 id="apb-offer-dialog-title" class="apb-popup__title">${escapeHtml(headline)}</h2>
        <p class="apb-popup__text">Füge das passende Zubehör hinzu und spare ${percentOne} % – mit beiden Artikeln sogar ${percentTwo} %.</p>
        <ul class="apb-popup__cards">${cards}</ul>
        ${bothButton}
      </div>`;
  }
}

/* -------------------------------------------------------------------------- */
/* Wiring                                                                      */
/* -------------------------------------------------------------------------- */

if (!customElements.get('apb-offer-tiers')) customElements.define('apb-offer-tiers', OfferTiers);
if (!customElements.get('apb-offer-set')) customElements.define('apb-offer-set', OfferSet);

if (!(/** @type {any} */ (window).__apbOfferPopup)) {
  const popup = new OfferPopup();
  /** @type {any} */ (window).__apbOfferPopup = popup;

  /**
   * Capture phase on window runs before the cart drawer's listener on document, so
   * auto-open can be held back for this add.
   * @param {any} event
   */
  const onCartLinesUpdate = (event) => {
    if (dispatchingOwnEvent || !popup.enabled || event.action !== 'add') return;

    const source = event.target instanceof Element ? event.target.closest('[data-product-id]') : null;
    const productId = source instanceof HTMLElement ? source.dataset.productId : undefined;
    if (!productId || hasSeen(productId)) return;

    const offer = readOffer(productId);
    if (!offer) return;

    const component = cartDrawerComponent();
    const hadAutoOpen = Boolean(component?.hasAttribute('auto-open'));
    if (hadAutoOpen) {
      component?.removeAttribute('auto-open');
      setTimeout(() => component?.setAttribute('auto-open', ''), 0);
    }

    const sourceModal = event.target instanceof Element ? event.target.closest('dialog:modal') : null;
    const variantId = Number(event.lines?.[0]?.merchandiseId) || offer.variantId;

    Promise.resolve(event.promise)
      .then(async (/** @type {any} */ result) => {
        if (result?.detail?.didError) return;
        if (sourceModal instanceof HTMLDialogElement && sourceModal.open) {
          await new Promise((resolve) => sourceModal.addEventListener('close', resolve, { once: true }));
        }

        const cart = await getCart();
        const nothingLeftToOffer =
          offer.type === 'quantity'
            ? quantityInCart(cart, offer.quantity.productIds) >= offer.quantity.tiers[offer.quantity.tiers.length - 1].min
            : offer.bundle.partners.every((/** @type {any} */ partner) => !partner.available || inCart(cart, partner.productId));

        if (nothingLeftToOffer) {
          if (hadAutoOpen) openCartDrawer();
          return;
        }

        markSeen(productId);
        popup.show(offer, { cart, variantId, openDrawerOnClose: hadAutoOpen });
      })
      .catch(() => {
        if (hadAutoOpen) openCartDrawer();
      });
  };

  window.addEventListener(StandardEvents.cartLinesUpdate, onCartLinesUpdate, { capture: true });
}
