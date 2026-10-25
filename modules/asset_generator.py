"""
Asset Generator Module
Generates realistic simulated construction site images and concrete crack pathology textures
for instant zero-dependency demonstration and testing.
"""

import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def ensure_assets_dir() -> str:
    """Ensures the assets directory exists."""
    os.makedirs("assets", exist_ok=True)
    return "assets"


def generate_sample_safety_image(scenario: str = "hazard_scaffold") -> Image.Image:
    """Generates a synthetic construction site scenario image using Pillow."""
    ensure_assets_dir()
    w, h = 800, 500
    img = Image.new("RGB", (w, h), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)

    # Background: Construction sky and concrete structure skeleton
    for y in range(h):
        # Sky gradient
        sky_r = int(20 + (y / h) * 40)
        sky_g = int(30 + (y / h) * 50)
        sky_b = int(50 + (y / h) * 70)
        draw.line([(0, y), (w, y)], fill=(sky_r, sky_g, sky_b))

    # Draw concrete building frame columns & slabs
    # Slabs
    draw.rectangle([50, 150, 750, 180], fill=(71, 85, 105), outline=(100, 116, 139), width=2)
    draw.rectangle([50, 320, 750, 350], fill=(71, 85, 105), outline=(100, 116, 139), width=2)

    # Columns
    draw.rectangle([80, 50, 130, 480], fill=(51, 65, 85), outline=(100, 116, 139), width=2)
    draw.rectangle([350, 50, 400, 480], fill=(51, 65, 85), outline=(100, 116, 139), width=2)
    draw.rectangle([650, 50, 700, 480], fill=(51, 65, 85), outline=(100, 116, 139), width=2)

    # Scaffolding tubular frames
    scaff_color = (203, 213, 225)
    for x_s in [180, 280, 460, 560]:
        draw.line([(x_s, 100), (x_s, 480)], fill=scaff_color, width=3)
    # Scaffolding cross braces (X-bracing)
    draw.line([(180, 180), (280, 320)], fill=(148, 163, 184), width=2)
    draw.line([(180, 320), (280, 180)], fill=(148, 163, 184), width=2)
    draw.line([(460, 180), (560, 320)], fill=(148, 163, 184), width=2)
    draw.line([(460, 320), (560, 180)], fill=(148, 163, 184), width=2)

    if scenario == "hazard_scaffold":
        # Scaffold hazard: Worker on upper staging (no harness, no helmet, unanchored)
        # Wooden plank platform
        draw.rectangle([160, 240, 300, 252], fill=(180, 83, 9), outline=(120, 53, 15))

        # Worker figure (Torso, limbs)
        wx, wy = 230, 200
        # Head (No Hardhat, brown cloth cap)
        draw.ellipse([wx - 10, wy - 35, wx + 10, wy - 15], fill=(120, 53, 15))
        # Torso (Blue shirt, NO neon vest)
        draw.rectangle([wx - 12, wy - 15, wx + 12, wy + 20], fill=(30, 58, 138))
        # Legs
        draw.line([(wx - 8, wy + 20), (wx - 8, wy + 40)], fill=(30, 41, 59), width=5)
        draw.line([(wx + 8, wy + 20), (wx + 8, wy + 40)], fill=(30, 41, 59), width=5)

        # Danger Annotations
        draw.rectangle([160, 120, 320, 150], fill=(239, 68, 68), outline=(255, 255, 255))
        draw.text((168, 125), "⚠️ NO HARNESS TETHER", fill=(255, 255, 255))

        # Uncapped rebar dowels at bottom
        for rx in range(160, 320, 25):
            draw.line([(rx, 480), (rx, 420)], fill=(148, 163, 184), width=4)
        draw.rectangle([150, 435, 330, 465], fill=(239, 68, 68), outline=(255, 255, 255))
        draw.text((155, 442), "⚠️ UNCAPPED REBAR HAZARD", fill=(255, 255, 255))

    elif scenario == "compliant_site":
        # Fully compliant workers with yellow helmets, high-vis neon vests
        # Guardrail on upper deck
        draw.line([(50, 140), (750, 140)], fill=(245, 158, 11), width=4)  # Top rail
        draw.line([(50, 160), (750, 160)], fill=(245, 158, 11), width=3)  # Mid rail

        for wx in [220, 500]:
            wy = 270
            # Safety Helmet (Yellow Hard Hat)
            draw.ellipse([wx - 14, wy - 42, wx + 14, wy - 20], fill=(234, 179, 8))
            draw.rectangle([wx - 16, wy - 24, wx + 16, wy - 20], fill=(202, 138, 4))
            # Torso with High-Vis Orange/Green Vest with Silver Reflective Stripes
            draw.rectangle([wx - 15, wy - 20, wx + 15, wy + 25], fill=(249, 115, 22))
            draw.line([(wx - 15, wy - 5), (wx + 15, wy - 5)], fill=(241, 245, 249), width=4)
            draw.line([(wx - 15, wy + 10), (wx + 15, wy + 10)], fill=(241, 245, 249), width=4)
            # Legs with steel-toe boots
            draw.line([(wx - 8, wy + 25), (wx - 8, wy + 50)], fill=(15, 23, 42), width=6)
            draw.line([(wx + 8, wy + 25), (wx + 8, wy + 50)], fill=(15, 23, 42), width=6)
            draw.rectangle([wx - 12, wy + 46, wx - 4, wy + 52], fill=(180, 83, 9))
            draw.rectangle([wx + 4, wy + 46, wx + 12, wy + 52], fill=(180, 83, 9))
            # Fall arrest lanyard tied to static line
            draw.line([(wx, wy - 5), (wx, 140)], fill=(59, 130, 246), width=3)

        draw.rectangle([180, 100, 480, 130], fill=(16, 185, 129), outline=(255, 255, 255))
        draw.text((190, 108), "✅ 100% PPE COMPLIANT: HELMETS, VESTS, DUAL SRL HARNESS", fill=(255, 255, 255))

    else:  # rcc deck
        # Slab rebar grid
        for rx in range(100, 700, 30):
            draw.line([(rx, 340), (rx + 40, 480)], fill=(100, 116, 139), width=3)
        for ry in range(350, 480, 25):
            draw.line([(100, ry), (700, ry)], fill=(100, 116, 139), width=3)

        # Worker standing on rebar
        wx, wy = 400, 290
        draw.ellipse([wx - 12, wy - 38, wx + 12, wy - 18], fill=(234, 179, 8))
        draw.rectangle([wx - 14, wy - 18, wx + 14, wy + 25], fill=(34, 197, 94))
        draw.line([(wx - 8, wy + 25), (wx - 8, wy + 50)], fill=(30, 41, 59), width=5)
        draw.line([(wx + 8, wy + 25), (wx + 8, wy + 50)], fill=(30, 41, 59), width=5)

        # Clutter / Scrap hazard on right
        draw.polygon([(560, 440), (620, 430), (600, 470)], fill=(180, 83, 9))
        draw.rectangle([520, 400, 710, 430], fill=(245, 158, 11), outline=(255, 255, 255))
        draw.text((530, 408), "⚠️ HOUSEKEEPING CLUTTER", fill=(15, 23, 42))

    return img


def generate_sample_crack_image(defect_type: str = "shear") -> Image.Image:
    """Generates a synthetic concrete surface texture with realistic crack morphology."""
    ensure_assets_dir()
    w, h = 800, 500

    # Concrete base texture
    img = Image.new("RGB", (w, h), color=(140, 140, 140))
    draw = ImageDraw.Draw(img)

    # Add realistic concrete aggregate noise
    random.seed(42)
    for _ in range(12000):
        nx = random.randint(0, w - 1)
        ny = random.randint(0, h - 1)
        shade = random.randint(110, 175)
        draw.point((nx, ny), fill=(shade, shade, shade))

    # Formwork joint lines
    draw.line([(0, 120), (w, 120)], fill=(100, 100, 100), width=2)
    draw.line([(0, 380), (w, 380)], fill=(100, 100, 100), width=2)
    draw.line([(300, 0), (300, h)], fill=(100, 100, 100), width=2)

    if defect_type == "shear":
        # 45-degree diagonal structural shear crack across concrete beam
        points = []
        cx, cy = 180, 420
        while cx < 620 and cy > 80:
            points.append((cx, cy))
            cx += random.randint(15, 25)
            cy -= random.randint(12, 22) + random.randint(-4, 4)

        # Draw main jagged crack
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            draw.line([p1, p2], fill=(20, 20, 20), width=6)
            # Secondary micro-branches
            if i % 3 == 0:
                bx = p1[0] + random.randint(-15, 15)
                by = p1[1] + random.randint(10, 25)
                draw.line([p1, (bx, by)], fill=(40, 40, 40), width=2)

        # Forensic scale marker
        draw.rectangle([40, 40, 220, 80], fill=(15, 23, 42), outline=(245, 158, 11), width=2)
        draw.text((50, 52), "SCALE: 100mm | BEAM SHEAR ZONE", fill=(245, 158, 11))

    elif defect_type == "spalling":
        # Spalling: Concrete cover popped off, exposed corroded rusty rebar
        draw.ellipse([260, 140, 540, 360], fill=(85, 75, 70), outline=(60, 50, 45), width=3)
        # Inner fractured core
        draw.ellipse([300, 170, 500, 330], fill=(55, 45, 40))

        # Corroded Rebars (Rust colored bars running vertically)
        rust_color = (180, 83, 9)
        rust_dark = (120, 53, 15)
        for rx in [360, 440]:
            draw.line([(rx, 110), (rx, 390)], fill=rust_dark, width=14)
            draw.line([(rx, 110), (rx, 390)], fill=rust_color, width=10)
            # Ribs on rebar
            for ry in range(120, 380, 12):
                draw.line([(rx - 6, ry), (rx + 6, ry)], fill=(217, 119, 6), width=3)

        draw.rectangle([40, 40, 240, 80], fill=(15, 23, 42), outline=(239, 68, 68), width=2)
        draw.text((50, 52), "DEFECT: SPALLING & CORROSION", fill=(239, 68, 68))

    elif defect_type == "settlement":
        # Stepped diagonal crack across masonry bed joints
        curr_x, curr_y = 200, 420
        while curr_x < 600 and curr_y > 100:
            # Horizontal step
            next_x = curr_x + random.randint(30, 50)
            draw.line([(curr_x, curr_y), (next_x, curr_y)], fill=(25, 25, 25), width=5)
            # Vertical step
            next_y = curr_y - random.randint(30, 50)
            draw.line([(next_x, curr_y), (next_x, next_y)], fill=(25, 25, 25), width=5)
            curr_x, curr_y = next_x, next_y

        draw.rectangle([40, 40, 240, 80], fill=(15, 23, 42), outline=(249, 115, 22), width=2)
        draw.text((50, 52), "DEFECT: STEPPED SETTLEMENT", fill=(249, 115, 22))

    elif defect_type == "thermal":
        # Straight vertical movement joint crack with spalled edges
        for y in range(80, 440, 10):
            offset = random.randint(-2, 2)
            draw.line([(400 + offset, y), (400 + offset, y + 10)], fill=(30, 30, 30), width=4)

        draw.rectangle([40, 40, 240, 80], fill=(15, 23, 42), outline=(234, 179, 8), width=2)
        draw.text((50, 52), "DEFECT: THERMAL MOVEMENT", fill=(234, 179, 8))

    else:  # Hairline
        # Fine spiderweb hairline cracks
        for _ in range(5):
            sx, sy = random.randint(250, 550), random.randint(180, 320)
            for _ in range(12):
                nx = sx + random.randint(-20, 20)
                ny = sy + random.randint(-20, 20)
                draw.line([(sx, sy), (nx, ny)], fill=(60, 60, 60), width=1)
                sx, sy = nx, ny

        draw.rectangle([40, 40, 220, 80], fill=(15, 23, 42), outline=(16, 185, 129), width=2)
        draw.text((50, 52), "DEFECT: HAIRLINE CRAZING", fill=(16, 185, 129))

    return img


def generate_all_sample_assets():
    """Generates and saves all sample assets to the assets/ directory."""
    ensure_assets_dir()

    safety_scenarios = {
        "sample_scaffold_hazard.jpg": "hazard_scaffold",
        "sample_site_compliant.jpg": "compliant_site",
        "sample_rcc_deck.jpg": "rcc_deck",
    }
    for filename, scenario in safety_scenarios.items():
        path = os.path.join("assets", filename)
        img = generate_sample_safety_image(scenario)
        img.save(path, "JPEG", quality=92)

    crack_scenarios = {
        "sample_crack_shear.jpg": "shear",
        "sample_crack_spalling.jpg": "spalling",
        "sample_crack_settlement.jpg": "settlement",
        "sample_crack_thermal.jpg": "thermal",
        "sample_crack_hairline.jpg": "hairline",
    }
    for filename, defect in crack_scenarios.items():
        path = os.path.join("assets", filename)
        img = generate_sample_crack_image(defect)
        img.save(path, "JPEG", quality=92)


if __name__ == "__main__":
    generate_all_sample_assets()
    print("All sample assets successfully generated in assets/")
