import os
import json

def generate_config():
    jpeg_dir = 'jpeg'
    # List all jpeg files and sort them
    files = sorted([f for f in os.listdir(jpeg_dir) if f.lower().endswith(('.jpg', '.jpeg'))])
    
    if not files:
        print("No jpeg files found.")
        return
        
    config = {
        "default": {
            "firstScene": files[0].split('.')[0],
            "sceneFadeDuration": 1000,
            "autoLoad": True
        },
        "scenes": {}
    }
    
    for i, file in enumerate(files):
        scene_id = file.split('.')[0]
        
        # Determine previous and next scenes for a simple sequence tour
        prev_scene = files[i-1].split('.')[0] if i > 0 else None
        next_scene = files[i+1].split('.')[0] if i < len(files) - 1 else None
        
        hotspots = []
        if prev_scene:
            hotspots.append({
                "pitch": 0,
                "yaw": 180,
                "type": "scene",
                "text": "Önceki (Previous)",
                "sceneId": prev_scene,
                "targetYaw": 0
            })
        if next_scene:
            hotspots.append({
                "pitch": 0,
                "yaw": 0,
                "type": "scene",
                "text": "Sonraki (Next)",
                "sceneId": next_scene,
                "targetYaw": 0
            })
            
        config["scenes"][scene_id] = {
            "title": file,
            "type": "equirectangular",
            "panorama": f"jpeg/{file}",
            "hotSpots": hotspots
        }
        
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
        
    print(f"Generated config.json with {len(files)} scenes.")

if __name__ == '__main__':
    generate_config()
