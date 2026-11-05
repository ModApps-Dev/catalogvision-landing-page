import os
import subprocess
import json
import glob

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
WORK_DIR = r"C:\repo\gemini\catalogvision-landing-page\video_build"
ASSETS_DIR = r"C:\repo\gemini\catalogvision-landing-page\assets"
VOICE = "en-US-AvaNeural"

SCENES = [
    {
        "id": "scene_1",
        "html": os.path.join(WORK_DIR, "scene_1_intro.html"),
        "png": os.path.join(WORK_DIR, "scene_1.png"),
        "audio": os.path.join(WORK_DIR, "scene_1.mp3"),
        "video": os.path.join(WORK_DIR, "scene_1.mp4"),
        "text": "Are blank category metafields holding back your Shopify store's search and discovery filters? Manually tagging thousands of apparel items takes weeks of tedious data entry. Welcome to CatalogVision AI.",
        "zoom": "min(zoom+0.0006,1.06)",
    },
    {
        "id": "scene_2",
        "html": os.path.join(WORK_DIR, "scene_2_dashboard.html"),
        "png": os.path.join(WORK_DIR, "scene_2.png"),
        "audio": os.path.join(WORK_DIR, "scene_2.mp3"),
        "video": os.path.join(WORK_DIR, "scene_2.mp4"),
        "text": "With one click, CatalogVision AI analyzes your apparel catalog. Our multimodal vision pipeline examines product imagery and supplier descriptions to detect primary colors, patterns, necklines, and sleeve lengths with pinpoint accuracy.",
        "zoom": "min(zoom+0.0005,1.05)",
    },
    {
        "id": "scene_3",
        "html": os.path.join(WORK_DIR, "scene_3_review_queue.html"),
        "png": os.path.join(WORK_DIR, "scene_3.png"),
        "audio": os.path.join(WORK_DIR, "scene_3.mp3"),
        "video": os.path.join(WORK_DIR, "scene_3.mp4"),
        "text": "You never have to accept an all-or-nothing batch. In the Polaris review table, you have complete editorial control. Inspect transparent confidence scores, use bulk actions to approve or exclude products, or click Exclude on individual items with a single click.",
        "zoom": "min(zoom+0.0006,1.06)",
    },
    {
        "id": "scene_3b",
        "html": os.path.join(WORK_DIR, "scene_3b_edit_modal.html"),
        "png": os.path.join(WORK_DIR, "scene_3b.png"),
        "audio": os.path.join(WORK_DIR, "scene_3b.mp3"),
        "video": os.path.join(WORK_DIR, "scene_3b.mp4"),
        "text": "Need to adjust a specific tag? Click Edit on any product to open the Quick-Edit modal. Select from official Shopify Standard Product Taxonomy values, save your changes, and the product is instantly verified and approved.",
        "zoom": "min(zoom+0.0005,1.05)",
    },
    {
        "id": "scene_4",
        "html": os.path.join(WORK_DIR, "scene_4_rollback.html"),
        "png": os.path.join(WORK_DIR, "scene_4.png"),
        "audio": os.path.join(WORK_DIR, "scene_4.mp3"),
        "video": os.path.join(WORK_DIR, "scene_4.mp4"),
        "text": "When you publish, only approved items are written to Shopify, completely skipping excluded items. Our compare-and-set concurrency check guarantees manual edits are never overwritten, and our compensating rollback engine lets you revert any batch in seconds.",
        "zoom": "min(zoom+0.0005,1.05)",
    },
    {
        "id": "scene_5",
        "html": os.path.join(WORK_DIR, "scene_5_outro.html"),
        "png": os.path.join(WORK_DIR, "scene_5.png"),
        "audio": os.path.join(WORK_DIR, "scene_5.mp3"),
        "video": os.path.join(WORK_DIR, "scene_5.mp4"),
        "text": "Enrich your first fifty products completely free. Install CatalogVision AI on the Shopify App Store today.",
        "zoom": "min(zoom+0.0006,1.06)",
    },
]

def run(cmd):
    print("Executing:", cmd)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print("ERROR:", res.stderr)
        raise RuntimeError(res.stderr)
    return res

def get_audio_duration(file_path):
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def main():
    print("=== Step 1: Generating Screenshots from Chrome Headless ===")
    for s in SCENES:
        print(f"Capturing {s['id']}...")
        chrome_cmd = f'"{CHROME_PATH}" --headless=new --screenshot="{s["png"]}" --window-size=1920,1080 --hide-scrollbars "{s["html"]}"'
        run(chrome_cmd)

    print("\n=== Step 2: Generating Studio Voiceover with edge-tts ===")
    for s in SCENES:
        print(f"Generating TTS for {s['id']}...")
        tts_cmd = f'edge-tts --voice "{VOICE}" --text "{s["text"]}" --write-media "{s["audio"]}"'
        run(tts_cmd)

    print("\n=== Step 3: Rendering 1080p Video Segments ===")
    concat_list = []
    for s in SCENES:
        dur = get_audio_duration(s["audio"]) + 0.6 # slight buffer for smooth transition
        fps = 30
        frames = int(dur * fps)
        print(f"Rendering {s['id']} (Duration: {dur:.2f}s, Frames: {frames})...")

        filter_complex = f"zoompan=z='{s['zoom']}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps={fps},format=yuv420p"
        render_cmd = f'ffmpeg -y -loop 1 -i "{s["png"]}" -i "{s["audio"]}" -vf "{filter_complex}" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -t {dur} "{s["video"]}"'
        run(render_cmd)
        concat_list.append(s["video"])

    print("\n=== Step 4: Concatenating All Segments ===")
    concat_txt = os.path.join(WORK_DIR, "concat.txt")
    with open(concat_txt, "w") as f:
        for v in concat_list:
            f.write(f"file '{v.replace('\\', '/')}'\n")

    final_output = os.path.join(ASSETS_DIR, "catalogvision_demo.mp4")
    concat_cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_txt}" -c copy "{final_output}"'
    run(concat_cmd)

    total_dur = get_audio_duration(final_output)
    size_mb = os.path.getsize(final_output) / (1024 * 1024)
    print("\n[SUCCESS] DEMO VIDEO RENDERED SUCCESSFULLY!")
    print(f"Output File: {final_output}")
    print(f"Total Duration: {total_dur:.1f} seconds")
    print(f"File Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()
