# Panelium2 — MVP Implementation Plan

## Project Audit Summary

### Current Architecture (What Exists & Works)

| Module | File(s) | Status |
|---|---|---|
| **Panorama Viewer** | [viewer.html](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/viewer.html) + [pannellum.js](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/pannellum.js) | ✅ Working |
| **Hotspot Editor** | [editor.html](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/editor.html) (monolith) | ✅ Working |
| **Hotspot Drag & Drop** | Inline in editor.html | ✅ Working |
| **Scene Thumbnails** | Inline in editor.html + viewer.html | ✅ Working |
| **Auto-Rotate** | Inline in both files | ✅ Working |
| **Social Media** | Inline in both files | ✅ Working |
| **Skin Menu (ui_elements)** | Inline in both files | ✅ Basic — buttons with drag & popup |
| **Video Modal** | Inline in both files | ✅ Working |
| **Editor Server** | [editor_server.py](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/editor_server.py) | ✅ Working |
| **Tour Generator** | [generate_tour.py](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/generate_tour.py) | ✅ Working |
| **JSON Save/Load** | Via `/save_config` endpoint | ✅ Working |

### Current Data Model ([config.json](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/config.json))

```
├── default (firstScene, sceneFadeDuration, autoLoad, hotSpotDebug)
├── scenes{} (40 scenes, each with title, type, panorama, hotSpots[])
├── socialMedia[]
├── customAutoRotate{}
└── ui_elements[] (1 item — basic skin buttons)
```

**Missing from current config vs. ornek 1 reference:**
- `skin{}` — Theme Engine, Layout, Navigation, Popups
- `panoramas[]` — Scene metadata with categories, order, thumbnails

---

## Reference Analysis (Engineering Concepts Extracted)

### From `ornek 1/` (Most Relevant Reference)

| Concept | Architecture Pattern | Applicable to MVP? |
|---|---|---|
| **SkinEngine** (IIFE module) | JSON-driven render engine, separate from editor | ✅ YES — Critical |
| **Theme Engine** | CSS variables from config presets (luxury, glass, etc.) | ✅ YES |
| **Layout System** | Header/Footer with ordered, typed items (logo, nav, CTA, social, thumbnails) | ✅ YES |
| **Navigation System** | Categories → Scenes, collapsible categories, custom menus | ✅ YES |
| **Popup Framework** | Type-based renderer (TEXT, IMAGE, VIDEO, MAP, CONTACT, SLIDER, etc.) | ✅ YES — Critical |
| **Panoramas Array** | Scene metadata: name, category, order, thumbnail_url, hidden, icon_type | ✅ YES |
| **Split-Panel Editor** | 65/35 split layout with tabs | 🟡 Later — current editor layout is protected |
| **style.css (external)** | All CSS via variables, no hardcoded colors | ✅ YES |

### From `3d vista ornek/`

| Concept | What It Teaches |
|---|---|
| **Preloading strategy** | `<link rel="preload">` for cube-face panorama tiles |
| **Playlist architecture** | Scene sequencing via PlayList objects |
| **Skin asset naming** | State-based assets: `icon.png`, `icon_pressed.png`, `icon_rollover.png` |
| **Multi-state buttons** | hover/pressed/active states for all UI elements |
| **postMessage API** | Parent-iframe communication (`tourLoaded`, `pauseTour`) |

### From `skin ornek/`

| Concept | What It Teaches |
|---|---|
| **Skin visual themes** | Magazine, portfolio, enterprise, antique — different UI layouts over the same panorama engine |
| **Branding approach** | Full-bleed brand images, community themes |

---

## Gap Analysis (Current vs. MVP Requirements)

> [!IMPORTANT]
> Per PROJECT_VISION.md, the MVP must include: Panorama Viewer ✅, Scene Manager ✅, Hotspot Editor ✅, Asset Manager ✅, JSON Save/Load ✅, Popup Engine ✅, Skin Engine ✅, Export Package ✅

| # | Feature | Priority | Complexity | Status |
|---|---|---|---|---|
| 1 | **Skin Engine** (JSON-driven UI renderer) | 🔴 Critical | High | ✅ Completed (Phase 1 & 2) |
| 2 | **Popup Framework** (multi-type popup system) | 🔴 Critical | Medium | ✅ Completed (Phase 1 & 2) |
| 3 | **Panoramas Array + Scene Manager** (category/order metadata) | 🔴 Critical | Medium | ✅ Completed (Phase 3) |
| 4 | **Theme Engine** (CSS variable presets) | 🟡 High | Low | ✅ Completed (Phase 1) |
| 5 | **Config Migration** (add `skin{}` + `panoramas[]` to config.json) | 🔴 Critical | Low | ✅ Completed (Phase 1) |
| 6 | **Viewer Integration** (replace inline skin code with SkinEngine) | 🟡 High | Medium | ✅ Completed (Phase 2) |
| 7 | **Editor Skin Panel** (manage skin/popups/theme from editor) | 🟡 High | High | ✅ Completed (Phase 3) |
| 8 | **Asset Manager** (browse/upload icons, images) | 🟡 High | Medium | ✅ Completed (Phase 4) |
| 9 | **Export Package** (zip download of tour) | 🟢 Medium | Medium | ✅ Completed (Phase 4) |

---

## Proposed Changes

### Phase 1: Config Migration + Skin Foundation

> Extend config.json with the `skin{}` and `panoramas[]` structures. Create the `skin-engine.js` and `skin.css` files as separate modules. Wire them into `viewer.html`.

#### [NEW] [skin-engine.js](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/skin-engine.js)

JSON-driven UI render engine (IIFE module), adapted from the `ornek 1` reference architecture but implemented as an **original solution**. Responsibilities:
- Theme application (CSS variables from presets)
- Header/Footer layout rendering
- Navigation with categories + scene thumbnails
- Popup framework (TEXT, IMAGE, VIDEO, YOUTUBE, MAP, IFRAME, CONTACT, SLIDER)
- Video modal
- Social icons
- Scene navigation (`goToScene`)
- Active state tracking

#### [NEW] [skin.css](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/skin.css)

All skin UI styles using CSS variables. Sections:
- CSS custom properties (theme tokens)
- Header (floating/docked, top/bottom)
- Footer (thumbnails strip, fullscreen button)
- Navigation dropdown (categories, scenes, custom menus)
- Popup overlay + container (layout variants: text, image_left, image_right, etc.)
- Video modal
- Social bar
- CTA button
- Logo
- Animations (scale, slide, fade)
- Responsive breakpoints

#### [MODIFY] [config.json](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/config.json)

Add `skin{}` object (theme presets, logo, layout, navigation, popups) and `panoramas[]` array (scene metadata with categories). Existing data (`scenes`, `ui_elements`, `socialMedia`, `customAutoRotate`) remains untouched.

---

### Phase 2: Viewer Integration

#### [MODIFY] [viewer.html](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/viewer.html)

- Add `<link rel="stylesheet" href="skin.css"/>` to `<head>`
- Add `<script src="skin-engine.js"></script>` before inline script
- Add `<div id="skin-ui"></div>` and `<div id="popup-overlay"></div>` to body
- Replace inline `renderSocialMedia()`, `renderSkinMenu()`, `buildThumbnails()`, `openSkinModal()`, `closeSkinModal()` with `SkinEngine.init(configData, viewer)` call
- Remove duplicated CSS (social, skin-btn, thumbnail styles) — now handled by skin.css
- Keep inline auto-rotate and hotspot preparation logic (still needed, SkinEngine doesn't own these)

---

### Phase 3: Editor Skin Panel

#### [MODIFY] [editor.html](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/editor.html)

> [!WARNING]  
> The existing editor UI layout is **protected** per PROJECT_VISION.md. We will only **add** new sub-panels to the existing accordion structure — never move or redesign existing panels.

Add new sub-panels to the `#main-sidebar` accordion:
- **🎨 Tema Ayarları** — Theme preset selector + custom color pickers
- **📐 Layout Ayarları** — Header/footer toggle + style selector
- **📑 Sahne Yönetimi** — Panoramas array management (name, category, order, visibility, thumbnail)
- **🪟 Popup Yönetimi** — CRUD for popups (type, title, content, dimensions)

> Editor continues to work with the inline `configData` object. The new panels just read/write to `configData.skin`, `configData.panoramas`, `configData.skin.popups` sections. The `saveConfig()` function already serializes the entire `configData` — no changes needed there.

---

### Phase 4: Asset Manager + Export Package

#### [MODIFY] [editor_server.py](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/editor_server.py)

- Add `POST /upload_asset` — Accept file uploads to `icon/` or `jpeg/` directories
- Add `GET /list_assets` — List all files in `icon/` and `jpeg/` with metadata
- Add `GET /export_tour` — Generate a zip of the tour (config.json, viewer.html, skin-engine.js, skin.css, pannellum.js, pannellum.css, icon/, jpeg/)

#### [MODIFY] [editor.html](file:///mnt/4TBSSD/DALYAN_RESORT/panorama/birleştirilmiş/panelium2/editor.html)

- Add **📁 Asset Yönetimi** sub-panel (file browser, drag-drop upload)
- Add **📦 Dışa Aktar** sub-panel (export button, progress)

---

## Open Questions

> [!IMPORTANT]
> **Q1: Should `ui_elements[]` be migrated into `skin.navigation.custom_menus[]`?**  
> The current config has 1 item in `ui_elements` (a Google Maps iframe popup button). The `ornek 1` architecture handles this via `skin.navigation.custom_menus` + `skin.popups`. Migrating would unify the data model and let the SkinEngine render these buttons properly within the header/footer layout instead of as free-floating divs.  
> **Recommendation:** Yes — migrate the existing `ui_elements[0]` to `skin.navigation.custom_menus` + `skin.popups`, then deprecate `ui_elements` in the viewer. Editor can still manage these via the new Popup panel.

> [!IMPORTANT]
> **Q2: Should we start Phase 1+2 (Skin Engine + Viewer) together, or one at a time?**  
> They are tightly coupled — the SkinEngine file is only testable once the viewer loads it. Implementing both in one pass is more efficient.

> [!IMPORTANT]
> **Q3: Category list for scenes — should we use the ornek 1 defaults (Genel, Odalar, Havuz, Spa, Restoran, Bahçe) or let you define them?**  
> The ornek 1 reference uses hotel-specific categories. We can start with these as defaults since this is a Dalyan Resort tour.

---

## Verification Plan

### Automated Tests
```bash
# Verify config.json is valid JSON after migration
python3 -c "import json; json.load(open('config.json'))"

# Verify server starts without errors
timeout 3 python3 editor_server.py 2>&1 || true

# Verify all referenced files exist
ls -la skin-engine.js skin.css viewer.html editor.html config.json pannellum.js pannellum.css
```

### Manual Verification
1. Open `http://localhost:8000/viewer.html` — SkinEngine header/footer should render with theme
2. Click "Keşfet" navigation → categories and scenes should appear
3. Click a scene thumbnail → viewer navigates to that scene
4. Click a CTA/custom menu button → popup opens with correct content
5. Open `http://localhost:8000/editor.html` — all existing functionality still works
6. Test the new Tema/Layout/Popup sub-panels in editor
7. Save config → verify `skin{}` and `panoramas[]` are persisted
