import os
import subprocess

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
WORK_DIR = r"C:\repo\gemini\catalogvision-landing-page\video_build"
DST_DIR = r"C:\repo\gemini\catalogvision-landing-page\assets\screenshots"
os.makedirs(DST_DIR, exist_ok=True)

MAPPINGS = [
    ("scene_2_dashboard.html", "screenshot_1_dashboard.png"),
    ("scene_3_review_queue.html", "screenshot_2_review_queue.png"),
    ("scene_3b_edit_modal.html", "screenshot_3_attribute_editor.png"),
    ("scene_4_rollback.html", "screenshot_4_audit_rollback.png"),
    ("scene_1_intro.html", "screenshot_5_apparel_filters.png"),
    ("scene_1_intro.html", "app_store_hero_feature_graphic.png"),
]

for html_file, out_png in MAPPINGS:
    html_path = os.path.join(WORK_DIR, html_file)
    tmp_1080 = os.path.join(WORK_DIR, f"temp_{out_png}")
    final_out = os.path.join(DST_DIR, out_png)

    # 1. Capture with Chrome Headless
    chrome_cmd = [
        CHROME,
        "--headless=new",
        f"--screenshot={tmp_1080}",
        "--window-size=1920,1080",
        "--hide-scrollbars",
        html_path,
    ]
    res = subprocess.run(chrome_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Chrome failed on {html_file}: {res.stderr}")

    # 2. Scale to exact 1600x900 with ffmpeg Lanczos
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i",
        tmp_1080,
        "-vf",
        "scale=1600:900:flags=lanczos",
        "-frames:v",
        "1",
        "-update",
        "1",
        final_out,
    ]
    subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
    if os.path.exists(tmp_1080):
        os.remove(tmp_1080)

    # Verify resolution and size
    res_dim = subprocess.check_output(
        f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "{final_out}"',
        shell=True,
    ).decode().strip()
    size_kb = os.path.getsize(final_out) / 1024
    print(f"Rendered {out_png}: {res_dim} ({size_kb:.1f} KB)")

print("\n[SUCCESS] All screenshots completely re-rendered and updated!")
