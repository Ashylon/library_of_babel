import pygame as pg
from utils import get_path
import os

FRAME_SIZE = 16
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 180
LEVEL_WIDTH, LEVEL_HEIGHT = 1600, 1200
#Kamera
DEAD_ZONE_Y = 20
CAMERA_DELAY_X, CAMERA_DELAY_Y = 50, 2

STANDARD_TILESET: str = "assets/sprites/tiles/autotile_tileset.png"

#region UI Constants
HEART_POS_0: pg.Vector2 = pg.Vector2(20, 2)
HEART_POS_1: pg.Vector2 = pg.Vector2(35, 2)
HEART_POS_2: pg.Vector2 = pg.Vector2(50, 2)
UI_HEART_POSITIONS: list[pg.Vector2] = [HEART_POS_0, HEART_POS_1, HEART_POS_2]

# LETTER_POS_0: pg.Vector2 = pg.Vector2(256, 0)
UI_LETTER_POSITIONS: list[pg.Vector2] = []
for i in range(5):
    UI_LETTER_POSITIONS.append(pg.Vector2(256 + (12 * i), 0))

LETTER_IMAGES = {}
for i in range(65, 90, 1):
    letter = chr(i)
    file_path = get_path("assets/sprites/letters/letter_" + letter + ".png")

    if os.path.exists(file_path):
        LETTER_IMAGES[letter] = pg.image.load(file_path)
#endregion

#World_generating
TILE_MAPPING = {
    0b0000: (0),  # Isolierte Kachel ohne Verbindungen
    0b0001: (1),  # Verbindung zur linken Kachel
    0b0010: (2),  # Verbindung zur unteren Kachel
    0b0011: (3),  # Verbindung zur linken und unteren Kachel
    0b0100: (4),  # Verbindung zur rechten Kachel
    0b0101: (5),  # Verbindung zur linken und rechten Kachel
    0b0110: (6),  # Verbindung zur rechten und unteren Kachel
    0b0111: (7),  # Verbindung zur linken, rechten und unteren Kachel (U-Form)
    0b1000: (8),  # Verbindung zur oberen Kachel
    0b1001: (9),  # Verbindung zur oberen und linken Kachel
    0b1010: (10),  # Verbindung zur oberen und unteren Kachel (vertikale Linie)
    0b1011: (11),  # Verbindung zur oberen, unteren und linken Kachel (U-Form)
    0b1100: (12),  # Verbindung zur oberen und rechten Kachel
    0b1101: (13),  # Verbindung zur oberen, rechten und linken Kachel (U-Form)
    0b1110: (14),  # Verbindung zur oberen, unteren und rechten Kachel (U-Form)
    0b1111: (15),  # Komplett umschlossene Kachel mit Verbindungen zu allen Seiten
}

#Background
BG_LAYERS = [
    {"image": pg.image.load(get_path('assets/sprites/parallax/parallax_bg_3.png')), "offset_y": -100,"depth": 20},
    {"image": pg.image.load(get_path('assets/sprites/parallax/parallax_bg_2.png')), "offset_y": -100,"depth": 12},
    {"image": pg.image.load(get_path('assets/sprites/parallax/parallax_bg_1.png')), "offset_y": -100,"depth": 5},
    {"image": pg.image.load(get_path('assets/sprites/parallax/parallax_bg_-1.png')), "offset_y": -33,"depth": -5}
]
