import re

with open('editor.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Thumbnail Bar CSS
css_thumb = """
        /* Thumbnails Bar */
        #thumbnail-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 80px;
            background: rgba(0,0,0,0.7);
            display: flex;
            align-items: center;
            overflow-x: auto;
            white-space: nowrap;
            padding: 0 10px;
            box-sizing: border-box;
            z-index: 9999;
        }
        .thumb-item {
            display: inline-block;
            margin-right: 10px;
            padding: 5px 15px;
            background: #333;
            border: 2px solid transparent;
            border-radius: 5px;
            cursor: pointer;
            color: #fff;
            font-size: 14px;
            transition: 0.3s;
        }
        .thumb-item:hover, .thumb-item.active {
            border-color: #ffcc00;
            background: #555;
        }
"""
content = content.replace("</style>", css_thumb + "\n    </style>")

# 2. Add Thumbnail Bar HTML
html_thumb = """
<div id="thumbnail-bar"></div>
"""
content = content.replace('<div id="social-container-preview"></div>', '<div id="social-container-preview"></div>\n' + html_thumb)

# 3. Add buildThumbnails logic and patch scenechange
scenechange_logic = """
            viewer.on('scenechange', function(sceneId) {
                currentScene = sceneId;
                resetRotateCounter();
                refreshHotspotList();
                updateThumbnails();
            });
"""
content = re.sub(r"viewer\.on\('scenechange', function\(sceneId\) \{[\s\S]*?\}\);", scenechange_logic.strip(), content)

# 4. Add buildThumbnails and updateThumbnails to JS
js_thumb = """
    function buildThumbnails() {
        var tb = document.getElementById('thumbnail-bar');
        tb.innerHTML = '';
        for (var sid in configData.scenes) {
            var sc = configData.scenes[sid];
            var item = document.createElement('div');
            item.className = 'thumb-item';
            item.id = 'thumb-' + sid;
            item.textContent = sc.title || sid;
            item.onclick = (function(id) {
                return function() {
                    viewer.loadScene(id);
                };
            })(sid);
            tb.appendChild(item);
        }
        updateThumbnails();
    }
    
    function updateThumbnails() {
        var items = document.querySelectorAll('.thumb-item');
        items.forEach(function(el) { el.classList.remove('active'); });
        var active = document.getElementById('thumb-' + currentScene);
        if (active) {
            active.classList.add('active');
            active.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
    }
"""
content = content.replace("renderSocialMedia();", "renderSocialMedia();\n            buildThumbnails();")
content = content.replace("</script>", js_thumb + "\n</script>")

# 5. Fix custom icon tooltip
tooltip_logic_old = """
    window.customIconTooltipFunc = function(hotSpotDiv, args) {
        // Pannellum'un sprite / tip class'larını kaldır
        hotSpotDiv.classList.remove('pnlm-info', 'pnlm-scene', 'pnlm-sprite');
        hotSpotDiv.classList.add('custom-icon-hs');

        // Pannellum bazen asenkron olarak class ekleyebilir → izle ve temizle
        var obs = new MutationObserver(function() {
            hotSpotDiv.classList.remove('pnlm-info', 'pnlm-scene', 'pnlm-sprite');
            hotSpotDiv.classList.add('custom-icon-hs');
        });
        obs.observe(hotSpotDiv, { attributes: true, attributeFilter: ['class'] });
        setTimeout(function() { obs.disconnect(); }, 3000);

        var img = document.createElement('img');
        img.src = args;
        img.style.cssText = 'display:block;width:40px;height:40px;cursor:pointer;';
        hotSpotDiv.appendChild(img);
    };
"""
tooltip_logic_new = """
    window.customIconTooltipFunc = function(hotSpotDiv, args) {
        hotSpotDiv.classList.remove('pnlm-info', 'pnlm-scene', 'pnlm-sprite');
        hotSpotDiv.classList.add('custom-icon-hs');
        hotSpotDiv.innerHTML = ''; // Temizle
        var img = document.createElement('img');
        img.src = args;
        img.style.cssText = 'display:block;width:100%;height:100%;cursor:pointer;';
        hotSpotDiv.appendChild(img);
    };
"""
content = content.replace(tooltip_logic_old.strip(), tooltip_logic_new.strip())

# 6. Fix Drag and Drop issue (if dragging finishes, save is done successfully but ensure coords are mapped)
# Often, Pannellum captures drag. The custom drag prevents default properly.
# Also fix auto rotate speed bug
ar_fix = """
            if (autoScene) {
                arTotalDeg += step;
                if (arTotalDeg >= 360) {
                    arTotalDeg = 0;
                    autoAdvanceScene();
                    return;
                }
            }
            if (!isNaN(step) && step < 10) {
                var cy = viewer.getYaw();
                if (!isNaN(cy)) {
                    viewer.setYaw(cy + step, false);
                }
            }
"""
content = re.sub(r"if \(autoScene\) \{[\s\S]*?viewer\.setYaw\(viewer\.getYaw\(\) \+ step, false\);", ar_fix.strip(), content)

# Write back
with open('editor.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("editor.html patched.")
