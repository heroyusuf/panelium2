# Panelium2 MVP Tasks

## Phase 1: Config Migration & Skin Foundation
- [x] Migrate `config.json` schema to include `skin{}` and `panoramas[]` structures
- [x] Create `skin-engine.js` (JSON-driven UI render motor, Theme Engine, Layout, Popups, Navigation)
- [x] Create `skin.css` (CSS variables, Theme presets, Header/Footer styles, Popup layout variants)

## Phase 2: Viewer Integration
- [x] Update `viewer.html` to integrate `skin-engine.js` and `skin.css`
- [x] Unify popup and thumbnail rendering via `SkinEngine.init`
- [ ] Test scene navigation, auto-rotate, and popup overlays in viewer

## Phase 3: Editor Skin Panel Integration
- [x] Add **🎨 Tema Ayarları** sub-panel to editor accordion (presets & color controls)
- [x] Add **📐 Layout Ayarları** sub-panel (Header/Footer styling & element order)
- [x] Add **📑 Sahne Yönetimi** sub-panel (category, order, visibility, thumbnail metadata)
- [x] Add **🪟 Popup Yönetimi** sub-panel (CRUD operations for text/image/video/iframe popups)

## Phase 4: Asset Manager & Export Package
- [x] Add `/upload_asset` and `/list_assets` endpoints to `editor_server.py`
- [x] Add **📁 Asset Yönetimi** sub-panel to editor
- [x] Add `/export_tour` zip generator endpoint to `editor_server.py`
- [x] Add **📦 Dışa Aktar** sub-panel to editor
## Phase 5: Interactive Editor Improvements
- [x] Hotspot click-to-select with pulsing selection ring (`.hs-selected`)
- [x] Visual row highlight in hotspot list panel (`.hs-row-selected`)
- [x] Keyboard arrow fine-adjustment (0.1° / 1.0° with Shift)
- [x] Keyboard Delete/Backspace to remove selected hotspot
- [x] Keyboard Escape to deselect
- [x] Header extended properties: Width, Padding, Margin, Alignment, Background
- [x] Footer extended properties: Height, Padding, Margin, Alignment, Opacity, Background
- [x] `initSkinPanels()` updated to sync all new header/footer fields
- [x] Hover labels via CSS `[data-label]::before` pseudo-element
- [x] MutationObserver wires `data-label` onto all `.pnlm-hotspot` elements
- [x] Skin buttons tagged with `data-label` for hover tooltips
