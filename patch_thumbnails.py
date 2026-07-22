import re

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. CSS update for .thumb-item
    old_css = """
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
"""
    new_css = """
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
    content = content.replace(old_css.strip(), new_css.strip())

    # 2. JS update for buildThumbnails()
    old_js = """
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
"""
    new_js = """
    function buildThumbnails() {
        var tb = document.getElementById('thumbnail-bar');
        tb.innerHTML = '';
        for (var sid in configData.scenes) {
            var sc = configData.scenes[sid];
            var item = document.createElement('div');
            item.className = 'thumb-item';
            item.id = 'thumb-' + sid;
            
            var imgPath = sc.panorama || '';
            var imgHtml = imgPath ? '<img src="' + imgPath + '" loading="lazy" alt="thumb">' : '';
            
            item.innerHTML = imgHtml + '<span>' + (sc.title || sid) + '</span>';
            
            item.onclick = (function(id) {
                return function() {
                    viewer.loadScene(id);
                };
            })(sid);
            tb.appendChild(item);
        }
        updateThumbnails();
    }
"""
    content = content.replace(old_js.strip(), new_js.strip())

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('editor.html')
update_file('viewer.html')

print("Thumbnails updated successfully.")
