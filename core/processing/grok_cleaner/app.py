#!/usr/bin/env python3
"""PhotoDesk — Grok AI Real Estate Photo Editor"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json, os, threading, io, re, base64, time
import urllib.request, urllib.error, ssl
import certifi

# macOS: Python.org builds ship without system SSL certs.
# Use certifi's bundle instead of disabling verification.
_SSL_CTX = ssl.create_default_context(cafile=certifi.where())
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image as PILImage, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import rawpy
    HAS_RAWPY = True
except ImportError:
    HAS_RAWPY = False

HAS_REQUESTS = True  # urllib always available

# ─── Constants ───────────────────────────────────────────────────────────────

CONFIG_FILE = os.path.expanduser("~/.photodesk/grok_config.json")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
RAW_EXTENSIONS = {".dng", ".cr2", ".cr3", ".nef", ".arw", ".raf", ".rw2", ".orf", ".pef", ".srw", ".x3f", ".rwl"}
ALL_EXTENSIONS = IMAGE_EXTENSIONS | RAW_EXTENSIONS
FILE_TYPES = [("Все фото", "*.jpg *.jpeg *.png *.dng *.cr2 *.nef *.arw *.tif *.tiff *.webp"), ("Все файлы", "*.*")]

ROOM_TYPES = ["кухня", "спальня", "гостиная", "ванная", "коридор", "балкон", "двор", "дрон", "по умолчанию"]

ROOM_KEYWORDS = {
    "кухня":    ["кухн", "kitchen", "кух"],
    "спальня":  ["спальн", "bedroom", "кроват", "bed"],
    "гостиная": ["гостин", "living", "зал", "hall", "salon", "столов"],
    "ванная":   ["ванн", "bathroom", "туалет", "wc", "bath", "санузел"],
    "коридор":  ["коридор", "hallway", "прихожая", "входн", "entryway"],
    "балкон":   ["балкон", "balcony", "терраса", "terrace", "лоджия"],
    "двор":     ["двор", "yard", "exterior", "улиц", "фасад", "facade", "подъезд", "parking"],
    "дрон":     ["dji", "drone", "aerial", "dron", "аэро", "aeb", "fly"],
}

# ─── Default Prompts (Full Empty) ─────────────────────────────────────────────

DEFAULT_PROMPTS = {
    "кухня": (
        "You are a professional real estate photo editor specializing in virtual staging removal.\n\n"
        "TASK: Transform this kitchen photo into a completely empty, clean room ready for virtual staging.\n\n"
        "REMOVE completely:\n"
        "- All counter items: small appliances (toaster, kettle, coffee maker, blender, microwave if freestanding), "
        "dishes, bowls, pots, cutting boards, food containers, fruit bowls, jars, bottles, cooking utensils\n"
        "- All open shelf items: dishes, glasses, decorative items, books, plants\n"
        "- Freestanding furniture: kitchen island if movable, bar stools, chairs, tables\n"
        "- Rugs and mats on the floor\n"
        "- Curtains, blinds, window coverings\n"
        "- Fridge magnets, stickers, notes on appliances\n"
        "- Trash bins, recycling containers\n"
        "- All personal items and clutter\n\n"
        "KEEP (do NOT remove):\n"
        "- Built-in cabinets (upper and lower), cabinet doors and handles\n"
        "- Built-in appliances: integrated oven, integrated dishwasher, integrated fridge, range hood\n"
        "- Countertops and backsplash\n"
        "- Sink and faucet\n"
        "- Flooring\n"
        "- Ceiling lights and recessed lighting\n"
        "- Windows and window frames\n"
        "- Walls and architectural elements\n\n"
        "RESULT: A clean, completely empty kitchen showing only built-in elements. "
        "Countertops are bare. No items on any surface.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "спальня": (
        "You are a professional real estate photo editor specializing in virtual staging removal.\n\n"
        "TASK: Transform this bedroom photo into a completely empty, clean room ready for virtual staging.\n\n"
        "REMOVE completely:\n"
        "- Bed frame, mattress, all bedding (sheets, pillows, duvet, blankets, mattress topper)\n"
        "- All freestanding furniture: wardrobes (unless built-in), nightstands, dressers, chests of drawers, "
        "chairs, armchairs, ottomans, benches, desks, bookshelves\n"
        "- Rugs and carpets\n"
        "- Curtains and all window coverings\n"
        "- All wall art, pictures, paintings, posters, mirrors (freestanding or hung)\n"
        "- Lamps (floor lamps, table lamps, bedside lamps)\n"
        "- All personal items: clothes, shoes, bags, books, electronics, cables\n"
        "- Plants (potted or hanging)\n"
        "- Decorative items on all surfaces\n\n"
        "KEEP (do NOT remove):\n"
        "- Built-in closets and wardrobes with their doors\n"
        "- Flooring (hardwood, carpet, tiles — whatever is there)\n"
        "- Ceiling fixtures and recessed lights\n"
        "- Windows and window frames\n"
        "- Architectural moldings, baseboards, crown molding\n"
        "- Walls\n\n"
        "RESULT: A completely bare, empty bedroom. No furniture, no textiles, no personal items. "
        "Just the room shell with flooring and ceiling fixtures.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "гостиная": (
        "You are a professional real estate photo editor specializing in virtual staging removal.\n\n"
        "TASK: Transform this living room photo into a completely empty, clean room ready for virtual staging.\n\n"
        "REMOVE completely:\n"
        "- All furniture: sofas, sectionals, loveseats, armchairs, accent chairs, coffee tables, "
        "side tables, TV stand, TV/monitor, entertainment center, bookshelves, bookcases, "
        "display cabinets, ottomans, poufs, benches\n"
        "- Rugs and carpets\n"
        "- Curtains, drapes, blinds, all window coverings\n"
        "- All wall art, pictures, paintings, posters, mirrors, clocks\n"
        "- Floor lamps, table lamps, all portable lighting\n"
        "- All decorative items: vases, plants, sculptures, candles, photo frames\n"
        "- Electronics and cables\n"
        "- Cushions and throws\n\n"
        "KEEP (do NOT remove):\n"
        "- Built-in shelving units integrated into walls\n"
        "- Fireplace surround and mantel if architecturally fixed\n"
        "- Flooring\n"
        "- Ceiling fixtures, chandeliers (ceiling-mounted only), recessed lights\n"
        "- Windows and window frames\n"
        "- Walls, baseboards, architectural trim\n\n"
        "RESULT: A completely empty living room. No furniture, no rugs, no decor. "
        "Only the room structure remains visible.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "ванная": (
        "You are a professional real estate photo editor specializing in virtual staging removal.\n\n"
        "TASK: Clean this bathroom photo by removing all personal items while keeping all fixtures.\n\n"
        "REMOVE completely:\n"
        "- All personal care products: shampoo, conditioner, soap, body wash, toothpaste, toothbrushes, "
        "razors, skincare products, perfume, cologne\n"
        "- Towels and bath mats\n"
        "- Shower curtain (if not built-in glass)\n"
        "- Toilet paper and toilet paper holders that are freestanding\n"
        "- All items on countertops and shelves\n"
        "- Trash bins\n"
        "- Laundry baskets\n"
        "- All personal items\n\n"
        "KEEP (do NOT remove):\n"
        "- Toilet\n"
        "- Sink and vanity cabinet\n"
        "- Bathtub\n"
        "- Shower enclosure (glass doors, tiles, fixtures)\n"
        "- All tiles (wall and floor)\n"
        "- Towel bars and towel rings (empty)\n"
        "- Mirrors (fixed to wall)\n"
        "- Lighting fixtures\n"
        "- Faucets and shower hardware\n"
        "- Built-in storage\n\n"
        "RESULT: A clean, empty bathroom showing all fixtures and tiles but no personal items.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "коридор": (
        "You are a professional real estate photo editor specializing in virtual staging removal.\n\n"
        "TASK: Transform this hallway/entryway photo into a completely empty space.\n\n"
        "REMOVE completely:\n"
        "- Shoes, shoe racks, shoe cabinets (if freestanding)\n"
        "- Coats, jackets, hats on hooks or coat rack (keep empty hooks)\n"
        "- Bags, umbrellas, walking sticks\n"
        "- Rugs and floor mats\n"
        "- Pictures, mirrors, wall decor\n"
        "- Freestanding furniture: benches, consoles, side tables\n"
        "- Decorative items, plants\n"
        "- All personal items\n\n"
        "KEEP (do NOT remove):\n"
        "- Built-in storage units, closets, wardrobes\n"
        "- Coat hooks (empty)\n"
        "- Flooring\n"
        "- Doors and door frames\n"
        "- Ceiling lights\n"
        "- Architectural elements, baseboards, trim\n"
        "- Walls\n\n"
        "RESULT: A completely empty hallway. No items on the floor, no coats, no shoes, no decor.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "балкон": (
        "You are a professional real estate photo editor specializing in virtual staging removal.\n\n"
        "TASK: Transform this balcony/terrace photo into a completely empty outdoor space.\n\n"
        "REMOVE completely:\n"
        "- All furniture: chairs, armchairs, sun loungers, tables, sofas, benches\n"
        "- All plants (potted, hanging, in planters)\n"
        "- Storage boxes, tool boxes, crates\n"
        "- Rugs and floor coverings\n"
        "- Decorative items, lanterns, candles\n"
        "- Drying laundry, drying racks\n"
        "- Bicycles, scooters, sports equipment\n"
        "- Trash bins\n\n"
        "KEEP (do NOT remove):\n"
        "- Railing and balustrade\n"
        "- Flooring/decking\n"
        "- Ceiling or overhead pergola if permanently fixed\n"
        "- Walls and structural elements\n"
        "- Built-in lighting\n\n"
        "RESULT: A completely bare balcony/terrace. Only the structural elements remain.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "двор": (
        "You are a professional real estate photo editor specializing in virtual staging removal.\n\n"
        "TASK: Transform this exterior/yard photo into a clean, empty outdoor space.\n\n"
        "REMOVE completely:\n"
        "- All vehicles (cars, motorcycles, bicycles, boats)\n"
        "- Garden furniture (chairs, tables, benches, sun loungers, parasols)\n"
        "- Potted plants and movable planters\n"
        "- Garden tools, hoses, lawnmowers\n"
        "- Children's toys, playsets, trampolines\n"
        "- Trash bins and recycling containers\n"
        "- Temporary structures (tents, pop-up shelters)\n"
        "- Clothes lines and drying racks\n"
        "- All personal items and clutter\n\n"
        "KEEP (do NOT remove):\n"
        "- Buildings and permanent structures\n"
        "- Trees and permanent landscaping (hedges, lawn, permanent garden beds)\n"
        "- Pathways, driveways, patios\n"
        "- Fences and permanent gates\n"
        "- Permanent outdoor lighting\n"
        "- Built-in features (pergolas, built-in BBQ, permanent pool)\n\n"
        "RESULT: A clean exterior with only permanent features. No vehicles, no movable furniture, no clutter.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "дрон": (
        "You are a professional real estate aerial photo editor.\n\n"
        "TASK: Enhance this aerial photograph for maximum real estate marketing impact.\n\n"
        "ENHANCE:\n"
        "- Sky: If sky is gray or dull, replace with a bright blue sky with beautiful photorealistic white clouds. "
        "Sun position should be natural.\n"
        "- Colors: Boost saturation and vibrancy of grass, trees, and buildings.\n"
        "- Contrast: Increase overall contrast and clarity.\n"
        "- Horizon: Straighten if slightly tilted.\n\n"
        "PRESERVE: All buildings, roads, landscape, vehicles — keep exact positions and shapes.\n\n"
        "QUALITY: Professional real estate aerial photography. Magazine-quality result.\n\n"
        "IMPORTANT: Do NOT remove or add structures. Maintain exact geometry and perspective."
    ),
    "по умолчанию": (
        "You are a professional real estate photo editor specializing in virtual staging removal.\n\n"
        "TASK: Transform this room photo into a completely empty, clean space ready for virtual staging.\n\n"
        "REMOVE completely:\n"
        "- All furniture: every piece including sofas, chairs, tables, beds, wardrobes, shelves\n"
        "- All personal items\n"
        "- Rugs and floor coverings\n"
        "- Curtains and window coverings\n"
        "- All decorative items, plants, pictures, lamps\n"
        "- All clutter and loose items\n\n"
        "KEEP (do NOT remove):\n"
        "- Built-in elements and architectural features\n"
        "- Flooring\n"
        "- Ceiling fixtures (ceiling-mounted)\n"
        "- Windows and window frames\n"
        "- Walls, baseboards, architectural trim\n\n"
        "RESULT: A completely empty room showing only the room structure.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
}

# ─── Declutter Prompts (Keep furniture, remove clutter) ───────────────────────

DECLUTTER_PROMPTS = {
    "кухня": (
        "You are a professional real estate photo editor and virtual stager.\n\n"
        "TASK: Declutter and clean up this kitchen photo to make it look professionally staged.\n\n"
        "KEEP in place — do NOT remove:\n"
        "- All appliances (refrigerator, oven, microwave, dishwasher, coffee maker, etc.)\n"
        "- All furniture (table, chairs, bar stools, kitchen island)\n"
        "- 1-2 tasteful, intentional decorative items per surface (a fruit bowl, a plant, a nice vase)\n"
        "- Decorative plants or herbs on the windowsill or counter\n\n"
        "REMOVE only genuine clutter:\n"
        "- Dirty or unwashed dishes in the sink or on counters\n"
        "- Open food containers, half-eaten food, grocery bags\n"
        "- Random bottles, jars, cluttered containers crowding countertops\n"
        "- Fridge magnets, sticky notes, papers, children's drawings on appliances\n"
        "- Visible trash in bins or on surfaces\n"
        "- Excessive items crowding any surface beyond 1-2 intentional items\n\n"
        "RESULT: A clean, professionally staged kitchen. Countertops are nearly clear. "
        "Everything looks like it was arranged by a professional photographer.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "спальня": (
        "You are a professional real estate photo editor and virtual stager.\n\n"
        "TASK: Declutter and clean up this bedroom photo to make it look professionally staged.\n\n"
        "KEEP in place — do NOT remove:\n"
        "- Bed frame, headboard, mattress — keep the bed exactly where it is\n"
        "- All furniture in their current positions (wardrobes, nightstands, dressers, chairs)\n"
        "- Artwork, paintings, and pictures hanging on walls\n"
        "- Neatly arranged books on shelves or nightstands\n"
        "- Decorative plants and flowers\n"
        "- Tasteful, intentional decorative items (vases, sculptures, lamps)\n"
        "- Mirrors fixed to wall\n\n"
        "REMOVE only genuine clutter:\n"
        "- Clothes thrown on the floor, chairs, or draped over furniture\n"
        "- Personal toiletries and hygiene items on surfaces\n"
        "- Open suitcases, travel bags, shopping bags\n"
        "- Chargers, cables, electronic clutter on surfaces\n"
        "- Children's toys scattered on the floor or bed\n"
        "- Too many random personal items cluttering nightstands or dressers\n\n"
        "ENHANCE — bed styling:\n"
        "- Make the bed look perfectly made: smooth, wrinkle-free sheets\n"
        "- Pillows plump and neatly arranged\n"
        "- Duvet or bedspread flat, symmetrical, hotel-quality presentation\n\n"
        "RESULT: A clean, inviting bedroom. Bed looks hotel-perfect. Furniture stays. "
        "Surfaces are tidy. Design elements remain.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "гостиная": (
        "You are a professional real estate photo editor and virtual stager.\n\n"
        "TASK: Declutter and clean up this living room photo to make it look professionally staged.\n\n"
        "KEEP in place — do NOT remove:\n"
        "- All furniture (sofas, armchairs, coffee table, TV unit, bookshelves, dining table)\n"
        "- Artwork, paintings, and pictures hanging on walls\n"
        "- Books neatly arranged on shelves — keep them exactly as organized\n"
        "- Decorative plants and flowers\n"
        "- Tasteful vases, sculptures, and intentional decorative objects\n"
        "- Neatly placed cushions and throws\n"
        "- Rugs in their place\n\n"
        "REMOVE only genuine clutter:\n"
        "- Children's toys scattered on the floor, sofa, or table\n"
        "- Newspapers, magazines, papers in disarray\n"
        "- Scattered remote controls, chargers, cables\n"
        "- Food, drinks, dishes, glasses left out\n"
        "- Personal clothing or bags left on furniture\n"
        "- General everyday mess that doesn't belong in a staged photo\n\n"
        "RESULT: A clean, professionally staged living room. All furniture and intentional design "
        "elements stay. Only random clutter is removed.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "ванная": (
        "You are a professional real estate photo editor and virtual stager.\n\n"
        "TASK: Declutter and clean up this bathroom photo to make it look professionally staged.\n\n"
        "KEEP in place:\n"
        "- All fixtures (toilet, sink, bathtub, shower)\n"
        "- 1-2 neatly folded towels (make them look hotel-quality)\n"
        "- Clean, minimal decor\n\n"
        "REMOVE only the clutter:\n"
        "- All personal care products cluttering countertops (toothbrushes, soap, shampoo, etc.)\n"
        "- Damp towels on floor or draped messily\n"
        "- Visible soap scum or grime\n"
        "- Items on toilet tank\n"
        "- Clutter on any surface\n\n"
        "RESULT: A clean, spa-like bathroom. Surfaces nearly bare. Any remaining towels look "
        "perfectly folded and hotel-quality.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "коридор": (
        "You are a professional real estate photo editor and virtual stager.\n\n"
        "TASK: Declutter and clean up this hallway/entryway photo.\n\n"
        "KEEP in place:\n"
        "- Furniture (bench, console table if present)\n"
        "- Intentional, tasteful decor\n\n"
        "REMOVE only the clutter:\n"
        "- Scattered shoes on the floor\n"
        "- Coats and bags piled messily\n"
        "- Umbrellas and random items by the door\n"
        "- General entry clutter\n\n"
        "RESULT: A tidy, welcoming entryway. No scattered items on the floor.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "балкон": (
        "You are a professional real estate photo editor and virtual stager.\n\n"
        "TASK: Declutter and clean up this balcony/terrace photo.\n\n"
        "KEEP in place:\n"
        "- Balcony furniture (chairs, table)\n"
        "- Neat, healthy-looking plants\n\n"
        "REMOVE only the clutter:\n"
        "- Scattered items\n"
        "- Unkempt, dead, or overgrown plants\n"
        "- Visible storage boxes\n"
        "- Drying laundry\n"
        "- General balcony clutter\n\n"
        "RESULT: A clean, inviting balcony that looks ready for outdoor living.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "двор": (
        "You are a professional real estate photo editor and virtual stager.\n\n"
        "TASK: Declutter and clean up this exterior/yard photo.\n\n"
        "KEEP in place:\n"
        "- All permanent elements\n"
        "- Vehicles parked in designated parking spots\n"
        "- Garden furniture\n\n"
        "REMOVE only the clutter:\n"
        "- Scattered garden tools\n"
        "- Children's toys on the lawn\n"
        "- Trash and debris\n"
        "- Temporary items out of place\n"
        "- General yard clutter\n\n"
        "RESULT: A clean, tidy exterior that presents well for real estate marketing.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
    "дрон": (
        "You are a professional real estate aerial photo editor.\n\n"
        "TASK: Enhance this aerial photograph for maximum real estate marketing impact.\n\n"
        "ENHANCE:\n"
        "- Sky: If sky is gray or dull, replace with a bright blue sky with beautiful photorealistic white clouds. "
        "Sun position should be natural.\n"
        "- Colors: Boost saturation and vibrancy of grass, trees, and buildings.\n"
        "- Contrast: Increase overall contrast and clarity.\n"
        "- Horizon: Straighten if slightly tilted.\n\n"
        "PRESERVE: All buildings, roads, landscape, vehicles — keep exact positions and shapes.\n\n"
        "QUALITY: Professional real estate aerial photography. Magazine-quality result.\n\n"
        "IMPORTANT: Do NOT remove or add structures. Maintain exact geometry and perspective."
    ),
    "по умолчанию": (
        "You are a professional real estate photo editor and virtual stager.\n\n"
        "TASK: Declutter and clean up this room photo to make it look professionally staged.\n\n"
        "KEEP in place — do NOT remove:\n"
        "- All furniture and appliances in their current positions\n"
        "- Artwork and paintings on walls\n"
        "- Neatly arranged books on shelves\n"
        "- Decorative plants and flowers\n"
        "- Intentional, tasteful decorative items\n\n"
        "REMOVE only genuine clutter:\n"
        "- Scattered personal items, clothing, toys\n"
        "- Cables, chargers, electronic clutter\n"
        "- Food, dishes, glasses left out\n"
        "- General mess and disarray that doesn't belong in a staged property\n\n"
        "RESULT: A clean, professionally staged room. All furniture and design elements stay. "
        "Only clutter is removed.\n\n"
        "IMPORTANT: Maintain exact perspective, geometry, and photorealistic quality. "
        "Do NOT add any new items. Do NOT change architecture or structure."
    ),
}

# ─── Sky Presets ──────────────────────────────────────────────────────────────

SKY_PRESETS = {
    "☀️  День (чистое небо)": {
        "suffix": "_day_clear",
        "prompt": (
            "You are a professional real estate photo editor.\n\n"
            "TASK: Replace the sky and update the lighting in this photo.\n\n"
            "SKY: Replace with a perfectly clear, bright blue sky. No clouds whatsoever. "
            "Pure azure blue, the kind of sky you see at 11AM on a perfect summer day. "
            "The blue should be deep and saturated at the zenith, slightly lighter near the horizon.\n\n"
            "LIGHTING: Strong, direct sunlight from above. Crisp, well-defined shadows. "
            "Warm, bright daylight illuminating all surfaces.\n\n"
            "FOR INTERIOR PHOTOS: Bright warm sunlight should stream through all windows, "
            "creating clean light patches on the floor and walls near windows. "
            "The overall interior should feel bright and sun-filled.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: Replace the actual sky visible in the photo with the described sky. "
            "Adjust the lighting on buildings, grass, and surfaces to match direct sunlight.\n\n"
            "QUALITY: Photorealistic. The final result should be indistinguishable from a real photograph "
            "taken on a perfect clear sunny day.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and the quality of light entering the space."
        ),
    },
    "☀️  День (пышные облака)": {
        "suffix": "_day_clouds",
        "prompt": (
            "You are a professional real estate photo editor.\n\n"
            "TASK: Replace the sky and update the lighting in this photo.\n\n"
            "SKY: Beautiful blue sky with large, puffy white cumulus clouds. The clouds should look "
            "dramatic and photogenic — bright white on top, slightly grey underneath. "
            "About 40-50% cloud coverage. Blue sky visible between the clouds. "
            "Time of day: 2PM, mid-afternoon.\n\n"
            "LIGHTING: Slightly diffused, soft light from partial cloud cover. "
            "Bright but not harsh. Soft shadows.\n\n"
            "FOR INTERIOR PHOTOS: Bright, soft, diffused light through windows. "
            "Gentle, flattering illumination without harsh direct sunlight. "
            "The interior should look airy and inviting.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: Replace the actual sky with the described sky. "
            "Natural, balanced lighting on all surfaces.\n\n"
            "QUALITY: Photorealistic. Magazine-quality real estate photography.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and light quality."
        ),
    },
    "🌤  День (лёгкая облачность)": {
        "suffix": "_day_partial",
        "prompt": (
            "You are a professional real estate photo editor.\n\n"
            "TASK: Replace the sky and update the lighting in this photo.\n\n"
            "SKY: Partly cloudy sky with about 50% cloud coverage. Mix of blue sky and white/light grey clouds. "
            "The overall feel is light, airy, and pleasant. Scattered clouds of varying sizes. "
            "Some areas of pure blue sky visible. Bright and cheerful atmosphere.\n\n"
            "LIGHTING: Gentle, even, diffused light. Bright without being harsh or contrasty. "
            "The kind of light that makes everything look naturally beautiful.\n\n"
            "FOR INTERIOR PHOTOS: Soft, even light through windows. No harsh sun beams, just a pleasant "
            "bright illumination that fills the space evenly. The interior looks welcoming and comfortable.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: Replace actual sky. Balanced, natural lighting on all surfaces.\n\n"
            "QUALITY: Photorealistic. The result should look like a naturally well-lit day.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and ambient light."
        ),
    },
    "🌅  Golden Hour (чистое небо)": {
        "suffix": "_golden_clear",
        "prompt": (
            "You are a professional real estate photo editor specializing in golden hour photography.\n\n"
            "TASK: Transform this photo to golden hour lighting with a clear sky.\n\n"
            "SKY: Clear golden hour sky, approximately 30 minutes before sunset. "
            "The horizon glows with warm orange-gold. The sky transitions from deep, rich orange at the horizon "
            "through golden yellow to a deep blue at the zenith. No clouds — pure gradient of warm to cool. "
            "The sun is low, just above the horizon, casting long shadows.\n\n"
            "LIGHTING: Warm, golden, directional light from low on the horizon. "
            "Everything is bathed in beautiful golden light. Long, dramatic shadows. "
            "The warmth should be orange-golden, not yellow.\n\n"
            "FOR INTERIOR PHOTOS: Stunning golden light streaming through windows at a low angle. "
            "Golden patches and elongated shadow patterns on the floor and walls. "
            "The entire interior is warmed with a gorgeous orange-gold glow. "
            "Interior ambient light is warm and inviting.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: Replace actual sky. All surfaces glowing with warm golden light. "
            "Building facades lit beautifully by warm directional sunlight.\n\n"
            "QUALITY: Cinematic, magazine-quality real estate photography at its finest.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and lighting."
        ),
    },
    "🌅  Golden Hour (пышные облака)": {
        "suffix": "_golden_clouds",
        "prompt": (
            "You are a professional real estate photo editor specializing in dramatic sunset photography.\n\n"
            "TASK: Transform this photo to golden hour with spectacular dramatic clouds.\n\n"
            "SKY: Golden hour with absolutely spectacular cumulus clouds. The clouds are massive and dramatic, "
            "lit from below by the setting sun in brilliant orange, pink, gold, and deep red. "
            "The undersides of clouds glow with intense warm color. "
            "Between the clouds: deep blue sky transitioning to orange near the horizon. "
            "This is the kind of sky that stops people in their tracks.\n\n"
            "LIGHTING: Intense warm golden-orange light from the low sun breaking through clouds. "
            "Dramatic contrast between lit and shadow areas. Warm amber tones everywhere.\n\n"
            "FOR INTERIOR PHOTOS: Stunning warm amber light flooding through windows. "
            "The interior is transformed with beautiful golden-orange light. "
            "Dramatic and breathtaking — the kind of photo that sells properties instantly.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: The entire scene is transformed by the spectacular sky. "
            "Buildings glow warm gold in the dramatic light.\n\n"
            "QUALITY: Absolutely stunning, award-winning real estate photography.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and lighting."
        ),
    },
    "🌅  Golden Hour (перистые облака)": {
        "suffix": "_golden_cirrus",
        "prompt": (
            "You are a professional real estate photo editor specializing in atmospheric photography.\n\n"
            "TASK: Transform this photo to golden hour with delicate wispy clouds.\n\n"
            "SKY: Beautiful golden hour sky with wispy, feathery cirrus clouds catching the last light. "
            "The thin, high-altitude clouds are painted in soft pink, warm orange, and delicate gold. "
            "They form elegant streaks and wisps across the sky. "
            "The background sky transitions from warm orange-gold at the horizon to soft purple-blue at top. "
            "Romantic, painterly, and beautiful.\n\n"
            "LIGHTING: Soft, warm golden light diffused through high clouds. "
            "Gentle golden warmth without harsh shadows. Romantic and flattering light.\n\n"
            "FOR INTERIOR PHOTOS: Soft, warm golden light through windows. "
            "A gentle golden glow fills the space. Romantic and inviting atmosphere. "
            "Warm tones on all surfaces.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: The delicate sky creates a beautiful backdrop. "
            "Soft warm light on all surfaces.\n\n"
            "QUALITY: Elegant, sophisticated real estate photography.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and lighting."
        ),
    },
    "🌄  Закат (алый горизонт)": {
        "suffix": "_sunset_red",
        "prompt": (
            "You are a professional real estate photo editor specializing in dramatic sunset photography.\n\n"
            "TASK: Transform this photo to a vivid, dramatic red-orange sunset.\n\n"
            "SKY: Extremely vivid and dramatic sunset with the sun right at the horizon. "
            "The sky is a spectacular gradient: deep, rich red at the very bottom/horizon, "
            "transitioning to bright orange, then purple-magenta in the middle, "
            "then deep dark blue-purple at the top of the sky. "
            "This is the most dramatic possible sunset — vivid, saturated, and breathtaking. "
            "If there are clouds, they are dramatically lit in deep red and orange.\n\n"
            "LIGHTING: Very strong orange-red light from the horizon. "
            "The entire scene is bathed in intense warm red-orange light. "
            "Strong contrast between the vivid exterior and lit interior.\n\n"
            "FOR INTERIOR PHOTOS: Strong, dramatic orange-red light streams through windows. "
            "The interior has a warm, fiery glow from outside. Interior lights are on and warm, "
            "creating beautiful contrast with the intense sunset outside.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: The dramatic red sky dominates. "
            "Building surfaces catch the deep orange-red light.\n\n"
            "QUALITY: Dramatic, cinematic real estate photography. Impact is maximum.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and lighting."
        ),
    },
    "🌆  Сумерки (синяя волна)": {
        "suffix": "_twilight_blue",
        "prompt": (
            "You are a professional real estate photo editor specializing in blue hour photography.\n\n"
            "TASK: Transform this photo to the magical blue hour twilight.\n\n"
            "SKY: Perfect blue hour, approximately 20 minutes after sunset. "
            "The sky is a deep, rich, cool blue — the iconic 'blue hour' color. "
            "At the horizon there is still a faint narrow band of warm orange-amber "
            "where the sun has just set, transitioning quickly to the deep blue. "
            "The sky is uniformly dark blue with no stars yet visible.\n\n"
            "LIGHTING: The ambient light is cool and blue. "
            "Interior lights are on and glowing warmly, creating a beautiful warm-cool contrast. "
            "The contrast between warm interior light and cool blue exterior is a hallmark of "
            "professional real estate photography.\n\n"
            "FOR INTERIOR PHOTOS: The space is lit by warm interior lighting. "
            "Through the windows, the deep blue twilight sky is visible with the faint orange at the horizon. "
            "The warm interior against the cool blue exterior creates a stunning, inviting atmosphere.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: The building is illuminated by exterior lights. "
            "Windows glow warm yellow-white. The deep blue sky creates a dramatic backdrop. "
            "STREET LIGHTING: All street lamps and outdoor lanterns on the surrounding streets "
            "and pathways are glowing with warm yellow-orange light. "
            "Lamp posts cast realistic pools of warm light on the pavement and sidewalks. "
            "If there are parked cars, their surfaces faintly reflect the streetlights. "
            "Traffic lights, shop signs, and any visible urban lighting elements are on. "
            "The entire street scene feels alive with warm artificial light against the cool blue sky.\n\n"
            "QUALITY: Classic professional real estate photography. The blue hour look that every "
            "real estate photographer dreams of.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and lighting."
        ),
    },
    "🌆  Сумерки (тёплые тона)": {
        "suffix": "_twilight_warm",
        "prompt": (
            "You are a professional real estate photo editor specializing in twilight photography.\n\n"
            "TASK: Transform this photo to warm, romantic twilight lighting.\n\n"
            "SKY: Warm twilight sky with beautiful pink and purple tones. "
            "The sun has just set and the sky shows: soft pink near the horizon, "
            "transitioning through lavender and light purple in the middle, "
            "to deep purple-blue at the top. "
            "A faint warm orange or golden glow lingers at the horizon. "
            "Soft, romantic, and absolutely beautiful.\n\n"
            "LIGHTING: Warm twilight ambient light with soft purple-pink tones from the sky. "
            "Interior lights are on and glowing warmly.\n\n"
            "FOR INTERIOR PHOTOS: The interior is warmly lit. Through the windows, "
            "the beautiful pink-purple twilight sky is visible. "
            "The warm interior lighting combined with the romantic outside sky "
            "creates a magical, inviting atmosphere.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: The warm pink-purple sky creates a stunning backdrop. "
            "Exterior lights are on, windows glow warm. "
            "STREET LIGHTING: Street lamps and pathway lanterns glow with warm amber light, "
            "casting romantic pools of light on the pavement. "
            "The warm streetlights complement the pink-purple twilight sky beautifully. "
            "The whole scene feels magical and romantic.\n\n"
            "QUALITY: Romantic, magazine-quality real estate photography.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and lighting."
        ),
    },
    "🌃  Ночь (звёздное небо)": {
        "suffix": "_night_stars",
        "prompt": (
            "You are a professional real estate photo editor specializing in night photography.\n\n"
            "TASK: Transform this photo to a stunning night scene with a star-filled sky.\n\n"
            "SKY: Clear, dark night sky absolutely filled with thousands of stars. "
            "The stars are bright, twinkling, and varied in size and brightness. "
            "If the composition allows, show a hint of the Milky Way as a soft, hazy band of light "
            "arching across the sky. The sky is deep black-blue, and the stars are spectacular.\n\n"
            "LIGHTING: Night lighting. Exterior is dark except for artificial lights. "
            "Interior lights are on and glowing warmly and brightly.\n\n"
            "FOR INTERIOR PHOTOS: The interior is brightly lit with warm light. "
            "Through the windows, the spectacular star-filled night sky is visible. "
            "The warm glow of the interior contrasts beautifully with the dark night outside. "
            "The stars visible through the windows add a magical, aspirational quality.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: The building is lit by exterior lighting. "
            "All windows glow warm yellow. The star-filled sky creates a breathtaking backdrop. "
            "If there is a pool or water feature, it reflects the stars. "
            "STREET LIGHTING: Street lamps cast bright pools of warm-white light on the dark pavement. "
            "Lamp posts are clearly visible and glowing. "
            "Road surface has wet-look reflections of streetlights for maximum drama. "
            "Any visible traffic lights, neon signs, or commercial lighting is on and adds to the urban glow. "
            "The contrast between the dark night sky full of stars and the warm street lighting "
            "below creates a cinematic, aspirational atmosphere.\n\n"
            "QUALITY: Stunning, aspirational real estate photography.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and lighting."
        ),
    },
    "🌃  Ночь (лунный свет)": {
        "suffix": "_night_moon",
        "prompt": (
            "You are a professional real estate photo editor specializing in moonlit night photography.\n\n"
            "TASK: Transform this photo to a beautiful moonlit night scene.\n\n"
            "SKY: Night sky with a large, beautiful, photorealistic full moon prominently visible. "
            "The moon should be photorealistic — showing craters and surface details. "
            "Around the moon, a soft halo of light. The sky is dark blue-black with scattered stars. "
            "The moonlight casts a soft, cool, silver-blue light on all exterior surfaces.\n\n"
            "LIGHTING: Cool silver-blue moonlight from the moon's direction. "
            "Soft, dramatic shadows cast by moonlight. "
            "Interior lights are on and glowing with warm yellow light.\n\n"
            "FOR INTERIOR PHOTOS: The interior is lit with warm lights on. "
            "Through the windows, the moonlit night sky is visible with the moon prominent. "
            "Soft silver-blue moonlight may enter the room slightly, "
            "creating a beautiful contrast with the warm interior lights.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: The building and landscape are bathed in silver-blue moonlight. "
            "Windows glow warm yellow. The moon is dramatically visible in the sky. "
            "If there is water or glass, it reflects the moonlight. "
            "STREET LIGHTING: Street lamps glow with warm-white or sodium-yellow light, "
            "creating a striking contrast with the cool silver moonlight. "
            "Lamp posts and their light pools are clearly visible on the pavement. "
            "The mix of cool moonlight and warm street lamps creates a dramatic, "
            "cinematic lighting composition. Road surfaces may show reflections of both "
            "the moon and the streetlights.\n\n"
            "QUALITY: Dramatic, cinematic, aspirational real estate photography.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and lighting."
        ),
    },
    "💡  Вечер (подсветка)": {
        "suffix": "_evening_lit",
        "prompt": (
            "You are a professional real estate photo editor specializing in evening architectural photography.\n\n"
            "TASK: Transform this photo to the magical evening 'all lights on' look.\n\n"
            "SKY: Early evening sky, just after sunset. Deep blue sky (darker than blue hour) "
            "with the very last traces of warm orange still visible at the horizon. "
            "The sky is the classic deep blue that makes lit buildings pop.\n\n"
            "LIGHTING — ALL LIGHTS ON:\n"
            "- Interior lights: Every room visible through windows is FULLY LIT with warm yellow-white light. "
            "Windows glow bright and warm.\n"
            "- Exterior spotlights: Architectural spotlights illuminate the building facade.\n"
            "- Garden lights: Any visible garden, pathway, or landscape lighting is on.\n"
            "- Entry lighting: Entrance and doorway lights are on.\n"
            "This is the 'hero shot' of real estate photography — everything is lit perfectly.\n\n"
            "FOR INTERIOR PHOTOS: The interior is beautifully lit with all lights on. "
            "Through the windows, the deep blue evening sky is visible "
            "with warm exterior lighting visible outside. "
            "The contrast between warm interior and cool blue exterior is perfect.\n\n"
            "FOR EXTERIOR/BALCONY PHOTOS: The building is a masterpiece of illumination. "
            "Every window glows warm, spotlights illuminate the facade, "
            "pathway lights line the entrance, and the deep blue sky creates the perfect backdrop. "
            "STREET LIGHTING: All street lamps on surrounding streets are on and glowing warmly. "
            "Lamp posts cast wide, overlapping pools of warm light on the pavement. "
            "If there is a road or sidewalk visible, it shows wet-look or polished reflections "
            "of the streetlights, adding depth and luxury to the scene. "
            "Traffic lights, business signs, and any other urban lighting elements are on. "
            "The street scene around the property is fully lit, making the property look "
            "like it's in a premium, well-maintained neighborhood. "
            "This looks like a magazine cover for an architectural publication.\n\n"
            "QUALITY: The pinnacle of professional real estate photography. "
            "This shot should make anyone want to immediately buy or rent this property.\n\n"
            "IMPORTANT: Do NOT change any interior elements, furniture, or architecture. "
            "Only change the sky and lighting."
        ),
    },
}

# ─── Universal prompt suffix (appended to every API call) ────────────────────

DEFECT_PRESERVATION = (
    "\n\nCRITICAL — PRESERVE ALL PHYSICAL DEFECTS: Do NOT fix, hide, mask, or improve any existing "
    "physical damage or imperfections. You MUST keep ALL of the following exactly as they appear in the original:\n"
    "- Wall stains, water damage marks, moisture streaks, yellowing\n"
    "- Peeling, flaking, cracked, or bubbling paint\n"
    "- Cracks in walls, ceiling, or floor tiles\n"
    "- Chipped, broken, or worn-out tiles, flooring, or baseboards\n"
    "- Dirty, discolored, or stained surfaces\n"
    "- Broken, missing, or damaged fixtures\n"
    "- Scuff marks, scratches, dents, holes in walls\n"
    "These defects are legally and ethically required for honest real estate disclosure. "
    "The output must reflect 100% authentic physical condition of the property."
)

PROMPT_FOOTER = (
    "\n\nOUTPUT QUALITY: Generate at the MAXIMUM available resolution — 2K (2048 pixels on the long side). "
    "Use the highest quality output with maximum detail, sharpness, and photorealism. "
    "The result must look like a professional photograph taken with a high-end camera.\n\n"
    "REFLECTIONS REMOVAL: Carefully inspect ALL reflective surfaces in the image — "
    "mirrors, windows, glass panels, TV screens, glossy floors, kitchen appliances, bathroom tiles, "
    "shower glass, picture frames, and any other reflective surfaces. "
    "Remove any reflections of: the photographer, the camera, the tripod, lighting equipment, "
    "or any other photography equipment. Replace removed reflections with the correct, "
    "realistic background content that should logically be visible in that reflection "
    "(e.g., the opposite wall, furniture, or the view outside). "
    "The final image must show zero trace of any photography equipment in any reflection."
)

# ─── Config ───────────────────────────────────────────────────────────────────

def detect_room_type(filename: str) -> str:
    low = filename.lower()
    for room_type, keywords in ROOM_KEYWORDS.items():
        for kw in keywords:
            if kw.strip("_") in low:
                return room_type
    return "по умолчанию"


def detect_room_type_ai(image_path: str, api_key: str) -> str:
    """Uses Grok vision model to detect room type from the actual image content.
    Falls back to filename-based detection on any error."""
    try:
        png_bytes = _to_png_bytes(image_path, max_side=512)
        b64 = base64.b64encode(png_bytes).decode("utf-8")
        data_uri = f"data:image/png;base64,{b64}"

        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "grok-2-vision-1212",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_uri}},
                        {"type": "text", "text": (
                            "This is a real estate photo. Identify the room type.\n"
                            "Reply with EXACTLY ONE Russian word from this list — no other text:\n"
                            "кухня / спальня / гостиная / ванная / коридор / балкон / двор / дрон / по умолчанию\n\n"
                            "кухня — kitchen with counters, cabinets, appliances\n"
                            "спальня — bedroom with a bed\n"
                            "гостиная — living room, dining room, lounge area\n"
                            "ванная — bathroom, toilet, shower room\n"
                            "коридор — hallway, entryway, corridor\n"
                            "балкон — balcony, terrace, loggia\n"
                            "двор — exterior, yard, facade, garden, parking lot\n"
                            "дрон — aerial or drone photo from above\n"
                            "по умолчанию — any other or unclear space\n"
                            "Reply with only the single Russian word."
                        )}
                    ]
                }
            ],
            "temperature": 0,
            "max_tokens": 15,
        }

        result = _xai_post(url, headers, payload, timeout=30, retries=2, retry_delay=3)
        detected = result["choices"][0]["message"]["content"].strip().lower()

        for room in ROOM_TYPES:
            if room in detected:
                return room
        return "по умолчанию"
    except Exception:
        return detect_room_type(Path(image_path).name)


def load_config() -> dict:
    defaults = {
        "api_key": "",
        "output_folder": str(Path.home() / "photodesk" / "grok_output"),
        "workers": 2,
        "model": "grok-imagine-image",
        "empty_prompts": dict(DEFAULT_PROMPTS),
        "declutter_prompts": dict(DECLUTTER_PROMPTS),
        "sky_prompts": {name: d["prompt"] for name, d in SKY_PRESETS.items()},
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for key in ["api_key", "output_folder", "workers", "model"]:
                if key in saved:
                    defaults[key] = saved[key]
            for pkey in ["empty_prompts", "declutter_prompts", "sky_prompts"]:
                if pkey in saved:
                    defaults[pkey].update(saved[pkey])
        except Exception:
            pass
    return defaults


def save_config(cfg: dict):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ─── API Functions ────────────────────────────────────────────────────────────

def _to_png_bytes(image_path: str, max_side: int = 2048) -> bytes:
    """Конвертирует изображение в PNG (в памяти). Поддерживает RAW/DNG через rawpy."""
    ext = Path(image_path).suffix.lower()

    if ext in RAW_EXTENSIONS:
        if HAS_RAWPY:
            with rawpy.imread(image_path) as raw:
                rgb = raw.postprocess(
                    use_camera_wb=True,
                    half_size=False,
                    no_auto_bright=False,
                    output_bps=8,
                )
            img = PILImage.fromarray(rgb)
        else:
            raise RuntimeError(
                f"Файл {Path(image_path).name} — RAW-формат, но rawpy не установлен.\n"
                "Установите: pip install rawpy"
            )
    elif HAS_PIL:
        img = PILImage.open(image_path).convert("RGB")
    else:
        with open(image_path, "rb") as f:
            return f.read()

    if max(img.width, img.height) > max_side:
        img.thumbnail((max_side, max_side), PILImage.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def _xai_post(url: str, headers: dict, payload: dict, timeout: int = 180,
               retries: int = 3, retry_delay: int = 10) -> dict:
    """Выполняет POST-запрос к xAI API с автоматическим повтором при 500/503."""
    data = json.dumps(payload).encode("utf-8")
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
                body = resp.read()
                return json.loads(body)
        except urllib.error.HTTPError as e:
            status = e.code
            raw = e.read().decode("utf-8", errors="ignore")
            try:
                detail = json.loads(raw)
            except Exception:
                detail = raw[:300] or e.reason

            if status == 403:
                raise RuntimeError(
                    f"403 Нет доступа — {detail}\n"
                    "Проверьте API ключ в настройках. "
                    "Убедитесь, что ключ имеет доступ к /v1/images/edits."
                )

            if status in (404, 405):
                raise RuntimeError(f"{status} — {detail}")

            if status in (429, 500, 503) and attempt < retries:
                last_exc = RuntimeError(f"{status} — {detail}")
                time.sleep(retry_delay * attempt)
                continue

            raise RuntimeError(f"{status} — {detail}")
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(retry_delay)
            continue

    raise last_exc or RuntimeError("Все попытки исчерпаны")


def process_image_xai(image_path: str, prompt: str, api_key: str,
                       model: str = "grok-imagine-image") -> bytes:
    """Отправляет фото в xAI API (JSON) и возвращает обработанные байты изображения."""
    png_bytes = _to_png_bytes(image_path)
    b64 = base64.b64encode(png_bytes).decode("utf-8")
    data_uri = f"data:image/png;base64,{b64}"

    url = "https://api.x.ai/v1/images/edits"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "image": data_uri,
        "n": 1,
    }

    result = _xai_post(url, headers, payload)
    item = result["data"][0]

    # API может вернуть либо b64_json, либо URL
    if "b64_json" in item and item["b64_json"]:
        return base64.b64decode(item["b64_json"])

    # Скачиваем по URL
    img_url = item.get("url", "")
    if not img_url:
        raise RuntimeError(f"API не вернул изображение: {result}")
    req = urllib.request.Request(img_url)
    with urllib.request.urlopen(req, timeout=60, context=_SSL_CTX) as resp:
        return resp.read()


def build_prompt(base: str, preserve_defects: bool = True) -> str:
    """Appends defect preservation + quality + reflection-removal footer to any prompt."""
    result = base.rstrip()
    if preserve_defects:
        result += DEFECT_PRESERVATION
    result += PROMPT_FOOTER
    return result


# ─── Main Application ─────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PhotoDesk — Grok AI Real Estate Editor")
        self.geometry("1100x800")
        self.minsize(900, 650)

        self.cfg = load_config()

        # Tab 1 state
        self._clean_stop = threading.Event()
        self._clean_running = False
        self._clean_rows = []  # list of dicts: {iid, path, room_var, mode_var, checked}

        # Tab 2 state
        self._sky_stop = threading.Event()
        self._sky_running = False
        self._sky_files = []  # list of full paths — parallel with treeview rows

        # Thumbnail state (keep references to avoid GC)
        self._clean_thumb_ref = None
        self._sky_thumb_ref = None

        self._build_ui()

    # ─── UI Build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self._tab_clean = ttk.Frame(self.notebook)
        self._tab_sky = ttk.Frame(self.notebook)
        self._tab_prompts = ttk.Frame(self.notebook)
        self._tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self._tab_clean, text="  Очистка  ")
        self.notebook.add(self._tab_sky, text="  Небо & Свет  ")
        self.notebook.add(self._tab_prompts, text="  Промпты  ")
        self.notebook.add(self._tab_settings, text="  Настройки  ")

        self._build_tab_clean()
        self._build_tab_sky()
        self._build_tab_prompts()
        self._build_tab_settings()

    # ─── Tab 1: Очистка ───────────────────────────────────────────────────────

    def _build_tab_clean(self):
        parent = self._tab_clean
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)
        parent.rowconfigure(3, weight=1)

        # ── Left side ─────────────────────────────────────────────────────────

        # Folders frame
        frm_folders = ttk.LabelFrame(parent, text="Папки")
        frm_folders.grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=(8, 4))
        frm_folders.columnconfigure(1, weight=1)

        ttk.Label(frm_folders, text="Источник:").grid(row=0, column=0, sticky="w", padx=6, pady=3)
        self._clean_input_var = tk.StringVar()
        ttk.Entry(frm_folders, textvariable=self._clean_input_var).grid(row=0, column=1, sticky="ew", padx=4, pady=3)
        ttk.Button(frm_folders, text="Выбрать...", command=self._clean_browse_input).grid(row=0, column=2, padx=4, pady=3)

        ttk.Label(frm_folders, text="Результат:").grid(row=1, column=0, sticky="w", padx=6, pady=3)
        self._clean_output_var = tk.StringVar(value=self.cfg.get("output_folder", ""))
        ttk.Entry(frm_folders, textvariable=self._clean_output_var).grid(row=1, column=1, sticky="ew", padx=4, pady=3)
        ttk.Button(frm_folders, text="Выбрать...", command=self._clean_browse_output).grid(row=1, column=2, padx=4, pady=3)

        # Load buttons row
        frm_load = ttk.Frame(parent)
        frm_load.grid(row=1, column=0, sticky="w", padx=(8, 4), pady=(0, 4))
        ttk.Button(frm_load, text="📁  Загрузить папку", command=self._clean_load_files).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(frm_load, text="➕  Добавить файлы", command=self._clean_add_files).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(frm_load, text="🗑  Очистить список", command=self._clean_clear_files).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(frm_load, text="🤖  AI Определить типы", command=self._clean_ai_detect_rooms).pack(side=tk.LEFT)

        # Mode frame
        frm_mode = ttk.LabelFrame(parent, text="Режим обработки")
        frm_mode.grid(row=2, column=0, sticky="ew", padx=(8, 4), pady=(0, 4))

        self._clean_mode_var = tk.StringVar(value="empty")
        ttk.Radiobutton(frm_mode, text="🏚  Полное опустошение — убрать всю мебель и вещи",
                        variable=self._clean_mode_var, value="empty").grid(row=0, column=0, sticky="w", padx=10, pady=4)
        ttk.Radiobutton(frm_mode, text="🧹  Реалистичная уборка — убрать только мусор, мебель оставить",
                        variable=self._clean_mode_var, value="declutter").grid(row=1, column=0, sticky="w", padx=10, pady=4)

        # Table frame
        frm_table = ttk.Frame(parent)
        frm_table.grid(row=3, column=0, sticky="nsew", padx=(8, 4), pady=(0, 4))
        frm_table.columnconfigure(0, weight=1)
        frm_table.rowconfigure(0, weight=1)

        cols = ("check", "file", "room", "mode", "status")
        self._clean_tree = ttk.Treeview(frm_table, columns=cols, show="headings", selectmode="browse")
        self._clean_tree.heading("check", text="☑")
        self._clean_tree.heading("file", text="Файл")
        self._clean_tree.heading("room", text="Тип комнаты")
        self._clean_tree.heading("mode", text="Режим")
        self._clean_tree.heading("status", text="Статус")
        self._clean_tree.column("check", width=40, minwidth=40, stretch=False, anchor="center")
        self._clean_tree.column("file", width=280, minwidth=150)
        self._clean_tree.column("room", width=120, minwidth=80, anchor="center")
        self._clean_tree.column("mode", width=100, minwidth=80, anchor="center")
        self._clean_tree.column("status", width=100, minwidth=80, anchor="center")

        scrollbar_y = ttk.Scrollbar(frm_table, orient="vertical", command=self._clean_tree.yview)
        self._clean_tree.configure(yscrollcommand=scrollbar_y.set)
        self._clean_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        self._clean_tree.bind("<ButtonRelease-1>", self._clean_tree_click)

        # Row below table
        frm_sel = ttk.Frame(parent)
        frm_sel.grid(row=4, column=0, sticky="w", padx=(8, 4), pady=(0, 4))
        ttk.Button(frm_sel, text="Выбрать все", command=self._clean_select_all).pack(side=tk.LEFT, padx=4)
        ttk.Button(frm_sel, text="Снять все", command=self._clean_deselect_all).pack(side=tk.LEFT, padx=4)

        # Control frame
        frm_ctrl = ttk.LabelFrame(parent, text="Управление")
        frm_ctrl.grid(row=5, column=0, sticky="ew", padx=(8, 4), pady=(0, 4))
        frm_ctrl.columnconfigure(3, weight=1)

        self._clean_btn_start = ttk.Button(frm_ctrl, text="▶  Обработать выбранные", command=self._clean_start)
        self._clean_btn_start.grid(row=0, column=0, padx=6, pady=6)

        self._clean_btn_stop = ttk.Button(frm_ctrl, text="■  Стоп", command=self._clean_stop_proc, state="disabled")
        self._clean_btn_stop.grid(row=0, column=1, padx=4, pady=6)

        self._clean_btn_retry = ttk.Button(frm_ctrl, text="↺  Повторить", command=self._clean_retry)
        self._clean_btn_retry.grid(row=0, column=2, padx=4, pady=6)

        self._clean_progress = ttk.Progressbar(frm_ctrl, mode="determinate")
        self._clean_progress.grid(row=0, column=3, sticky="ew", padx=8, pady=6)

        self._clean_status_var = tk.StringVar(value="Готово")
        ttk.Label(frm_ctrl, textvariable=self._clean_status_var).grid(row=0, column=4, padx=6, pady=6)

        # Log
        frm_log = ttk.LabelFrame(parent, text="Лог")
        frm_log.grid(row=6, column=0, sticky="ew", padx=(8, 4), pady=(0, 8))
        frm_log.columnconfigure(0, weight=1)
        self._clean_log = scrolledtext.ScrolledText(frm_log, height=4, state="disabled", wrap=tk.WORD)
        self._clean_log.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ── Right side: thumbnail preview ─────────────────────────────────────
        frm_thumb = ttk.LabelFrame(parent, text="Превью")
        frm_thumb.grid(row=0, column=1, rowspan=7, sticky="nsew", padx=(0, 8), pady=8)
        frm_thumb.columnconfigure(0, weight=1)

        self._clean_thumb_canvas = tk.Canvas(frm_thumb, width=220, height=180,
                                              bg="#1e1e1e", highlightthickness=0)
        self._clean_thumb_canvas.grid(row=0, column=0, padx=6, pady=6)

        self._clean_thumb_label = ttk.Label(frm_thumb, text="", wraplength=220,
                                             font=("", 9), foreground="gray")
        self._clean_thumb_label.grid(row=1, column=0, padx=6, pady=(0, 6))

        # Combobox popup reference
        self._combo_popup = None

    def _clean_browse_input(self):
        folder = filedialog.askdirectory(title="Выбрать папку с фотографиями")
        if folder:
            self._clean_input_var.set(folder)

    def _clean_browse_output(self):
        folder = filedialog.askdirectory(title="Выбрать папку для результатов")
        if folder:
            self._clean_output_var.set(folder)

    def _clean_load_files(self):
        folder = self._clean_input_var.get().strip()
        if not folder:
            folder = filedialog.askdirectory(title="Выбрать папку с фотографиями")
            if not folder:
                return
            self._clean_input_var.set(folder)

        # Clear existing rows
        for item in self._clean_tree.get_children():
            self._clean_tree.delete(item)
        self._clean_rows.clear()

        files = sorted([
            f for f in Path(folder).iterdir()
            if f.suffix.lower() in ALL_EXTENSIONS
        ])

        if not files:
            messagebox.showinfo("Нет файлов", "В выбранной папке нет поддерживаемых фото.")
            return

        self._clean_insert_files(files)
        self._clean_log_msg(f"Загружено {len(files)} файлов из {folder}")

    def _clean_add_files(self):
        paths = filedialog.askopenfilenames(
            title="Добавить фотографии",
            filetypes=FILE_TYPES
        )
        if not paths:
            return
        existing = {r["path"] for r in self._clean_rows}
        new_files = [Path(p) for p in paths if p not in existing]
        if not new_files:
            return
        self._clean_insert_files(new_files)
        self._clean_log_msg(f"Добавлено {len(new_files)} файлов")

    def _clean_clear_files(self):
        for item in self._clean_tree.get_children():
            self._clean_tree.delete(item)
        self._clean_rows.clear()
        self._clean_thumb_canvas.delete("all")
        self._clean_thumb_label.config(text="")

    def _clean_insert_files(self, files):
        mode = self._clean_mode_var.get()
        for f in files:
            room = detect_room_type(f.name)
            mode_label = "Опустошение" if mode == "empty" else "Уборка"
            iid = self._clean_tree.insert("", "end", values=("☑", f.name, room, mode_label, "Ожидание"))
            self._clean_rows.append({
                "iid": iid,
                "path": str(f),
                "room": room,
                "mode": mode,
                "checked": True,
                "out_path": None,
            })

    def _clean_tree_click(self, event):
        col = self._clean_tree.identify_column(event.x)
        iid = self._clean_tree.identify_row(event.y)
        if not iid:
            return

        if col == "#1":  # check column
            self._clean_toggle_check(iid)
        elif col == "#3":  # room column
            self._clean_show_room_combo(iid, event.x, event.y)

        # Update thumbnail: show result if available, otherwise input
        for row in self._clean_rows:
            if row["iid"] == iid:
                path = row.get("out_path") or row["path"]
                self._show_thumb(path, self._clean_thumb_canvas, self._clean_thumb_label)
                break

    def _clean_toggle_check(self, iid):
        for row in self._clean_rows:
            if row["iid"] == iid:
                row["checked"] = not row["checked"]
                vals = list(self._clean_tree.item(iid, "values"))
                vals[0] = "☑" if row["checked"] else "☐"
                self._clean_tree.item(iid, values=vals)
                break

    def _clean_show_room_combo(self, iid, x, y):
        if self._combo_popup:
            self._combo_popup.destroy()
            self._combo_popup = None

        bbox = self._clean_tree.bbox(iid, "#3")
        if not bbox:
            return

        combo_var = tk.StringVar()
        for row in self._clean_rows:
            if row["iid"] == iid:
                combo_var.set(row["room"])
                break

        popup = ttk.Combobox(self._clean_tree, textvariable=combo_var,
                              values=ROOM_TYPES, state="readonly", width=14)
        popup.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        popup.focus_set()

        def on_select(event=None):
            selected = combo_var.get()
            for row in self._clean_rows:
                if row["iid"] == iid:
                    row["room"] = selected
                    vals = list(self._clean_tree.item(iid, "values"))
                    vals[2] = selected
                    self._clean_tree.item(iid, values=vals)
                    break
            popup.destroy()
            self._combo_popup = None

        def on_focusout(event=None):
            popup.destroy()
            self._combo_popup = None

        popup.bind("<<ComboboxSelected>>", on_select)
        popup.bind("<FocusOut>", on_focusout)
        popup.bind("<Return>", on_select)
        popup.bind("<Escape>", on_focusout)
        self._combo_popup = popup

    def _clean_select_all(self):
        for row in self._clean_rows:
            row["checked"] = True
            vals = list(self._clean_tree.item(row["iid"], "values"))
            vals[0] = "☑"
            self._clean_tree.item(row["iid"], values=vals)

    def _clean_deselect_all(self):
        for row in self._clean_rows:
            row["checked"] = False
            vals = list(self._clean_tree.item(row["iid"], "values"))
            vals[0] = "☐"
            self._clean_tree.item(row["iid"], values=vals)

    def _clean_start(self):
        if self._clean_running:
            return
        api_key = self.cfg.get("api_key", "").strip()
        if not api_key:
            messagebox.showerror("Нет API ключа", "Укажите xAI API ключ в настройках.")
            return

        checked = [r for r in self._clean_rows if r["checked"]]
        if not checked:
            messagebox.showinfo("Нет файлов", "Нет выбранных файлов для обработки.")
            return

        output_folder = self._clean_output_var.get().strip()
        if not output_folder:
            messagebox.showerror("Нет папки", "Укажите папку для результатов.")
            return

        self._clean_stop.clear()
        self._clean_running = True
        self._clean_btn_start.config(state="disabled")
        self._clean_btn_stop.config(state="normal")
        self._clean_progress["maximum"] = len(checked)
        self._clean_progress["value"] = 0
        self._clean_status_var.set(f"Обработка 0 / {len(checked)}")

        t = threading.Thread(target=self._run_clean, args=(checked, output_folder, api_key), daemon=True)
        t.start()

    def _clean_stop_proc(self):
        self._clean_stop.set()
        self._clean_status_var.set("Останавливается...")

    def _clean_ai_detect_rooms(self):
        """Определяет тип комнаты для всех загруженных фото с помощью AI (Grok vision)."""
        api_key = self.cfg.get("api_key", "").strip()
        if not api_key:
            messagebox.showwarning("API ключ", "Укажите API ключ Grok в настройках.")
            return
        rows = list(self._clean_rows)
        if not rows:
            messagebox.showinfo("Нет файлов", "Сначала загрузите фотографии.")
            return

        self._clean_log_msg(f"🤖 AI определяет типы комнат для {len(rows)} фото...")

        def run_detection():
            for row in rows:
                try:
                    detected = detect_room_type_ai(row["path"], api_key)
                    row["room"] = detected
                    vals = list(self._clean_tree.item(row["iid"], "values"))
                    vals[2] = detected
                    self.after(0, lambda iid=row["iid"], v=vals: self._clean_tree.item(iid, values=v))
                    self.after(0, lambda fname=Path(row["path"]).name, r=detected:
                               self._clean_log_msg(f"  {fname} → {r}"))
                except Exception as e:
                    self.after(0, lambda fname=Path(row["path"]).name, err=str(e):
                               self._clean_log_msg(f"  {fname} — ошибка: {err[:60]}"))
            self.after(0, lambda: self._clean_log_msg("✅ AI определение завершено."))

        threading.Thread(target=run_detection, daemon=True).start()

    def _run_clean(self, rows, output_folder, api_key):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(output_folder) / f"Clean_{timestamp}"
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.after(0, lambda: self._clean_log_msg(f"Ошибка создания папки: {e}"))
            self.after(0, self._clean_done)
            return

        workers = int(self.cfg.get("workers", 2))
        total = len(rows)
        done_count = [0]

        def process_one(row):
            if self._clean_stop.is_set():
                return row, None, "Отменено"

            room = row["room"]
            mode = row["mode"]

            if mode == "empty":
                base = self.cfg.get("empty_prompts", DEFAULT_PROMPTS).get(room, DEFAULT_PROMPTS["по умолчанию"])
            else:
                base = self.cfg.get("declutter_prompts", DECLUTTER_PROMPTS).get(room, DECLUTTER_PROMPTS["по умолчанию"])

            prompt = build_prompt(base)
            self.after(0, lambda r=row: self._clean_set_status(r["iid"], "Обработка..."))

            try:
                img_bytes = process_image_xai(row["path"], prompt, api_key,
                                               model=self.cfg.get("model", "aurora"))
                suffix = "_empty" if mode == "empty" else "_clean"
                stem = Path(row["path"]).stem
                out_path = out_dir / f"{stem}{suffix}.jpg"
                if HAS_PIL:
                    img = PILImage.open(io.BytesIO(img_bytes)).convert("RGB")
                    img.save(str(out_path), "JPEG", quality=95)
                else:
                    out_path.write_bytes(img_bytes)
                return row, str(out_path), "Готово"
            except Exception as e:
                return row, None, f"Ошибка: {str(e)[:60]}"

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(process_one, row): row for row in rows}
            for future in as_completed(futures):
                if self._clean_stop.is_set():
                    break
                row, out_path, status = future.result()
                done_count[0] += 1
                cnt = done_count[0]

                def update_ui(r=row, s=status, op=out_path, c=cnt):
                    self._clean_set_status(r["iid"], "✅ Готово" if op else f"❌ {s[:30]}")
                    self._clean_progress["value"] = c
                    self._clean_status_var.set(f"Обработка {c} / {total}")
                    if op:
                        r["out_path"] = op
                        self._clean_log_msg(f"[OK] {Path(r['path']).name} → {Path(op).name}")
                        # Show result thumbnail if this row is currently selected
                        sel = self._clean_tree.selection()
                        if sel and sel[0] == r["iid"]:
                            self._show_thumb(op, self._clean_thumb_canvas, self._clean_thumb_label)
                    else:
                        self._clean_log_msg(f"[ERR] {Path(r['path']).name}: {s}")

                self.after(0, update_ui)

        self.after(0, lambda: self._clean_log_msg(f"Завершено. Результаты: {out_dir}"))
        self.after(0, self._clean_done)

    def _clean_set_status(self, iid, status):
        try:
            vals = list(self._clean_tree.item(iid, "values"))
            vals[4] = status
            self._clean_tree.item(iid, values=vals)
        except Exception:
            pass

    def _clean_done(self):
        self._clean_running = False
        self._clean_btn_start.config(state="normal")
        self._clean_btn_stop.config(state="disabled")
        self._clean_status_var.set("Готово")

    def _clean_retry(self):
        """Re-process the currently selected row."""
        if self._clean_running:
            messagebox.showinfo("Занято", "Дождитесь окончания текущей обработки.")
            return
        sel = self._clean_tree.selection()
        if not sel:
            messagebox.showinfo("Нет выбора", "Кликните на строку в таблице, чтобы выбрать фото.")
            return
        iid = sel[0]
        row = next((r for r in self._clean_rows if r["iid"] == iid), None)
        if not row:
            return
        api_key = self.cfg.get("api_key", "").strip()
        if not api_key:
            messagebox.showerror("Нет API ключа", "Укажите xAI API ключ в настройках.")
            return
        output_folder = self._clean_output_var.get().strip()
        if not output_folder:
            messagebox.showerror("Нет папки", "Укажите папку для результатов.")
            return
        row["out_path"] = None
        self._clean_set_status(iid, "Ожидание")
        self._clean_stop.clear()
        self._clean_running = True
        self._clean_btn_start.config(state="disabled")
        self._clean_btn_stop.config(state="normal")
        self._clean_progress["maximum"] = 1
        self._clean_progress["value"] = 0
        self._clean_status_var.set("Повтор 1 / 1")
        t = threading.Thread(target=self._run_clean, args=([row], output_folder, api_key), daemon=True)
        t.start()

    def _clean_log_msg(self, msg):
        self._log_to(self._clean_log, msg)

    # ─── Thumbnail helper ─────────────────────────────────────────────────────

    def _show_thumb(self, path: str, canvas: tk.Canvas, label: ttk.Label):
        if not HAS_PIL:
            return
        try:
            w = canvas.winfo_width() or 220
            h = canvas.winfo_height() or 180
            img = PILImage.open(path)
            img.thumbnail((w, h), PILImage.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            canvas.delete("all")
            # center
            x = w // 2
            y = h // 2
            canvas.create_image(x, y, anchor="center", image=photo)
            # store reference on the canvas widget itself to survive GC
            canvas._thumb_ref = photo
            label.config(text=Path(path).name)
        except Exception:
            canvas.delete("all")
            label.config(text=Path(path).name)

    # ─── Tab 2: Небо & Свет ───────────────────────────────────────────────────

    def _build_tab_sky(self):
        parent = self._tab_sky
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        # Source frame
        frm_src = ttk.LabelFrame(parent, text="Источник фотографий")
        frm_src.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        frm_src.columnconfigure(1, weight=1)

        ttk.Label(frm_src, text="Папка:").grid(row=0, column=0, sticky="w", padx=6, pady=3)
        self._sky_folder_var = tk.StringVar()
        ttk.Entry(frm_src, textvariable=self._sky_folder_var).grid(row=0, column=1, sticky="ew", padx=4, pady=3)
        ttk.Button(frm_src, text="Выбрать...", command=self._sky_browse_folder).grid(row=0, column=2, padx=4, pady=3)
        ttk.Button(frm_src, text="Загрузить", command=self._sky_load_folder).grid(row=0, column=3, padx=4, pady=3)

        frm_btns = ttk.Frame(frm_src)
        frm_btns.grid(row=1, column=0, columnspan=4, sticky="w", padx=4, pady=3)
        ttk.Button(frm_btns, text="➕  Добавить файлы", command=self._sky_add_files).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(frm_btns, text="☑  Выбрать все", command=self._sky_select_all).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(frm_btns, text="☐  Снять все", command=self._sky_deselect_all).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(frm_btns, text="🗑  Очистить", command=self._sky_clear_files).pack(side=tk.LEFT)

        ttk.Label(frm_src, text="Результат:").grid(row=2, column=0, sticky="w", padx=6, pady=3)
        self._sky_output_var = tk.StringVar(value=self.cfg.get("output_folder", ""))
        ttk.Entry(frm_src, textvariable=self._sky_output_var).grid(row=2, column=1, sticky="ew", padx=4, pady=3)
        ttk.Button(frm_src, text="Выбрать...", command=self._sky_browse_output).grid(row=2, column=2, padx=4, pady=3)

        # Main area: photos list + preview + preset panel
        frm_main = ttk.Frame(parent)
        frm_main.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 4))
        frm_main.columnconfigure(0, weight=1)
        frm_main.columnconfigure(1, weight=2)
        frm_main.rowconfigure(0, weight=1)

        # Left: photo treeview with checkboxes
        frm_photos = ttk.LabelFrame(frm_main, text="Фотографии (☑ = будет обработано)")
        frm_photos.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        frm_photos.columnconfigure(0, weight=1)
        frm_photos.rowconfigure(0, weight=1)

        sky_cols = ("check", "file", "status")
        self._sky_tree = ttk.Treeview(frm_photos, columns=sky_cols, show="headings", selectmode="browse")
        self._sky_tree.heading("check", text="☑")
        self._sky_tree.heading("file", text="Файл")
        self._sky_tree.heading("status", text="Статус")
        self._sky_tree.column("check", width=36, minwidth=36, stretch=False, anchor="center")
        self._sky_tree.column("file", width=200, minwidth=120)
        self._sky_tree.column("status", width=80, minwidth=60, anchor="center")
        sb_y = ttk.Scrollbar(frm_photos, orient="vertical", command=self._sky_tree.yview)
        self._sky_tree.configure(yscrollcommand=sb_y.set)
        self._sky_tree.grid(row=0, column=0, sticky="nsew", padx=(4, 0), pady=4)
        sb_y.grid(row=0, column=1, sticky="ns", pady=4)
        self._sky_tree.bind("<ButtonRelease-1>", self._sky_tree_click)

        # Thumbnail below treeview
        frm_sky_thumb = ttk.LabelFrame(frm_photos, text="Превью")
        frm_sky_thumb.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 4))
        frm_sky_thumb.columnconfigure(0, weight=1)
        self._sky_thumb_canvas = tk.Canvas(frm_sky_thumb, width=220, height=150,
                                            bg="#1e1e1e", highlightthickness=0)
        self._sky_thumb_canvas.grid(row=0, column=0, padx=4, pady=(4, 2))
        self._sky_thumb_label = ttk.Label(frm_sky_thumb, text="", wraplength=220,
                                           font=("", 9), foreground="gray")
        self._sky_thumb_label.grid(row=1, column=0, padx=4, pady=(0, 4))

        # Right: preset panel
        frm_preset = ttk.LabelFrame(frm_main, text="Пресет неба / освещения")
        frm_preset.grid(row=0, column=1, sticky="nsew")
        frm_preset.columnconfigure(0, weight=1)
        frm_preset.rowconfigure(1, weight=1)

        sky_names = list(SKY_PRESETS.keys())
        self._sky_preset_listbox = tk.Listbox(frm_preset, height=12, selectmode=tk.SINGLE, exportselection=False)
        for name in sky_names:
            self._sky_preset_listbox.insert(tk.END, name)
        self._sky_preset_listbox.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        self._sky_preset_listbox.bind("<<ListboxSelect>>", self._sky_preset_selected)

        ttk.Label(frm_preset, text="Редактировать промпт:").grid(row=1, column=0, sticky="w", padx=6, pady=(4, 0))
        self._sky_prompt_text = scrolledtext.ScrolledText(frm_preset, height=6, wrap=tk.WORD)
        self._sky_prompt_text.grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
        frm_preset.rowconfigure(2, weight=1)

        ttk.Label(frm_preset, text="Изменения применяются только к текущей сессии. Сохранить в Промпты → Небо",
                  foreground="gray").grid(row=3, column=0, sticky="w", padx=6, pady=(0, 4))

        # Select first preset
        if sky_names:
            self._sky_preset_listbox.selection_set(0)
            first_name = sky_names[0]
            prompt = self.cfg.get("sky_prompts", {}).get(first_name, SKY_PRESETS[first_name]["prompt"])
            self._sky_prompt_text.insert("1.0", prompt)

        # Bottom controls
        frm_ctrl = ttk.Frame(parent)
        frm_ctrl.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 4))
        frm_ctrl.columnconfigure(3, weight=1)

        self._sky_btn_start = ttk.Button(frm_ctrl, text="▶  Применить к отмеченным фото", command=self._sky_start)
        self._sky_btn_start.grid(row=0, column=0, padx=6, pady=6)

        self._sky_btn_stop = ttk.Button(frm_ctrl, text="■  Стоп", command=self._sky_stop_proc, state="disabled")
        self._sky_btn_stop.grid(row=0, column=1, padx=4, pady=6)

        self._sky_btn_retry = ttk.Button(frm_ctrl, text="↺  Повторить", command=self._sky_retry)
        self._sky_btn_retry.grid(row=0, column=2, padx=4, pady=6)

        self._sky_progress = ttk.Progressbar(frm_ctrl, mode="determinate")
        self._sky_progress.grid(row=0, column=3, sticky="ew", padx=8, pady=6)

        self._sky_status_var = tk.StringVar(value="Готово")
        ttk.Label(frm_ctrl, textvariable=self._sky_status_var).grid(row=0, column=4, padx=6, pady=6)

        # Log
        frm_log = ttk.LabelFrame(parent, text="Лог")
        frm_log.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
        frm_log.columnconfigure(0, weight=1)
        self._sky_log = scrolledtext.ScrolledText(frm_log, height=4, state="disabled", wrap=tk.WORD)
        self._sky_log.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _sky_browse_folder(self):
        folder = filedialog.askdirectory(title="Выбрать папку с фотографиями")
        if folder:
            self._sky_folder_var.set(folder)

    def _sky_load_folder(self):
        folder = self._sky_folder_var.get().strip()
        if not folder:
            folder = filedialog.askdirectory(title="Выбрать папку с фотографиями")
            if not folder:
                return
            self._sky_folder_var.set(folder)
        files = sorted([
            str(f) for f in Path(folder).iterdir()
            if f.suffix.lower() in ALL_EXTENSIONS
        ])
        if not files:
            messagebox.showinfo("Нет файлов", "В папке нет поддерживаемых фото.")
            return
        added = 0
        for f in files:
            if f not in self._sky_files:
                self._sky_files.append(f)
                iid = self._sky_tree.insert("", "end", values=("☑", Path(f).name, "Ожидание"))
                added += 1
        self._sky_log_msg(f"Загружено {added} файлов из {folder}")

    def _sky_add_files(self):
        paths = filedialog.askopenfilenames(title="Добавить фотографии", filetypes=FILE_TYPES)
        added = 0
        for f in paths:
            if f not in self._sky_files:
                self._sky_files.append(f)
                self._sky_tree.insert("", "end", values=("☑", Path(f).name, "Ожидание"))
                added += 1
        if added:
            self._sky_log_msg(f"Добавлено {added} файлов")

    def _sky_select_all(self):
        for iid in self._sky_tree.get_children():
            vals = list(self._sky_tree.item(iid, "values"))
            vals[0] = "☑"
            self._sky_tree.item(iid, values=vals)

    def _sky_deselect_all(self):
        for iid in self._sky_tree.get_children():
            vals = list(self._sky_tree.item(iid, "values"))
            vals[0] = "☐"
            self._sky_tree.item(iid, values=vals)

    def _sky_clear_files(self):
        self._sky_files.clear()
        for iid in self._sky_tree.get_children():
            self._sky_tree.delete(iid)
        self._sky_thumb_canvas.delete("all")
        self._sky_thumb_label.config(text="")

    def _sky_tree_click(self, event):
        col = self._sky_tree.identify_column(event.x)
        iid = self._sky_tree.identify_row(event.y)
        if not iid:
            return
        if col == "#1":  # toggle check
            vals = list(self._sky_tree.item(iid, "values"))
            vals[0] = "☐" if vals[0] == "☑" else "☑"
            self._sky_tree.item(iid, values=vals)
        # Update thumbnail: show result if available, else input
        idx = self._sky_tree.index(iid)
        if 0 <= idx < len(self._sky_files):
            fpath = self._sky_files[idx]
            out = getattr(self, "_sky_out_paths", {}).get(fpath)
            self._show_thumb(out or fpath, self._sky_thumb_canvas, self._sky_thumb_label)

    def _sky_browse_output(self):
        folder = filedialog.askdirectory(title="Папка для результатов")
        if folder:
            self._sky_output_var.set(folder)

    def _sky_preset_selected(self, event=None):
        sel = self._sky_preset_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        name = list(SKY_PRESETS.keys())[idx]
        prompt = self.cfg.get("sky_prompts", {}).get(name, SKY_PRESETS[name]["prompt"])
        self._sky_prompt_text.delete("1.0", tk.END)
        self._sky_prompt_text.insert("1.0", prompt)

    def _sky_start(self):
        if self._sky_running:
            return
        api_key = self.cfg.get("api_key", "").strip()
        if not api_key:
            messagebox.showerror("Нет API ключа", "Укажите xAI API ключ в настройках.")
            return

        # Get checked files (☑) from treeview
        files = []
        sky_iids = []
        for idx, iid in enumerate(self._sky_tree.get_children()):
            vals = self._sky_tree.item(iid, "values")
            if vals[0] == "☑" and idx < len(self._sky_files):
                files.append(self._sky_files[idx])
                sky_iids.append(iid)

        if not files:
            messagebox.showinfo("Нет файлов", "Добавьте фотографии для обработки.")
            return

        # Get current preset
        preset_sel = self._sky_preset_listbox.curselection()
        if not preset_sel:
            messagebox.showinfo("Нет пресета", "Выберите пресет неба.")
            return

        preset_idx = preset_sel[0]
        preset_name = list(SKY_PRESETS.keys())[preset_idx]
        preset_suffix = SKY_PRESETS[preset_name]["suffix"]
        prompt = build_prompt(self._sky_prompt_text.get("1.0", tk.END).strip(), preserve_defects=False)

        output_folder = self._sky_output_var.get().strip()
        if not output_folder:
            messagebox.showerror("Нет папки", "Укажите папку для результатов.")
            return

        self._sky_stop.clear()
        self._sky_running = True
        self._sky_btn_start.config(state="disabled")
        self._sky_btn_stop.config(state="normal")
        self._sky_progress["maximum"] = len(files)
        self._sky_progress["value"] = 0
        self._sky_status_var.set(f"Обработка 0 / {len(files)}")

        t = threading.Thread(
            target=self._run_sky,
            args=(files, sky_iids, prompt, preset_suffix, output_folder, api_key),
            daemon=True
        )
        t.start()

    def _sky_stop_proc(self):
        self._sky_stop.set()
        self._sky_status_var.set("Останавливается...")

    def _sky_set_row_status(self, iid, status):
        try:
            vals = list(self._sky_tree.item(iid, "values"))
            vals[2] = status
            self._sky_tree.item(iid, values=vals)
        except Exception:
            pass

    def _run_sky(self, files, iids, prompt, suffix, output_folder, api_key):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(output_folder) / f"Sky_{timestamp}"
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.after(0, lambda: self._sky_log_msg(f"Ошибка создания папки: {e}"))
            self.after(0, self._sky_done)
            return

        workers = int(self.cfg.get("workers", 2))
        total = len(files)
        done_count = [0]
        # Map path → iid for status updates
        path_to_iid = {f: iid for f, iid in zip(files, iids)}

        def process_one(fpath):
            if self._sky_stop.is_set():
                return fpath, None, "Отменено"
            try:
                img_bytes = process_image_xai(fpath, prompt, api_key,
                                               model=self.cfg.get("model", "aurora"))
                stem = Path(fpath).stem
                out_path = out_dir / f"{stem}{suffix}.jpg"
                if HAS_PIL:
                    img = PILImage.open(io.BytesIO(img_bytes)).convert("RGB")
                    img.save(str(out_path), "JPEG", quality=95)
                else:
                    out_path.write_bytes(img_bytes)
                return fpath, str(out_path), "Готово"
            except Exception as e:
                return fpath, None, f"Ошибка: {str(e)[:60]}"

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(process_one, f): f for f in files}
            for future in as_completed(futures):
                if self._sky_stop.is_set():
                    break
                fpath, out_path, status = future.result()
                done_count[0] += 1
                cnt = done_count[0]
                row_iid = path_to_iid.get(fpath)

                def update_ui(fp=fpath, op=out_path, s=status, c=cnt, rid=row_iid):
                    self._sky_progress["value"] = c
                    self._sky_status_var.set(f"Обработка {c} / {total}")
                    if rid:
                        self._sky_set_row_status(rid, "✅ Готово" if op else "❌ Ошибка")
                    if op:
                        # Store out_path in sky files map
                        if not hasattr(self, "_sky_out_paths"):
                            self._sky_out_paths = {}
                        self._sky_out_paths[fp] = op
                        self._sky_log_msg(f"[OK] {Path(fp).name} → {Path(op).name}")
                        # Show result thumbnail if this row is selected
                        if rid and self._sky_tree.selection() and self._sky_tree.selection()[0] == rid:
                            self._show_thumb(op, self._sky_thumb_canvas, self._sky_thumb_label)
                    else:
                        self._sky_log_msg(f"[ERR] {Path(fp).name}: {s}")

                self.after(0, update_ui)

        self.after(0, lambda: self._sky_log_msg(f"Завершено. Результаты: {out_dir}"))
        self.after(0, self._sky_done)

    def _sky_done(self):
        self._sky_running = False
        self._sky_btn_start.config(state="normal")
        self._sky_btn_stop.config(state="disabled")
        self._sky_status_var.set("Готово")

    def _sky_retry(self):
        """Re-process the currently selected sky row."""
        if self._sky_running:
            messagebox.showinfo("Занято", "Дождитесь окончания текущей обработки.")
            return
        sel = self._sky_tree.selection()
        if not sel:
            messagebox.showinfo("Нет выбора", "Кликните на строку в таблице, чтобы выбрать фото.")
            return
        iid = sel[0]
        idx = self._sky_tree.index(iid)
        if idx >= len(self._sky_files):
            return
        fpath = self._sky_files[idx]
        api_key = self.cfg.get("api_key", "").strip()
        if not api_key:
            messagebox.showerror("Нет API ключа", "Укажите xAI API ключ в настройках.")
            return
        preset_sel = self._sky_preset_listbox.curselection()
        if not preset_sel:
            messagebox.showinfo("Нет пресета", "Выберите пресет неба.")
            return
        preset_name = list(SKY_PRESETS.keys())[preset_sel[0]]
        preset_suffix = SKY_PRESETS[preset_name]["suffix"]
        prompt = build_prompt(self._sky_prompt_text.get("1.0", tk.END).strip(), preserve_defects=False)
        output_folder = self._sky_output_var.get().strip()
        if not output_folder:
            messagebox.showerror("Нет папки", "Укажите папку для результатов.")
            return
        self._sky_set_row_status(iid, "Ожидание")
        self._sky_stop.clear()
        self._sky_running = True
        self._sky_btn_start.config(state="disabled")
        self._sky_btn_stop.config(state="normal")
        self._sky_progress["maximum"] = 1
        self._sky_progress["value"] = 0
        self._sky_status_var.set("Повтор 1 / 1")
        t = threading.Thread(
            target=self._run_sky,
            args=([fpath], [iid], prompt, preset_suffix, output_folder, api_key),
            daemon=True
        )
        t.start()

    def _sky_log_msg(self, msg):
        self._log_to(self._sky_log, msg)

    # ─── Tab 3: Промпты ───────────────────────────────────────────────────────

    def _build_tab_prompts(self):
        parent = self._tab_prompts
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        # Mode selector
        frm_modes = ttk.Frame(parent)
        frm_modes.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        self._prompts_mode_var = tk.StringVar(value="empty")
        btn_empty = ttk.Radiobutton(frm_modes, text="🏚 Полное опустошение",
                                     variable=self._prompts_mode_var, value="empty",
                                     command=self._prompts_mode_changed)
        btn_empty.pack(side=tk.LEFT, padx=8)
        btn_declutter = ttk.Radiobutton(frm_modes, text="🧹 Уборка",
                                         variable=self._prompts_mode_var, value="declutter",
                                         command=self._prompts_mode_changed)
        btn_declutter.pack(side=tk.LEFT, padx=8)
        btn_sky = ttk.Radiobutton(frm_modes, text="🌅 Небо & Свет",
                                   variable=self._prompts_mode_var, value="sky",
                                   command=self._prompts_mode_changed)
        btn_sky.pack(side=tk.LEFT, padx=8)

        # Main area
        frm_main = ttk.Frame(parent)
        frm_main.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 4))
        frm_main.columnconfigure(1, weight=1)
        frm_main.rowconfigure(0, weight=1)

        # Left sidebar
        frm_sidebar = ttk.LabelFrame(frm_main, text="Список")
        frm_sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        frm_sidebar.rowconfigure(0, weight=1)

        self._prompts_listbox = tk.Listbox(frm_sidebar, width=22, exportselection=False)
        sb = ttk.Scrollbar(frm_sidebar, orient="vertical", command=self._prompts_listbox.yview)
        self._prompts_listbox.configure(yscrollcommand=sb.set)
        self._prompts_listbox.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        sb.grid(row=0, column=1, sticky="ns", pady=4)
        self._prompts_listbox.bind("<<ListboxSelect>>", self._prompts_item_selected)

        # Right: prompt editor
        frm_editor = ttk.LabelFrame(frm_main, text="Промпт")
        frm_editor.grid(row=0, column=1, sticky="nsew")
        frm_editor.columnconfigure(0, weight=1)
        frm_editor.rowconfigure(0, weight=1)

        self._prompts_text = scrolledtext.ScrolledText(frm_editor, wrap=tk.WORD)
        self._prompts_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # Save button
        frm_save = ttk.Frame(parent)
        frm_save.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        ttk.Button(frm_save, text="💾  Сохранить все промпты", command=self._prompts_save).pack(side=tk.LEFT, padx=4)

        self._prompts_mode_changed()

    def _prompts_mode_changed(self):
        self._prompts_listbox.delete(0, tk.END)
        mode = self._prompts_mode_var.get()
        if mode in ("empty", "declutter"):
            for name in ROOM_TYPES:
                self._prompts_listbox.insert(tk.END, name)
        else:
            for name in SKY_PRESETS.keys():
                self._prompts_listbox.insert(tk.END, name)

        self._prompts_text.delete("1.0", tk.END)
        if self._prompts_listbox.size() > 0:
            self._prompts_listbox.selection_set(0)
            self._prompts_item_selected()

    def _prompts_item_selected(self, event=None):
        sel = self._prompts_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        mode = self._prompts_mode_var.get()

        if mode == "empty":
            name = ROOM_TYPES[idx]
            prompt = self.cfg.get("empty_prompts", DEFAULT_PROMPTS).get(name, DEFAULT_PROMPTS.get(name, ""))
        elif mode == "declutter":
            name = ROOM_TYPES[idx]
            prompt = self.cfg.get("declutter_prompts", DECLUTTER_PROMPTS).get(name, DECLUTTER_PROMPTS.get(name, ""))
        else:
            name = list(SKY_PRESETS.keys())[idx]
            prompt = self.cfg.get("sky_prompts", {}).get(name, SKY_PRESETS[name]["prompt"])

        self._prompts_text.delete("1.0", tk.END)
        self._prompts_text.insert("1.0", prompt)

    def _prompts_save(self):
        # Save current text first
        sel = self._prompts_listbox.curselection()
        if sel:
            idx = sel[0]
            mode = self._prompts_mode_var.get()
            text = self._prompts_text.get("1.0", tk.END).strip()

            if mode == "empty":
                name = ROOM_TYPES[idx]
                if "empty_prompts" not in self.cfg:
                    self.cfg["empty_prompts"] = dict(DEFAULT_PROMPTS)
                self.cfg["empty_prompts"][name] = text
            elif mode == "declutter":
                name = ROOM_TYPES[idx]
                if "declutter_prompts" not in self.cfg:
                    self.cfg["declutter_prompts"] = dict(DECLUTTER_PROMPTS)
                self.cfg["declutter_prompts"][name] = text
            else:
                name = list(SKY_PRESETS.keys())[idx]
                if "sky_prompts" not in self.cfg:
                    self.cfg["sky_prompts"] = {n: d["prompt"] for n, d in SKY_PRESETS.items()}
                self.cfg["sky_prompts"][name] = text

        save_config(self.cfg)
        messagebox.showinfo("Сохранено", "Промпты сохранены.")

    # ─── Tab 4: Настройки ─────────────────────────────────────────────────────

    def _build_tab_settings(self):
        parent = self._tab_settings
        parent.columnconfigure(1, weight=1)

        row = 0

        ttk.Label(parent, text="xAI API ключ:").grid(row=row, column=0, sticky="w", padx=12, pady=10)
        self._settings_api_var = tk.StringVar(value=self.cfg.get("api_key", ""))
        self._settings_api_entry = ttk.Entry(parent, textvariable=self._settings_api_var, show="*", width=50)
        self._settings_api_entry.grid(row=row, column=1, sticky="ew", padx=8, pady=10)

        row += 1
        self._settings_show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text="Показать ключ",
                        variable=self._settings_show_key_var,
                        command=self._settings_toggle_key).grid(row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ttk.Label(parent, text="Папка результатов:").grid(row=row, column=0, sticky="w", padx=12, pady=10)
        self._settings_output_var = tk.StringVar(value=self.cfg.get("output_folder", ""))
        ttk.Entry(parent, textvariable=self._settings_output_var).grid(row=row, column=1, sticky="ew", padx=8, pady=10)
        ttk.Button(parent, text="Обзор...", command=self._settings_browse_output).grid(row=row, column=2, padx=4, pady=10)

        row += 1
        ttk.Label(parent, text="Параллельных потоков:").grid(row=row, column=0, sticky="w", padx=12, pady=10)
        self._settings_workers_var = tk.IntVar(value=int(self.cfg.get("workers", 2)))
        ttk.Spinbox(parent, from_=1, to=5, textvariable=self._settings_workers_var, width=8).grid(
            row=row, column=1, sticky="w", padx=8, pady=10)

        row += 1
        ttk.Button(parent, text="Сохранить настройки", command=self._settings_save).grid(
            row=row, column=0, columnspan=2, pady=20)

        # Info
        row += 1
        info = ttk.LabelFrame(parent, text="Информация")
        info.grid(row=row, column=0, columnspan=3, sticky="ew", padx=12, pady=8)
        libs = []
        libs.append(f"PIL/Pillow: {'✓' if HAS_PIL else '✗ (pip install Pillow)'}")
        libs.append(f"rawpy: {'✓' if HAS_RAWPY else '✗ (pip install rawpy) — нужен для RAW/DNG'}")
        libs.append(f"requests: {'✓' if HAS_REQUESTS else '✗ (pip install requests)'}")
        ttk.Label(info, text="\n".join(libs), justify=tk.LEFT).pack(padx=8, pady=6, anchor="w")

    def _settings_toggle_key(self):
        if self._settings_show_key_var.get():
            self._settings_api_entry.config(show="")
        else:
            self._settings_api_entry.config(show="*")

    def _settings_browse_output(self):
        folder = filedialog.askdirectory(title="Папка для результатов")
        if folder:
            self._settings_output_var.set(folder)

    def _settings_save(self):
        self.cfg["api_key"] = self._settings_api_var.get().strip()
        self.cfg["output_folder"] = self._settings_output_var.get().strip()
        self.cfg["workers"] = int(self._settings_workers_var.get())
        # Sync output folder to other tabs
        self._clean_output_var.set(self.cfg["output_folder"])
        self._sky_output_var.set(self.cfg["output_folder"])
        save_config(self.cfg)
        messagebox.showinfo("Сохранено", "Настройки сохранены.")

    # ─── Shared Log ───────────────────────────────────────────────────────────

    def _log_to(self, widget, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        widget.config(state="normal")
        widget.insert(tk.END, line)
        widget.see(tk.END)
        widget.config(state="disabled")

    def _log(self, msg):
        """Log to active tab's log widget."""
        tab_idx = self.notebook.index(self.notebook.select())
        if tab_idx == 0:
            self._clean_log_msg(msg)
        elif tab_idx == 1:
            self._sky_log_msg(msg)


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
