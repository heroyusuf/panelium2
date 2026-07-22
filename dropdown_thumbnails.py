import re

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace HTML
    content = content.replace('<div id="thumbnail-bar"></div>', 
"""<div id="scene-dropdown-container">
        <button id="scene-dropdown-btn" onclick="var tb = document.getElementById('thumbnail-bar'); tb.style.display = (tb.style.display === 'none' || tb.style.display === '') ? 'block' : 'none';">
            <span id="current-scene-title">Sahneler</span>
            <span style="font-size: 12px; margin-left: auto;">&#9660;</span>
        </button>
        <div id="thumbnail-bar" style="display: none;"></div>
    </div>""")

    # 2. Update CSS for thumbnail-bar
    old_thumb_bar_css = """
        #thumbnail-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            background: rgba(0,0,0,0.5);
            padding: 10px;
            box-sizing: border-box;
            overflow-x: auto;
            white-space: nowrap;
            z-index: 10;
        }"""
    
    new_thumb_bar_css = """
        #scene-dropdown-container {
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 20;
        }
        #scene-dropdown-btn {
            background: rgba(0,0,0,0.8);
            color: #fff;
            border: 1px solid #555;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            min-width: 250px;
            text-align: left;
        }
        #thumbnail-bar {
            position: absolute;
            bottom: 100%;
            left: 0;
            margin-bottom: 5px;
            width: 300px;
            max-height: 400px;
            background: rgba(0,0,0,0.9);
            border: 1px solid #444;
            border-radius: 5px;
            overflow-y: auto;
            padding: 5px;
            box-sizing: border-box;
            display: none;
        }"""
    
    # Simple replace string if it exists
    if old_thumb_bar_css.strip() in content:
        content = content.replace(old_thumb_bar_css.strip(), new_thumb_bar_css.strip())
    else:
        # regex replacement for #thumbnail-bar
        content = re.sub(r'#thumbnail-bar\s*\{[^}]*\}', new_thumb_bar_css.strip(), content)

    # 3. Update CSS for thumb-item
    old_thumb_item_css = """
        .thumb-item {
            display: inline-flex;
            align-items: center;
            margin-right: 10px;
            padding: 5px 15px;
            background: rgba(0,0,0,0.8);
            border: 2px solid transparent;
            border-radius: 5px;
            cursor: pointer;
            color: #fff;
            font-size: 14px;
            transition: 0.3s;
            min-width: max-content;
        }
        .thumb-item img {
            width: 50px;
            height: 50px;
            object-fit: cover;
            border-radius: 3px;
            margin-right: 10px;
        }
"""
    new_thumb_item_css = """
        .thumb-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
            padding: 8px 10px;
            background: rgba(0,0,0,0.5);
            border: 2px solid transparent;
            border-radius: 5px;
            cursor: pointer;
            color: #fff;
            font-size: 14px;
            transition: 0.3s;
            width: 100%;
            box-sizing: border-box;
        }
        .thumb-item:last-child {
            margin-bottom: 0;
        }
        .thumb-item img {
            width: 40px;
            height: 40px;
            object-fit: cover;
            border-radius: 3px;
            margin-right: 10px;
        }
"""
    
    if old_thumb_item_css.strip() in content:
        content = content.replace(old_thumb_item_css.strip(), new_thumb_item_css.strip())
    else:
        # Fallback regex
        content = re.sub(r'\.thumb-item\s*\{[^}]*\}', '', content)
        content = re.sub(r'\.thumb-item\s*img\s*\{[^}]*\}', '', content)
        # We assume it will just append or replace. We'll append it if not found exactly.
        if '.thumb-item' not in content:
             content = content.replace('</style>', new_thumb_item_css + '\n    </style>')

    # 4. JS updateThumbnails -> add title change
    old_update_js = """
    function updateThumbnails() {
        var current = viewer.getScene();
        var items = document.getElementsByClassName('thumb-item');
        for(var i=0; i<items.length; i++) {
            items[i].classList.remove('active');
        }
        var activeItem = document.getElementById('thumb-' + current);
        if (activeItem) {
            activeItem.classList.add('active');
            activeItem.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        }
    }
"""
    new_update_js = """
    function updateThumbnails() {
        var current = viewer.getScene();
        var items = document.getElementsByClassName('thumb-item');
        for(var i=0; i<items.length; i++) {
            items[i].classList.remove('active');
        }
        var activeItem = document.getElementById('thumb-' + current);
        if (activeItem) {
            activeItem.classList.add('active');
            activeItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            var btnTitle = document.getElementById('current-scene-title');
            if (btnTitle && configData.scenes[current]) {
                btnTitle.textContent = configData.scenes[current].title || current;
            }
        }
    }
"""
    if old_update_js.strip() in content:
        content = content.replace(old_update_js.strip(), new_update_js.strip())
    else:
        content = re.sub(r'function updateThumbnails\(\)\s*\{[^}]*\}', new_update_js.strip(), content)

    # 5. Hide on click in buildThumbnails
    # Replace viewer.loadScene(id); with viewer.loadScene(id); document.getElementById('thumbnail-bar').style.display = 'none';
    if "viewer.loadScene(id);" in content:
        content = content.replace("viewer.loadScene(id);", "viewer.loadScene(id);\n                    document.getElementById('thumbnail-bar').style.display = 'none';")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('editor.html')
update_file('viewer.html')

print("Dropdown list implemented successfully.")
