/**
 * skin-engine.js — Panelium2 JSON-Driven Skin Engine
 * IIFE module. Reads configData.skin + configData.panoramas and renders
 * the full hotel virtual tour UI: header, footer, navigation, popups, social.
 *
 * Public API:
 *   SkinEngine.init(configData, viewer)
 *   SkinEngine.goToScene(sceneId)
 *   SkinEngine.openPopup(popupId)
 *   SkinEngine.closePopup()
 *   SkinEngine.setActiveScene(sceneId)
 */

const SkinEngine = (function () {
    'use strict';

    // ── State ────────────────────────────────────────────────
    let _cfg = null;   // configData.skin
    let _panos = [];     // configData.panoramas
    let _viewer = null;   // Pannellum viewer instance
    let _currentScene = null;
    let _currentCat = null;
    let _navOpen = false;
    let _sliderIndexes = {}; // popup_id → current slide index

    // ── Preset themes ────────────────────────────────────────
    const PRESETS = {
        luxury: {
            primary_color: '#1a1a2e',
            accent_color: '#c9a84c',
            text_color: '#ffffff',
            background_color: '#0f0f1e',
            font_family: 'Cormorant Garamond, Georgia, serif',
            border_radius: '4px',
        },
        glass: {
            primary_color: '#1e293b',
            accent_color: '#38bdf8',
            text_color: '#f1f5f9',
            background_color: '#0f172a',
            font_family: 'Inter, system-ui, sans-serif',
            border_radius: '8px',
        },
        minimal: {
            primary_color: '#ffffff',
            accent_color: '#111111',
            text_color: '#111111',
            background_color: '#f5f5f5',
            font_family: 'Inter, system-ui, sans-serif',
            border_radius: '2px',
        },
        nature: {
            primary_color: '#1a3a2e',
            accent_color: '#7ec8a0',
            text_color: '#e8f5ee',
            background_color: '#0d2218',
            font_family: 'Lato, Helvetica, sans-serif',
            border_radius: '6px',
        },
    };

    // ── Utility ──────────────────────────────────────────────
    function el(id) { return document.getElementById(id); }
    function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
    function qsa(sel, ctx) { return (ctx || document).querySelectorAll(sel); }

    function applyTheme(theme) {
        const preset = PRESETS[theme.preset] || PRESETS.luxury;
        const t = Object.assign({}, preset, theme);
        const root = document.documentElement;
        root.style.setProperty('--skin-primary', t.primary_color);
        root.style.setProperty('--skin-accent', t.accent_color);
        root.style.setProperty('--skin-text', t.text_color);
        root.style.setProperty('--skin-bg', t.background_color);
        root.style.setProperty('--skin-font', t.font_family);
        root.style.setProperty('--skin-radius', t.border_radius);
        if (t.header_height) root.style.setProperty('--skin-header-h', t.header_height);
        if (t.thumb_size) root.style.setProperty('--skin-thumb-size', t.thumb_size);
    }

    // ── Build Header ─────────────────────────────────────────
    function buildHeader() {
        const skin = _cfg;
        if (!skin.header || !skin.header.enabled) return '';

        const logoHtml = buildLogo(skin.logo);
        const navHtml = buildNavTrigger(skin.navigation);
        const rightHtml = buildHeaderRight(skin);

        return `
        <header id="skin-header">
            <div class="skin-header-left">
                ${logoHtml}
                ${navHtml}
            </div>
            <div class="skin-header-center"></div>
            <div class="skin-header-right">
                ${rightHtml}
            </div>
        </header>`;
    }

    function buildLogo(logo) {
        if (!logo || !logo.enabled) return '';
        const href = logo.link ? `href="${logo.link}"` : 'href="#" onclick="return false;"';
        const style = logo.width ? `style="max-width:${logo.width}"` : '';
        const imgTag = logo.url
            ? `<img src="${logo.url}" alt="${logo.alt || 'Logo'}" ${style} onerror="this.style.display='none';this.nextElementSibling.style.display='block'">`
            : '';
        const textTag = `<span class="skin-logo-text" ${!logo.url ? '' : 'style="display:none"'}>${logo.alt || 'Tour'}</span>`;
        return `<a class="skin-logo" ${href}>${imgTag}${textTag}</a>`;
    }

    function buildNavTrigger(nav) {
        if (!nav || !nav.enabled) return '';
        return `
        <button class="skin-nav-trigger" id="skin-nav-trigger" aria-expanded="false" aria-controls="skin-nav-dropdown">
            <svg class="trigger-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
            ${nav.label || 'Keşfet'}
        </button>`;
    }

    function buildHeaderRight(skin) {
        let html = '';

        // Social icons
        if (skin.social && skin.social.enabled && skin.social.position === 'header_right') {
            html += buildSocialIcons(skin.social);
        }

        // Custom menu buttons positioned in header_right
        if (skin.navigation && skin.navigation.custom_menus) {
            skin.navigation.custom_menus
                .filter(m => m.position === 'header_right')
                .forEach(m => { html += buildCustomBtn(m); });
        }

        return html;
    }

    function buildSocialIcons(social) {
        if (!social.items || !social.items.length) return '';
        return `<div id="skin-social">` +
            social.items.map(item => {
                const iconHtml = item.icon
                    ? `<img src="${item.icon}" alt="${item.label || ''}">`
                    : item.emoji || '🔗';
                return `<a class="skin-social-link" href="${item.url || '#'}" target="_blank" rel="noopener" title="${item.label || ''}">${iconHtml}</a>`;
            }).join('') +
            `</div>`;
    }

    function buildCustomBtn(menu) {
        const iconHtml = menu.icon ? `<img src="${menu.icon}" alt="">` : '';
        return `<button class="skin-custom-btn" data-action="${menu.action}" data-popup-id="${menu.popup_id || ''}" data-scene-id="${menu.scene_id || ''}" id="skin-custombtn-${menu.id}">
            ${iconHtml}${menu.label || ''}
        </button>`;
    }

    // ── Build Navigation Dropdown ────────────────────────────
    function buildNavDropdown() {
        const nav = _cfg.navigation;
        if (!nav || !nav.enabled) return '';

        const cats = nav.show_categories && nav.categories && nav.categories.length
            ? nav.categories
            : null;

        // determine default cat
        if (cats) {
            _currentCat = cats[0];
        }

        const catTabsHtml = cats ? `
        <div class="skin-nav-categories">
            ${cats.map((c, i) => `<button class="skin-cat-tab ${i === 0 ? 'is-active' : ''}" data-cat="${c}">${c}</button>`).join('')}
        </div>` : '';

        return `
        <div id="skin-nav-dropdown" role="dialog" aria-label="Sahne Navigasyonu">
            ${catTabsHtml}
            <div class="skin-scene-grid" id="skin-scene-grid">
                ${buildSceneCards(_currentCat)}
            </div>
        </div>`;
    }

    function buildSceneCards(filterCat) {
        const panos = filterCat
            ? _panos.filter(p => p.category === filterCat && !p.hidden)
            : _panos.filter(p => !p.hidden);

        return panos
            .sort((a, b) => (a.order || 0) - (b.order || 0))
            .map(p => {
                const isActive = p.id === _currentScene ? ' is-active' : '';
                return `
                <div class="skin-scene-card${isActive}" data-scene="${p.id}" role="button" tabindex="0" title="${p.name}">
                    <img src="${p.thumbnail_url}" alt="${p.name}" loading="lazy"
                         onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22120%22 height=%2268%22><rect width=%22120%22 height=%2268%22 fill=%22%23333%22/><text x=%2260%22 y=%2239%22 text-anchor=%22middle%22 fill=%22%23888%22 font-size=%2211%22>${p.name}</text></svg>'">
                    <span class="skin-scene-label">${p.name}</span>
                </div>`;
            }).join('');
    }

    // ── Build Footer ─────────────────────────────────────────
    function buildFooter() {
        const footer = _cfg.footer;
        if (!footer || !footer.enabled) return '';
        if (footer.style !== 'thumbnails') return '';

        const thumbsHtml = _panos
            .filter(p => !p.hidden)
            .sort((a, b) => (a.order || 0) - (b.order || 0))
            .map(p => {
                const isActive = p.id === _currentScene ? ' is-active' : '';
                return `
                <div class="skin-footer-thumb${isActive}" data-scene="${p.id}" title="${p.name}">
                    <img src="${p.thumbnail_url}" alt="${p.name}" loading="lazy">
                </div>`;
            }).join('');

        const fsBtn = footer.show_fullscreen
            ? `<button class="skin-fullscreen-btn" id="skin-fullscreen-btn" title="Tam Ekran">⛶</button>`
            : '';

        return `<div id="skin-footer">${thumbsHtml}${fsBtn}</div>`;
    }

    // ── Build Popup Container ─────────────────────────────────
    function buildPopupOverlay() {
        return `<div id="popup-overlay" role="dialog" aria-modal="true" aria-hidden="true"></div>`;
    }

    // ── Render Popup by ID ────────────────────────────────────
    function renderPopup(popupId) {
        const popup = (_cfg.popups || []).find(p => p.id === popupId);
        if (!popup) return;

        const overlay = el('popup-overlay');
        if (!overlay) return;

        const type = (popup.type || 'TEXT').toLowerCase();
        const width = popup.width || '600px';
        const height = popup.height || 'auto';

        const bodyHtml = buildPopupBody(popup, type);

        overlay.innerHTML = `
        <div class="skin-popup skin-popup--${type}" style="width:${width};min-height:50px"
             role="document" aria-labelledby="popup-title-${popupId}">
            <div class="skin-popup-header">
                <span class="skin-popup-title" id="popup-title-${popupId}">${popup.title || ''}</span>
                <button class="skin-popup-close" id="skin-popup-close" aria-label="Kapat">✕</button>
            </div>
            <div class="skin-popup-body" style="${type !== 'text' ? 'height:' + height : ''}">${bodyHtml}</div>
        </div>`;

        overlay.setAttribute('aria-hidden', 'false');
        requestAnimationFrame(() => overlay.classList.add('is-open'));

        // Events
        el('skin-popup-close').addEventListener('click', closePopup);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closePopup();
        });

        // Slider setup
        if (type === 'slider' && popup.images && popup.images.length) {
            _sliderIndexes[popupId] = 0;
            bindSlider(popupId, popup.images.length);
        }
    }

    function buildPopupBody(popup, type) {
        switch (type) {
            case 'text':
                return popup.content || '';

            case 'image':
                return `<img src="${popup.content}" alt="${popup.title || ''}">`;

            case 'video':
                return `<div class="skin-popup-video-wrap"><video controls src="${popup.content}" autoplay></video></div>`;

            case 'youtube':
            case 'iframe':
            case 'map': {
                // Accept either a full iframe HTML string or a plain URL
                const src = popup.content && popup.content.trim().startsWith('<')
                    ? popup.content  // already an iframe tag
                    : `<iframe src="${popup.content}" allowfullscreen allow="autoplay; encrypted-media"></iframe>`;
                return `<div class="skin-popup-video-wrap">${src}</div>`;
            }

            case 'slider': {
                const imgs = popup.images || [];
                return `
                <div class="skin-slider-wrap" style="position:relative;overflow:hidden">
                    <div class="skin-slider-track" id="slider-track-${popup.id}">
                        ${imgs.map(img => `<img src="${img.url}" alt="${img.caption || ''}">`).join('')}
                    </div>
                    ${imgs.length > 1 ? `
                    <button class="skin-slider-btn skin-slider-prev" data-popup="${popup.id}" data-dir="-1">‹</button>
                    <button class="skin-slider-btn skin-slider-next" data-popup="${popup.id}" data-dir="1">›</button>
                    ` : ''}
                </div>`;
            }

            case 'contact':
                return `<div class="skin-contact-body">${popup.content || ''}</div>`;

            default:
                return popup.content || '';
        }
    }

    function bindSlider(popupId, total) {
        qsa(`[data-popup="${popupId}"]`).forEach(btn => {
            btn.addEventListener('click', () => {
                const dir = parseInt(btn.dataset.dir, 10);
                const track = el(`slider-track-${popupId}`);
                if (!track) return;
                _sliderIndexes[popupId] = (_sliderIndexes[popupId] + dir + total) % total;
                track.style.transform = `translateX(-${_sliderIndexes[popupId] * 100}%)`;
            });
        });
    }

    // ── Scene Navigation ─────────────────────────────────────
    function goToScene(sceneId) {
        if (!sceneId || !_viewer) return;
        try {
            _viewer.loadScene(sceneId);
        } catch (e) {
            console.warn('[SkinEngine] loadScene error:', e);
        }
        setActiveScene(sceneId);
        _navOpen && toggleNav(false);
    }

    function setActiveScene(sceneId) {
        _currentScene = sceneId;

        // Update dropdown cards
        qsa('.skin-scene-card').forEach(c => {
            c.classList.toggle('is-active', c.dataset.scene === sceneId);
        });

        // Update footer thumbs
        qsa('.skin-footer-thumb').forEach(t => {
            t.classList.toggle('is-active', t.dataset.scene === sceneId);
        });

        // Scroll active footer thumb into view
        const activeThumb = qs(`.skin-footer-thumb.is-active`);
        if (activeThumb) {
            activeThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
    }

    // ── Navigation open/close ────────────────────────────────
    function toggleNav(forceState) {
        _navOpen = (forceState !== undefined) ? forceState : !_navOpen;
        const dropdown = el('skin-nav-dropdown');
        const trigger = el('skin-nav-trigger');
        if (dropdown) dropdown.classList.toggle('is-open', _navOpen);
        if (trigger) {
            trigger.classList.toggle('is-open', _navOpen);
            trigger.setAttribute('aria-expanded', String(_navOpen));
        }
    }

    // ── Popup open/close ─────────────────────────────────────
    function openPopup(popupId) {
        renderPopup(popupId);
    }

    function closePopup() {
        const overlay = el('popup-overlay');
        if (!overlay) return;
        overlay.classList.remove('is-open');
        overlay.setAttribute('aria-hidden', 'true');
        overlay.addEventListener('transitionend', () => {
            overlay.innerHTML = '';
        }, { once: true });
    }

    // ── Event Binding ────────────────────────────────────────
    function bindEvents(container) {
        // Nav trigger
        const trigger = el('skin-nav-trigger');
        if (trigger) trigger.addEventListener('click', () => toggleNav());

        // Category tabs
        container.addEventListener('click', (e) => {
            const catTab = e.target.closest('.skin-cat-tab');
            if (catTab) {
                _currentCat = catTab.dataset.cat;
                qsa('.skin-cat-tab').forEach(t => t.classList.toggle('is-active', t === catTab));
                const grid = el('skin-scene-grid');
                if (grid) {
                    grid.innerHTML = buildSceneCards(_currentCat);
                    bindSceneCards(grid);
                }
                return;
            }

            // Scene card in dropdown
            const sceneCard = e.target.closest('.skin-scene-card');
            if (sceneCard && sceneCard.dataset.scene) {
                goToScene(sceneCard.dataset.scene);
                return;
            }

            // Footer thumb
            const footerThumb = e.target.closest('.skin-footer-thumb');
            if (footerThumb && footerThumb.dataset.scene) {
                goToScene(footerThumb.dataset.scene);
                return;
            }

            // Custom button
            const customBtn = e.target.closest('.skin-custom-btn');
            if (customBtn) {
                const action = customBtn.dataset.action;
                const popupId = customBtn.dataset.popupId;
                const sceneId = customBtn.dataset.sceneId;
                if (action === 'popup' && popupId) openPopup(popupId);
                if (action === 'scene' && sceneId) goToScene(sceneId);
                return;
            }

            // Fullscreen button
            const fsBtn = e.target.closest('#skin-fullscreen-btn');
            if (fsBtn) {
                toggleFullscreen();
                return;
            }
        });

        // Keyboard: Escape closes nav and popup
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (_navOpen) toggleNav(false);
                else closePopup();
            }
        });

        // Close nav on outside click
        document.addEventListener('click', (e) => {
            if (!_navOpen) return;
            const nav = el('skin-nav-dropdown');
            const navTrig = el('skin-nav-trigger');
            if (nav && !nav.contains(e.target) && navTrig && !navTrig.contains(e.target)) {
                toggleNav(false);
            }
        });
    }

    function bindSceneCards(grid) {
        grid.querySelectorAll('.skin-scene-card').forEach(card => {
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    goToScene(card.dataset.scene);
                }
            });
        });
    }

    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => { });
        } else {
            document.exitFullscreen().catch(() => { });
        }
    }

    // ── Pannellum event hookup ────────────────────────────────
    function hookPannellumEvents() {
        if (!_viewer) return;
        _viewer.on('scenechange', (id) => setActiveScene(id));
    }

    // ── Main injection ───────────────────────────────────────
    function injectDom(configData) {
        let skinUI = document.getElementById('skin-ui');
        if (!skinUI) {
            skinUI = document.createElement('div');
            skinUI.id = 'skin-ui';
            document.body.appendChild(skinUI);
        }

        let popupOverlay = document.getElementById('popup-overlay');
        if (!popupOverlay) {
            popupOverlay = document.createElement('div');
            popupOverlay.id = 'popup-overlay';
            popupOverlay.setAttribute('role', 'dialog');
            popupOverlay.setAttribute('aria-modal', 'true');
            popupOverlay.setAttribute('aria-hidden', 'true');
            document.body.appendChild(popupOverlay);
        }

        skinUI.innerHTML =
            buildHeader() +
            buildNavDropdown() +
            buildFooter();

        return skinUI;
    }

    // ── Public: init ─────────────────────────────────────────
    function init(configData, viewer) {
        if (!configData || !configData.skin) {
            console.warn('[SkinEngine] configData.skin is missing — SkinEngine not initialized.');
            return;
        }

        _cfg = configData.skin;
        _panos = configData.panoramas || [];
        _viewer = viewer || null;

        // Determine starting scene
        _currentScene = (configData.default && configData.default.firstScene) || null;
        if (_panos.length && !_currentScene) _currentScene = _panos[0].id;

        // Apply theme CSS variables
        if (_cfg.theme) applyTheme(_cfg.theme);

        // Set custom thumb size
        if (_cfg.footer && _cfg.footer.thumbnail_size) {
            document.documentElement.style.setProperty('--skin-thumb-size', _cfg.footer.thumbnail_size);
        }

        // Inject DOM
        const container = injectDom(configData);

        // Bind events
        bindEvents(container);

        // Hook Pannellum
        hookPannellumEvents();

        // Set initial active state
        if (_currentScene) setActiveScene(_currentScene);

        console.log('[SkinEngine] Initialized. Theme:', _cfg.theme && _cfg.theme.preset, '| Scenes:', _panos.length);
    }

    // ── Public API ───────────────────────────────────────────
    return { init, goToScene, openPopup, closePopup, setActiveScene };

}());
