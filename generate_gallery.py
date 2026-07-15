import re
import os

def get_clean_url_key(url):
    match = re.search(r"(https?://[^\?]+)", url)
    return match.group(1) if match else url

def parse_extracted_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} nahi mili!")
        return None

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    posts_raw = content.split("================================================================================")
    
    all_images_raw = [] 
    unique_images_by_post = [] 
    
    seen_global_urls = set()

    for block in posts_raw:
        if "POST ID:" not in block:
            continue
        
        post_id_match = re.search(r"POST ID:\s*(\d+)", block)
        if not post_id_match:
            continue
        post_id = post_id_match.group(1)

        image_blocks = block.split("Image ")
        post_unique_images = []

        for img_block in image_blocks[1:]:
            res_match = re.search(r"Resolution:\s*(\d+x\d+)", img_block)
            url_match = re.search(r"URL:\s*(https?://\S+)", img_block)
            
            if url_match:
                url = url_match.group(1)
                res = res_match.group(1) if res_match else "Unknown"
                
                all_images_raw.append({
                    "post_id": post_id,
                    "url": url,
                    "res": res
                })

                clean_key = get_clean_url_key(url)
                if clean_key not in seen_global_urls:
                    seen_global_urls.add(clean_key)
                    post_unique_images.append({
                        "url": url,
                        "resolution": res
                    })

        if post_unique_images:
            unique_images_by_post.append({
                "post_id": post_id,
                "images": post_unique_images
            })
            
    return {
        "all_raw": all_images_raw,
        "unique_posts": unique_images_by_post
    }

def get_category(resolution):
    if resolution == "Unknown":
        return "Other Media"
    try:
        w, h = map(int, resolution.split('x'))
        if w == h: return "Square Posts (1:1)"
        elif h > w:
            if h / w > 1.5: return "Reels / Stories (9:16)"
            return "Portrait Feed Posts (4:5)"
        else: return "Landscape Media"
    except:
        return "Other Media"

def generate_html(data_dict, output_html="index.html"):
    all_raw = data_dict["all_raw"]
    unique_posts = data_dict["unique_posts"]

    categories = {
        "Reels / Stories (9:16)": [],
        "Portrait Feed Posts (4:5)": [],
        "Square Posts (1:1)": [],
        "Landscape Media": [],
        "Other Media": []
    }

    for post in unique_posts:
        for img in post['images']:
            cat = get_category(img['resolution'])
            categories[cat].append({
                "post_id": post['post_id'],
                "url": img['url'],
                "res": img['resolution']
            })

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dual View Media Dashboard</title>
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #151f32;
            --text-main: #f1f5f9;
            --text-muted: #64748b;
            --accent: #38bdf8;
        }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 10px;
            border-bottom: 1px solid #1e293b;
        }
        header h1 { margin: 0; font-size: 2.3rem; color: var(--accent); }
        
        .tabs-container {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
        }
        .tab-btn {
            background-color: #1e293b;
            color: var(--text-main);
            border: 2px solid #334155;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .tab-btn:hover {
            border-color: var(--accent);
        }
        .tab-btn.active {
            background-color: var(--accent);
            color: #0b0f19;
            border-color: var(--accent);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }

        .category-section {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 35px;
            border: 1px solid #1e293b;
        }
        .category-title {
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            border-bottom: 2px solid #1e293b;
            padding-bottom: 10px;
        }
        .category-title span {
            background: #0284c7;
            padding: 2px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
        }
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
            gap: 15px;
        }
        .grid-item {
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            background-color: #0b0f19;
            aspect-ratio: 1 / 1;
            border: 1px solid #334155;
            transition: transform 0.2s, border-color 0.2s;
        }
        .grid-item:hover {
            transform: scale(1.04);
            border-color: var(--accent);
        }
        .grid-item img {
            width: 100%; height: 100%; object-fit: cover; display: block;
        }
        .info-overlay {
            position: absolute;
            bottom: 0; left: 0; right: 0;
            background: rgba(11, 15, 25, 0.85);
            padding: 6px;
            font-size: 0.72rem;
            display: flex;
            justify-content: space-between;
            backdrop-filter: blur(4px);
            border-top: 1px solid #1e293b;
        }
        .info-overlay a { color: var(--accent); text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Dual-View Media Portal</h1>
        </header>

        <div class="tabs-container">
            <button class="tab-btn active" onclick="switchTab('unique-view')">📊 Unique Dashboard</button>
            <button class="tab-btn" onclick="switchTab('all-view')">🎞️ All Raw Media ({len(all_raw)})</button>
        </div>

        <div id="unique-view" class="tab-content active">
"""

    for cat_name, items in categories.items():
        if not items: continue
        html_content += f"""
            <div class="category-section">
                <div class="category-title">{cat_name} <span>{len(items)} Unique Photos</span></div>
                <div class="image-grid">
        """
        for item in items:
            html_content += f"""
                    <div class="grid-item">
                        <img src="{item['url']}" loading="lazy" alt="Media">
                        <div class="info-overlay">
                            <span>Res: {item['res']}</span>
                            <a href="{item['url']}" target="_blank">🔗 Open</a>
                        </div>
                    </div>
            """
        html_content += "</div></div>"

    html_content += f"""
        </div>

        <div id="all-view" class="tab-content">
            <div class="category-section">
                <div class="category-title">All Extracted Media Sequence <span>Unfiltered History</span></div>
                <div class="image-grid">
"""

    for idx, item in enumerate(all_raw, 1):
        html_content += f"""
                    <div class="grid-item">
                        <img src="{item['url']}" loading="lazy" alt="Raw Image">
                        <div class="info-overlay">
                            <span>#{idx} | ID: ..{item['post_id'][-4:]}</span>
                            <a href="{item['url']}" target="_blank">🔗 View</a>
                        </div>
                    </div>
        """

    html_content += """
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"🎉 Portal Generated Successfully -> {output_html}")

if __name__ == "__main__":
    input_filename = "extracted_urls.txt" 
    print("⏳ Parsing complex dual structures...")
    data = parse_extracted_file(input_filename)
    if data:
        generate_html(data)
