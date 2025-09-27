# file: night_sky_perceptions.py
import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Night Sky Perceptions")
clock = pygame.time.Clock()

# Config
MAX_OBJECTS = 7
MAX_PER_TYPE = 4
SPEED_MULTIPLIER = 1.0
VIEW_MODE = "PLAN"
DIRECTION = "EAST"

# Object definitions
OBJECT_TYPES = {
    "Plane": {"color": (255, 0, 0), "prob": 30},
    "Helicopter": {"color": (0, 0, 255), "prob": 20},
    "Satellite": {"color": (255, 255, 255), "prob": 20},
    "Meteor": {"color": (255, 255, 150), "prob": 20},
    "Rare": {"color": (150, 0, 150), "prob": 10},
}
MOVEMENT_TYPES = ["normal", "hover_zip", "rare", "orbit", "shooting_star"]
MOVEMENT_DIST = [35, 25, 10, 15, 15]


class SkyObject:
    def __init__(self, oid, otype):
        self.id = oid
        self.otype = otype
        self.base_color = OBJECT_TYPES[otype]["color"]
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT / 2)
        self.z = random.uniform(0, 100)
        self.trail = []
        self.speed = random.uniform(1, 3)
        self.movement = random.choices(MOVEMENT_TYPES, MOVEMENT_DIST)[0]
        angle = random.uniform(0, 2 * math.pi)
        self.vx, self.vy = math.cos(angle) * self.speed, math.sin(angle) * self.speed

    def update(self):
        global SPEED_MULTIPLIER
        self.x += self.vx * SPEED_MULTIPLIER
        self.y += self.vy * SPEED_MULTIPLIER
        self.z = max(0, min(100, self.z + random.uniform(-0.2, 0.2)))
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0

    def draw(self, surface):
        factor = 1 - (self.z / 100)
        color = tuple(min(255, int(c + factor * 80)) for c in self.base_color)
        if VIEW_MODE == "PLAN":
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 5)
            pygame.draw.lines(surface, color, False, self.trail, 1)
            self._draw_id(surface, self.x, self.y)
        else:
            gx = self.x if DIRECTION == "EAST" else WIDTH - self.x
            gy = HEIGHT - (self.z * 5)
            pygame.draw.circle(surface, color, (int(gx), int(gy)), 5)
            self._draw_id(surface, gx, gy)

    def _draw_id(self, surface, x, y):
        font = pygame.font.SysFont("Arial", 14)
        label = font.render(str(self.id), True, (255, 255, 255))
        surface.blit(label, (x + 8, y - 8))


def spawn_objects():
    objs, oid = [], 1
    counts = {k: 0 for k in OBJECT_TYPES}
    while len(objs) < MAX_OBJECTS:
        choice = random.choices(list(OBJECT_TYPES.keys()),
                                [v["prob"] for v in OBJECT_TYPES.values()])[0]
        if counts[choice] < MAX_PER_TYPE:
            objs.append(SkyObject(oid, choice))
            counts[choice] += 1
            oid += 1
    return objs


# --- UI Elements ---
BUTTON_HEIGHT = 50
SLIDER_Y = HEIGHT - 80
SLIDER_X, SLIDER_W = 200, 600
SLIDER_H = 20
KNOB_RADIUS = 12

def draw_button(surface, rect, text, active=False):
    color = (80, 80, 120) if not active else (120, 120, 200)
    pygame.draw.rect(surface, color, rect, border_radius=8)
    font = pygame.font.SysFont("Arial", 20)
    label = font.render(text, True, (255, 255, 255))
    surface.blit(label, (rect.x + 10, rect.y + 10))

def draw_slider(surface, value):
    pygame.draw.rect(surface, (100, 100, 100),
                     (SLIDER_X, SLIDER_Y, SLIDER_W, SLIDER_H))
    knob_x = SLIDER_X + int(((value - 0.5) / 2.5) * SLIDER_W)
    pygame.draw.circle(surface, (200, 200, 200),
                       (knob_x, SLIDER_Y + SLIDER_H // 2), KNOB_RADIUS)


def main():
    global VIEW_MODE, DIRECTION, SPEED_MULTIPLIER
    objects = spawn_objects()
    running = True

    view_btn = pygame.Rect(20, HEIGHT - BUTTON_HEIGHT - 20, 150, BUTTON_HEIGHT)
    dir_btn = pygame.Rect(20, HEIGHT - 2 * BUTTON_HEIGHT - 40, 150, BUTTON_HEIGHT)
    dragging_slider = False

    while running:
        screen.fill((10, 10, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if view_btn.collidepoint(mx, my):
                    VIEW_MODE = "GROUND" if VIEW_MODE == "PLAN" else "PLAN"
                elif dir_btn.collidepoint(mx, my):
                    DIRECTION = "WEST" if DIRECTION == "EAST" else "EAST"
                elif (SLIDER_X <= mx <= SLIDER_X + SLIDER_W and
                      SLIDER_Y - 10 <= my <= SLIDER_Y + SLIDER_H + 10):
                    dragging_slider = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False
            elif event.type == pygame.MOUSEMOTION and dragging_slider:
                mx, _ = event.pos
                ratio = (mx - SLIDER_X) / SLIDER_W
                ratio = max(0, min(1, ratio))
                SPEED_MULTIPLIER = 0.5 + ratio * 2.5

        for obj in objects:
            obj.update()
            obj.draw(screen)

        draw_button(screen, view_btn, f"View: {VIEW_MODE}", True)
        draw_button(screen, dir_btn, f"Dir: {DIRECTION}", True)
        draw_slider(screen, SPEED_MULTIPLIER)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
