import os
import subprocess

screens = [
    ('scene_2.png', 'screenshot_1_dashboard.png'),
    ('scene_3.png', 'screenshot_2_review_queue.png'),
    ('scene_3b.png', 'screenshot_3_attribute_editor.png'),
    ('scene_4.png', 'screenshot_4_audit_rollback.png'),
    ('scene_1.png', 'screenshot_5_apparel_filters.png'),
    ('scene_1.png', 'app_store_hero_feature_graphic.png'),
]

src_dir = r"C:\repo\gemini\catalogvision-landing-page\video_build"
dst_dir = r"C:\repo\gemini\catalogvision-landing-page\assets\screenshots"
os.makedirs(dst_dir, exist_ok=True)

for src_name, dst_name in screens:
    src_path = os.path.join(src_dir, src_name)
    dst_path = os.path.join(dst_dir, dst_name)
    cmd = f'ffmpeg -y -i "{src_path}" -vf "scale=1600:900:flags=lanczos" -frames:v 1 -update 1 "{dst_path}"'
    subprocess.run(cmd, shell=True, check=True)
    res = subprocess.check_output(f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "{dst_path}"', shell=True).decode().strip()
    size_kb = os.path.getsize(dst_path) / 1024
    print(f"{dst_name}: {res} ({size_kb:.1f} KB)")

print("\n[SUCCESS] All screenshots scaled to exactly 1600x900!")
