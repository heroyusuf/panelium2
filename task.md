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
- [ ] Add **🎨 Tema Ayarları** sub-panel to editor accordion (presets & color controls)
- [ ] Add **📐 Layout Ayarları** sub-panel (Header/Footer styling & element order)
- [ ] Add **📑 Sahne Yönetimi** sub-panel (category, order, visibility, thumbnail metadata)
- [ ] Add **🪟 Popup Yönetimi** sub-panel (CRUD operations for text/image/video/iframe popups)

## Phase 4: Asset Manager & Export Package
- [ ] Add `/upload_asset` and `/list_assets` endpoints to `editor_server.py`
- [ ] Add **📁 Asset Yönetimi** sub-panel to editor
- [ ] Add `/export_tour` zip generator endpoint to `editor_server.py`
- [ ] Add **📦 Dışa Aktar** sub-panel to editor
- [ ] Final end-to-end MVP verification
