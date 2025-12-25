// Cart module placeholder. Add cart-related logic here.
// Example structure:
// - addToCart(productId, qty)
// - removeFromCart(productId)
// - updateQty(productId, qty)
// - calculateTotals()
// - persist to localStorage

(function(){
  'use strict';

  const CART_KEY = 'inbis_cart_v1';

  function loadCart(){
    try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch { return []; }
  }
  function saveCart(items){ localStorage.setItem(CART_KEY, JSON.stringify(items)); }

  function addToCart(id, qty=1){
    const items = loadCart();
    const idx = items.findIndex(i => i.id === id);
    if (idx >= 0) items[idx].qty += qty; else items.push({id, qty});
    saveCart(items);
    return items;
  }

  function removeFromCart(id){
    const items = loadCart().filter(i => i.id !== id);
    saveCart(items);
    return items;
  }

  function updateQty(id, qty){
    const items = loadCart();
    const it = items.find(i => i.id === id);
    if (it) it.qty = Math.max(0, qty);
    saveCart(items);
    return items;
  }

  function clearCart(){ saveCart([]); }

  // Expose globally (adjust if using modules/bundlers)
  window.Cart = { loadCart, addToCart, removeFromCart, updateQty, clearCart };
})();

(function(){
  'use strict';

  function ensureNoticeEl(){
    let el = document.getElementById('cart-notice');
    if (el) return el;
    el = document.createElement('div');
    el.id = 'cart-notice';
    el.style.position = 'fixed';
    el.style.right = '16px';
    el.style.top = '16px';
    el.style.zIndex = '9999';
    el.style.padding = '10px 12px';
    el.style.borderRadius = '10px';
    el.style.background = '#111827';
    el.style.color = '#fff';
    el.style.fontSize = '13px';
    el.style.boxShadow = '0 10px 30px rgba(0,0,0,0.25)';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-8px)';
    el.style.transition = 'opacity 200ms ease, transform 200ms ease';
    document.body.appendChild(el);
    return el;
  }

  let hideTimer;
  function showNotice(text){
    const el = ensureNoticeEl();
    el.textContent = text;
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
    if (hideTimer) window.clearTimeout(hideTimer);
    hideTimer = window.setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
    }, 1800);
  }

  document.addEventListener('click', function(e){
    const btn = e.target.closest('[data-cart-add][data-product-id]');
    if (!btn) return;
    e.preventDefault();

    const authMeta = document.querySelector('meta[name="is-authenticated"]');
    const isAuthed = authMeta ? authMeta.getAttribute('content') === '1' : false;
    if (!isAuthed) {
      const next = window.location.pathname + window.location.search;
      window.location.href = '/login/?next=' + encodeURIComponent(next);
      return;
    }

    const id = parseInt(btn.dataset.productId, 10);
    const qty = parseInt(btn.dataset.qty || '1', 10) || 1;
    if (!window.Cart || Number.isNaN(id)) return;
    window.Cart.addToCart(id, qty);
    showNotice('Produk ditambahkan ke keranjang.');
  });
})();

// ================== Penjualan page logic extracted from penjualan.html ==================
(function(){
  'use strict';

  document.addEventListener('DOMContentLoaded', function(){
    const productListEl = document.getElementById('product-list');
    const paginationEl = document.getElementById('pagination');
    const categoryListEl = document.getElementById('category-list');
    const digitalViewEl = document.getElementById('digital-view');
    const digitalGalleryEl = document.getElementById('digital-gallery');

    // Only run on penjualan page
    if (!productListEl || !paginationEl || !categoryListEl) return;

    // Parse server-rendered JSON data
    const productsDataEl = document.getElementById('products-data');
    const jasaDataEl = document.getElementById('jasa-data');
    const products = productsDataEl ? JSON.parse(productsDataEl.textContent) : [];
    const jasa = jasaDataEl ? JSON.parse(jasaDataEl.textContent) : [];

    const productsPerPage = 12;
    let currentPage = 1;
    let currentCategory = 'all';
    let currentView = 'kategori';

    function renderProducts(){
      if (currentView !== 'kategori') return;
      // Ensure correct panels are visible when rendering products
      productListEl.style.display = '';
      paginationEl.style.display = '';
      if (digitalViewEl) digitalViewEl.style.display = 'none';
      const filtered = currentCategory === 'all' ? products : products.filter(p => p.category === currentCategory);
      const startIndex = (currentPage - 1) * productsPerPage;
      const pageItems = filtered.slice(startIndex, startIndex + productsPerPage);

      if (filtered.length === 0) {
        productListEl.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; color:#6b7280; padding:16px;">Belum ada produk untuk kategori ini.</div>`;
        paginationEl.innerHTML = '';
        return;
      }

      productListEl.innerHTML = pageItems.map(product => {
        const productUrl = product.url || '#';
        const stockClass = product.stok > 0 ? '' : 'out-of-stock';
        const stockText = product.stok > 0 ? `Stok: ${product.stok}` : 'Stok Habis';
        return `
        <div class="product-card">
          <div class="product-media">
            <img src="${product.img}" alt="${product.name}" />
            <a class="product-link-icon" href="${productUrl}" aria-label="Lihat ${product.name}">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/>
              </svg>
            </a>
          </div>
          <div class="product-name">${product.name}</div>
          <div class="product-stock ${stockClass}">${stockText}</div>
          <div class="product-desc">${product.desc}</div>
        </div>`;
      }).join('');

      if (filtered.length > productsPerPage) {
        const totalPages = Math.ceil(filtered.length / productsPerPage);
        paginationEl.innerHTML = Array.from({length: totalPages}, (_, i) => i + 1)
          .map(i => `<button class="page-btn ${i===currentPage?'active':''}" data-page="${i}">${i}</button>`)
          .join('');
      } else {
        paginationEl.innerHTML = '';
      }
    }

    function goToPage(page){
      currentPage = page;
      renderProducts();
    }

    paginationEl.addEventListener('click', (e) => {
      const btn = e.target.closest('.page-btn');
      if (!btn) return;
      const p = parseInt(btn.getAttribute('data-page'), 10);
      if (!isNaN(p)) goToPage(p);
    });

    // Category clicks and image modal
    // Create category modal once
    const categoryModal = document.createElement('div');
    categoryModal.className = 'category-modal-overlay';
    categoryModal.innerHTML = `
      <button class="category-modal-close" aria-label="Tutup">✕</button>
      <div class="category-modal-content"><img src="" alt="Preview Kategori"/></div>
    `;
    document.body.appendChild(categoryModal);
    const categoryModalImg = categoryModal.querySelector('img');
    const categoryModalClose = categoryModal.querySelector('.category-modal-close');

    categoryModal.addEventListener('click', (e) => {
      if (e.target === categoryModal || e.target === categoryModalClose) {
        categoryModal.classList.remove('active');
        document.body.style.overflow = '';
      }
    });

    categoryListEl.addEventListener('click', (e) => {
      const img = e.target.closest('img');
      const categoryItem = e.target.closest('.category-item');

      if (img && img.closest('.category-item')) {
        e.preventDefault();
        e.stopPropagation();
        document.body.style.overflow = 'hidden';
        categoryModalImg.classList.remove('visible');
        categoryModalImg.src = img.src;
        categoryModalImg.alt = img.alt;
        categoryModal.classList.add('active');
        categoryModalImg.onload = () => categoryModalImg.classList.add('visible');
        return;
      }

      if (!categoryItem) return;
      // If clicking the special "Digital" item inserted in categories, switch to digital view directly
      if (categoryItem.hasAttribute('data-digital')) {
        [...categoryListEl.children].forEach(item => item.classList.remove('active'));
        categoryItem.classList.add('active');
        currentView = 'digital';
        productListEl.style.display = 'none';
        paginationEl.style.display = 'none';
        if (digitalViewEl) {
          digitalViewEl.style.display = '';
        }
        renderDigital();
        return;
      }
      [...categoryListEl.children].forEach(item => item.classList.remove('active'));
      categoryItem.classList.add('active');
      currentCategory = categoryItem.getAttribute('data-category');
      currentPage = 1;
      // Ensure returning to kategori view hides digital
      currentView = 'kategori';
      if (digitalViewEl) digitalViewEl.style.display = 'none';
      productListEl.style.display = '';
      paginationEl.style.display = '';
      renderProducts();
    });

    // Toggle bar removed: view switching is controlled from category click above

    function renderDigital(){
      const items = jasa.slice(0, 12);
      if (!digitalGalleryEl) return;
      digitalGalleryEl.innerHTML = items.map((j, i) => `
        <div class="digital-card" data-index="${i}">
          <img src="${j.img}" alt="Digital ${i+1}"/>
          <div class="digital-caption">${j.desc || ''}</div>
        </div>
      `).join('');
    }

    // Digital modal
    const digitalModal = document.createElement('div');
    digitalModal.className = 'digital-modal-overlay';
    digitalModal.innerHTML = `
      <button class="digital-modal-close" aria-label="Tutup">✕</button>
      <div class="digital-modal-content">
        <img src="" alt="Pratinjau Gambar"/>
        <div class="digital-modal-description"></div>
      </div>
    `;
    document.body.appendChild(digitalModal);
    const digitalModalImg = digitalModal.querySelector('img');
    const digitalModalClose = digitalModal.querySelector('.digital-modal-close');
    const digitalModalDesc = digitalModal.querySelector('.digital-modal-description');

    digitalModal.addEventListener('click', (e) => {
      if (e.target === digitalModal || e.target === digitalModalClose) {
        digitalModal.classList.remove('active');
        document.body.style.overflow = '';
      }
    });

    if (digitalGalleryEl) {
      digitalGalleryEl.addEventListener('click', (e) => {
        const card = e.target.closest('.digital-card');
        if (!card) return;
        const img = card.querySelector('img');
        if (!img) return;
        const idx = parseInt(card.getAttribute('data-index'), 10);
        const descText = (jasa[idx] && jasa[idx].desc) ? jasa[idx].desc : '';
        digitalModalImg.classList.remove('visible');
        const src = img.src;
        if (digitalModalImg.complete && digitalModalImg.naturalWidth && digitalModalImg.src === src) {
          requestAnimationFrame(() => digitalModalImg.classList.add('visible'));
        } else {
          digitalModalImg.onload = () => { digitalModalImg.classList.add('visible'); };
        }
        digitalModalImg.src = src;
        digitalModalDesc.textContent = descText;
        document.body.style.overflow = 'hidden';
        digitalModal.classList.add('active');
      });
    }

    // Initial render: ensure digital view hidden by default
    if (digitalViewEl) digitalViewEl.style.display = 'none';
    renderProducts();
  });
})();
