/**
 * The Rose Atelier — script.js
 * Handles: mobile nav drawer, scroll-reveal animations,
 *          AJAX add-to-cart, cart quantity updates, toasts
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Mobile nav drawer ────────────────────────────────────────
  const navToggle   = document.getElementById('navToggle');
  const mobileDrawer = document.getElementById('mobileDrawer');
  const drawerClose  = document.getElementById('drawerClose');

  if (navToggle && mobileDrawer) {
    navToggle.addEventListener('click', () => mobileDrawer.classList.add('open'));
  }
  if (drawerClose && mobileDrawer) {
    drawerClose.addEventListener('click', () => mobileDrawer.classList.remove('open'));
  }
  mobileDrawer && mobileDrawer.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => mobileDrawer.classList.remove('open'));
  });

  // ── Scroll-reveal: ribbon headings + fade-in blocks ──────────
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  document.querySelectorAll('.ribbon-heading, .fade-in-scroll').forEach(el => {
    observer.observe(el);
  });

  // ── Flash message auto-dismiss ───────────────────────────────
  document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => dismissFlash(flash), 4500);
  });
  document.querySelectorAll('.flash-close').forEach(btn => {
    btn.addEventListener('click', () => dismissFlash(btn.closest('.flash')));
  });
  function dismissFlash(el) {
    if (!el) return;
    el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateX(24px)';
    setTimeout(() => el.remove(), 320);
  }

  // ── Mini toast helper (for AJAX feedback) ────────────────────
  function showToast(message) {
    let toast = document.getElementById('miniToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'miniToast';
      toast.className = 'mini-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(toast._hideTimer);
    toast._hideTimer = setTimeout(() => toast.classList.remove('show'), 2600);
  }

  // ── AJAX: Add to cart (shop page + product cards) ────────────
  document.querySelectorAll('.add-cart-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('.add-cart-btn');
      const originalText = btn.textContent;

      try {
        const res = await fetch(form.action, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          body: new FormData(form)
        });
        const data = await res.json();

        if (data.success) {
          btn.textContent = 'Added ✓';
          btn.classList.add('added');
          updateCartBadge(data.cart_count);
          showToast(`${data.product_name} added to your cart`);

          setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('added');
          }, 1600);
        }
      } catch {
        showToast('Something went wrong. Please try again.');
      }
    });
  });

  function updateCartBadge(count) {
    document.querySelectorAll('.cart-badge').forEach(badge => {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    });
    // If badge doesn't exist yet but count > 0, that's handled server-side on reload
  }

  // ── Cart page: quantity +/- buttons ──────────────────────────
  document.querySelectorAll('.qty-control').forEach(control => {
    const input    = control.querySelector('input');
    const minusBtn = control.querySelector('.qty-minus');
    const plusBtn  = control.querySelector('.qty-plus');
    const productId = control.dataset.productId;

    minusBtn && minusBtn.addEventListener('click', () => {
      const newQty = Math.max(0, parseInt(input.value, 10) - 1);
      input.value = newQty;
      updateCartQuantity(productId, newQty);
    });

    plusBtn && plusBtn.addEventListener('click', () => {
      const newQty = parseInt(input.value, 10) + 1;
      input.value = newQty;
      updateCartQuantity(productId, newQty);
    });

    input && input.addEventListener('change', () => {
      const newQty = Math.max(0, parseInt(input.value, 10) || 0);
      input.value = newQty;
      updateCartQuantity(productId, newQty);
    });
  });

  async function updateCartQuantity(productId, quantity) {
    try {
      const body = new FormData();
      body.append('product_id', productId);
      body.append('quantity', quantity);

      const res = await fetch('/cart/update', {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body
      });
      const data = await res.json();

      if (data.success) {
        if (quantity <= 0) {
          // Remove the row from view
          const row = document.querySelector(`[data-cart-row="${productId}"]`);
          if (row) row.remove();
        } else {
          // Update this row's line total
          const lineEl = document.querySelector(`[data-line-total="${productId}"]`);
          const product = window.PRODUCT_PRICES ? window.PRODUCT_PRICES[productId] : null;
          if (lineEl && product) {
            lineEl.textContent = formatPrice(product * quantity);
          }
        }
        // Update summary totals
        const totalPriceEl = document.getElementById('cartTotalPrice');
        const totalItemsEl = document.getElementById('cartTotalItems');
        if (totalPriceEl) totalPriceEl.textContent = formatPrice(data.total_price);
        if (totalItemsEl) totalItemsEl.textContent = data.total_items;
        updateCartBadge(data.cart_count);

        // If cart is now empty, reload to show empty state
        if (data.total_items === 0) {
          window.location.reload();
        }
      }
    } catch {
      showToast('Could not update cart. Please try again.');
    }
  }

  function formatPrice(amount) {
    return '₹' + Number(amount).toLocaleString('en-IN');
  }

  // ── Cart page: remove item ───────────────────────────────────
  document.querySelectorAll('.remove-item-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const productId = form.dataset.productId;

      try {
        const res = await fetch(form.action, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          body: new FormData(form)
        });
        const data = await res.json();

        if (data.success) {
          const row = document.querySelector(`[data-cart-row="${productId}"]`);
          if (row) {
            row.style.transition = 'opacity 0.3s ease';
            row.style.opacity = '0';
            setTimeout(() => row.remove(), 300);
          }
          const totalPriceEl = document.getElementById('cartTotalPrice');
          const totalItemsEl = document.getElementById('cartTotalItems');
          if (totalPriceEl) totalPriceEl.textContent = formatPrice(data.total_price);
          if (totalItemsEl) totalItemsEl.textContent = data.total_items;
          updateCartBadge(data.cart_count);
          showToast('Item removed from cart');

          if (data.total_items === 0) {
            setTimeout(() => window.location.reload(), 400);
          }
        }
      } catch {
        showToast('Could not remove item. Please try again.');
      }
    });
  });

  // ── Shop page: category filter (no reload, smooth) ───────────
  const filterPills = document.querySelectorAll('.filter-pill');
  filterPills.forEach(pill => {
    pill.addEventListener('click', (e) => {
      // Allow normal navigation (server-rendered filter via URL param)
      // but add a quick active-state swap for instant feedback
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
    });
  });

  // ── Nav background on scroll (subtle shadow once scrolled) ───
  const nav = document.querySelector('.nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 12) {
        nav.style.boxShadow = '0 4px 20px rgba(43,35,32,0.06)';
      } else {
        nav.style.boxShadow = 'none';
      }
    });
  }

});