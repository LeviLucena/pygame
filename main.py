#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║       S P A C E   I N V A D E R S  — v4  ARCADE        ║
║   MULTI · MACHINEGUN · FLAME  |  CRT · Shake · March   ║
╠══════════════════════════════════════════════════════════╣
║  ← → / A D  Move    SPACE  Shoot    P  Pause  M  Mute  ║
╚══════════════════════════════════════════════════════════╝
  Reference: @DaleCloudman Rust terminal invaders
"""

import pygame, sys, random, math, io, wave, struct, time

# ══════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════
SW, SH  = 900, 650
FPS     = 60
TITLE   = "Space Invaders — Arcade Edition"

BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
GREEN    = (  0, 230,   0)       # mid enemies
MAGENTA  = (220,   0, 220)       # bottom enemies
YELLOW   = (255, 220,   0)       # top enemies
CYAN     = (  0, 220, 255)       # player
RED      = (255,  30,  30)       # UFO / flame
ORANGE   = (255, 140,   0)       # enemy bullets / flame
GRAY     = (130, 130, 130)
DKGRAY   = ( 25,  25,  35)
MGRAY    = ( 65,  65,  80)
PU_MULTI = (  0, 200, 255)
PU_MG    = (255, 220,  50)
PU_FL    = (255,  80,   0)

# Gameplay
PLAYER_SPEED      = 5
BULLET_SPD        = 13
MG_SPD            = 16
MG_COOLDOWN       = 4
MG_MAX            = 14
MULTI_SPD         = 13
ENEMY_BULLET_SPD  = 5
ENEMY_SHOOT_BASE  = 0.0011

ENEMY_COLS   = 11
ENEMY_ROWS   = 5
CELL_W       = 60
CELL_H       = 46
GRID_X       = (SW - ENEMY_COLS * CELL_W) // 2
GRID_Y       = 90

ENEMY_STEP_X = 10
ENEMY_STEP_Y = 18

FLAME_BEAM_W   = 52    # width of flamethrower column
FLAME_BEAM_DUR = 8     # frames per trigger
FLAME_COOLDOWN = 22

LIVES_START      = 3
POWERUP_DURATION = 60 * 3    # 3 seconds
POWERUP_DROP     = 0.20
MAX_PARTICLES    = 500

ROW_COLORS = [YELLOW, YELLOW, GREEN, MAGENTA, MAGENTA]
ROW_PTS    = [30, 30, 20, 10, 10]

# ══════════════════════════════════════════════════════════════════
#  SPRITE DATA — pixel art matching reference video aesthetic
#  Scale 4px per dot
# ══════════════════════════════════════════════════════════════════
SC = 4   # default sprite scale

_SHAPES = {
    # Player — simple cyan pyramid/ship
    "player": [
        "..1..",
        ".111.",
        "11111",
        "11111",
        "11111",
    ],

    # Yellow top enemy — hollow arch / bracket (2 frames)
    "yel0": [
        "1111111",
        "1.....1",
        "1.....1",
        "1.....1",
    ],
    "yel1": [
        "1111111",
        "1.....1",
        "1.....1",
        ".1...1.",
    ],

    # Green mid enemy — chunky crown/M shape (2 frames)
    "grn0": [
        "1.1.1.1",
        "1111111",
        "1111111",
        ".1.1.1.",
    ],
    "grn1": [
        ".1.1.1.",
        "1111111",
        "1111111",
        "1.1.1.1",
    ],

    # Magenta bottom enemy — Y-fork / antenna (2 frames)
    "mag0": [
        "1.....1",
        ".1...1.",
        "..111..",
        "..111..",
        "...1...",
    ],
    "mag1": [
        ".1...1.",
        "1.....1",
        "..111..",
        "..111..",
        "...1...",
    ],

    # UFO
    "ufo": [
        "...111111...",
        ".111111111..",
        "1.11.11.11.1",
        "111111111111",
        ".11..11..11.",
        "...1....1...",
    ],

    # Powerup icons (scale 3)
    "pu_multi": [
        "1.1.1",
        "11111",
        "11111",
        ".1.1.",
    ],
    "pu_mg": [
        ".111.",
        "11111",
        "1.1.1",
        "11111",
        ".111.",
    ],
    "pu_fl": [
        "..1..",
        ".111.",
        "11111",
        "11111",
        ".111.",
        "..1..",
    ],

    # ── BOSS — OMEGA DREADNOUGHT ──────────────────────────────────
    # 26 cols × 6 rows  (rendered at scale=26 → 676×156 px)
    # Estilo Space Invaders: bloco largo, dome central, asas abertas
    "boss0": [
        "....111111111111111111....",   # dome top
        "..1111111111111111111111..",   # dome wide
        "1.1111111111111111111111.1",   # body + notch wings
        "11111111111111111111111111",   # solid row
        "11111111111111111111111111",   # solid row
        "1.1.1.11111111111111.1.1.1",  # detail — feet/vents
    ],
    "boss1": [
        "....111111111111111111....",   # dome top (same)
        "..1111111111111111111111..",   # dome wide (same)
        "1.1111111111111111111111.1",   # body (same)
        "11111111111111111111111111",   # solid (same)
        "11111111111111111111111111",   # solid (same)
        ".1.1.1111111111111111.1.1.",   # detail — inverted animation (26)
    ],

    # Weapon turret — 6 cols × 9 rows (rendered at scale=9 → 54×81 px)
    "boss_wpn0": [
        ".1111.",  # turret cap
        "111111",
        "1.11.1",  # detail
        "111111",
        "1.11.1",  # detail
        "111111",
        "..11..",  # barrel
        "..11..",
        "..11..",  # muzzle
    ],
    "boss_wpn1": [
        ".1111.",  # turret cap (same)
        "111111",
        "111111",  # glow frame — solid
        "111111",
        "111111",
        "111111",
        "..11..",
        "..11..",
        "..11..",
    ],
}

_CACHE: dict = {}

def _surf(key: str, color: tuple, scale: int = SC) -> pygame.Surface:
    ck = (key, color, scale)
    if ck not in _CACHE:
        shape = _SHAPES[key]
        cols  = max(len(r) for r in shape)
        rows  = len(shape)
        s     = pygame.Surface((cols*scale, rows*scale), pygame.SRCALPHA)
        for r, row in enumerate(shape):
            for c, ch in enumerate(row):
                if ch == '1':
                    pygame.draw.rect(s, color, (c*scale, r*scale, scale, scale))
        _CACHE[ck] = s
    return _CACHE[ck]


# ══════════════════════════════════════════════════════════════════
#  PIXEL FONT  (draw big retro letters like the reference title)
# ══════════════════════════════════════════════════════════════════
# We'll use a large SysFont with a glow effect to mimic the reference
def draw_glitch_title(surf, text, x, y, color, font, t, intensity=1.0):
    """Neon glow + chromatic aberration + random glitch scanlines."""
    w, h = font.size(text)

    # ── Outer glow (3 passes)
    for r in (6, 4, 2):
        gs = pygame.Surface((w + r*2, h + r*2), pygame.SRCALPHA)
        gl = font.render(text, True, (*color, max(0, int(55 - r*8))))
        gs.blit(gl, (r, r))
        surf.blit(gs, (x - r, y - r))

    # ── Chromatic aberration — red left, blue right
    ca = int(4 * intensity)
    r_lbl = font.render(text, True, (255, 0, 0))
    b_lbl = font.render(text, True, (0, 80, 255))
    r_lbl.set_alpha(90); b_lbl.set_alpha(90)
    glitch_drift = int(2 * math.sin(t * 0.07))
    surf.blit(r_lbl, (x - ca + glitch_drift, y), special_flags=pygame.BLEND_ADD)
    surf.blit(b_lbl, (x + ca - glitch_drift, y), special_flags=pygame.BLEND_ADD)

    # ── Main text
    lbl = font.render(text, True, color)
    surf.blit(lbl, (x, y))

    # ── Random glitch band (occasional horizontal slice shift)
    if random.random() < 0.04 * intensity:
        gy  = y + random.randint(4, h - 8)
        gbw = random.randint(30, w // 2)
        gbx = x + random.randint(0, w - gbw)
        clip_r = pygame.Rect(gbx, gy, gbw, random.randint(2, 5))
        if (clip_r.right <= surf.get_width() and
                clip_r.bottom <= surf.get_height() and clip_r.width > 0):
            try:
                tmp = surf.subsurface(clip_r).copy()
                surf.blit(tmp, (gbx + random.randint(-10, 10), gy))
            except Exception:
                pass


def draw_pixel_title(surf, text, x, y, color, font, glow=True):
    """Legacy wrapper — forwards to glitch version."""
    draw_glitch_title(surf, text, x, y, color, font, t=0, intensity=0.4)


def draw_pixel_glitch_title(surf, text, x, y, color, pixel_font, scale, t, intensity=1.0):
    """Pixel retro title: renders small → scale-up (nearest-neighbor) → glitch/glow."""
    # Render base at small size (no antialiasing = sharp pixel edges)
    base = pixel_font.render(text, False, color)
    W, H = base.get_width() * scale, base.get_height() * scale
    big  = pygame.transform.scale(base, (W, H))

    # ── Outer glow (3 passes using alpha surfaces)
    for r, alpha in ((8, 25), (5, 45), (3, 65)):
        gs   = pygame.Surface((W + r*2, H + r*2), pygame.SRCALPHA)
        gbig = pygame.transform.scale(base.copy(), (W, H))
        gbig.set_alpha(alpha)
        gs.blit(gbig, (r, r))
        surf.blit(gs, (x - r, y - r))

    # ── Chromatic aberration — red left, blue right
    ca   = max(2, int(3 * intensity))
    r_s  = pixel_font.render(text, False, (255, 0, 0))
    b_s  = pixel_font.render(text, False, (0, 80, 255))
    r_big = pygame.transform.scale(r_s, (W, H))
    b_big = pygame.transform.scale(b_s, (W, H))
    drift = int(2 * math.sin(t * 0.07))
    r_big.set_alpha(90); b_big.set_alpha(90)
    surf.blit(r_big, (x - ca + drift, y), special_flags=pygame.BLEND_ADD)
    surf.blit(b_big, (x + ca - drift, y), special_flags=pygame.BLEND_ADD)

    # ── Main text
    surf.blit(big, (x, y))

    # ── Occasional glitch band (horizontal slice shift)
    if random.random() < 0.04 * intensity:
        gy   = y + random.randint(scale, H - scale * 2)
        gbw  = random.randint(scale * 3, W // 2)
        gbx  = x + random.randint(0, max(0, W - gbw))
        clip = pygame.Rect(gbx, gy, gbw, random.randint(scale, scale * 2))
        if (clip.right <= surf.get_width() and
                clip.bottom <= surf.get_height() and clip.width > 0):
            try:
                tmp = surf.subsurface(clip).copy()
                surf.blit(tmp, (gbx + random.randint(-scale*2, scale*2), gy))
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════
#  SOUND
# ══════════════════════════════════════════════════════════════════
SR = 22050

def _wav(samples):
    buf = io.BytesIO()
    with wave.open(buf, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(struct.pack(f'<{len(samples)}h',
            *(int(max(-1, min(1, s)) * 32767) for s in samples)))
    return buf.getvalue()

def _synth(freq, dur, vol=0.4, wt='square', f2=None, nm=0.0):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        f = freq if f2 is None else freq + (f2-freq)*i/n
        if   wt=='square': v = vol if math.sin(2*math.pi*f*t)>=0 else -vol
        elif wt=='sine':   v = vol*math.sin(2*math.pi*f*t)
        elif wt=='tri':    ph=(f*t)%1.0; v=vol*(4*abs(ph-0.5)-1)
        elif wt=='noise':  v=vol*random.uniform(-1,1)
        else: v=0.0
        if nm>0: v=v*(1-nm)+random.uniform(-vol,vol)*nm
        out.append(v*min(1,t/0.01)*max(0,1-i/n))
    return pygame.mixer.Sound(io.BytesIO(_wav(out)))


class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=SR, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(32)
        self.muted = False
        self._s = {}
        self._build()

    def _build(self):
        s = self._s
        s['shoot']    = _synth(900,  0.09, wt='square', f2=200)
        s['mg0']      = _synth(1100, 0.05, vol=0.28, wt='square', f2=700)
        s['mg1']      = _synth(1000, 0.05, vol=0.28, wt='square', f2=650)
        s['mg2']      = _synth(1200, 0.05, vol=0.28, wt='square', f2=750)
        s['multi']    = _synth(750,  0.08, vol=0.32, wt='square', f2=400)
        s['flame']    = _synth(200,  0.12, vol=0.6,  wt='noise', nm=0.8)
        s['expl_sm']  = _synth(200,  0.18, vol=0.4,  wt='noise', f2=80)
        s['expl_md']  = _synth(120,  0.28, vol=0.5,  wt='noise', f2=50)
        s['expl_lg']  = _synth(80,   0.38, vol=0.6,  wt='noise', f2=30)
        s['march0']   = _synth(160,  0.06, vol=0.18, wt='square')
        s['march1']   = _synth(130,  0.06, vol=0.18, wt='square')
        s['march2']   = _synth(100,  0.06, vol=0.18, wt='square')
        s['march3']   = _synth(80,   0.06, vol=0.18, wt='square')
        s['ufo']      = _synth(440,  0.08, wt='square', f2=880)
        s['ufo_hit']  = _synth(300,  0.25, wt='square', f2=40)
        s['lose_life']= _synth(80,   0.55, vol=0.6, wt='tri', f2=25)
        s['level_up'] = _synth(660,  0.35, wt='sine', f2=1320)
        s['gameover'] = _synth(55,   0.85, vol=0.6, wt='tri', f2=18)
        s['powerup']  = _synth(400,  0.28, wt='sine', f2=950)
        s['boss_hit']   = _synth(300,  0.15, vol=0.5,  wt='noise', f2=100)
        s['boss_expl']  = _synth(60,   0.65, vol=0.7,  wt='noise', f2=20)
        s['boss_intro'] = _synth(80,   0.8,  vol=0.55, wt='tri',   f2=40)
        s['missile']    = _synth(600,  0.10, vol=0.3,  wt='square',f2=1200)
        s['shield_brk'] = _synth(200,  0.5,  vol=0.6,  wt='tri',   f2=800)

    def play(self, name):
        if not self.muted and name in self._s: self._s[name].play()
    def play_mg(self):
        if not self.muted: self._s[f'mg{random.randint(0,2)}'].play()
    def play_march(self, i):
        if not self.muted: self._s[f'march{i}'].play()
    def play_expl(self, sz='md'):
        if not self.muted: self._s[f'expl_{sz}'].play()


# ══════════════════════════════════════════════════════════════════
#  SCREEN SHAKE
# ══════════════════════════════════════════════════════════════════
class ScreenShake:
    MAX = 18   # HARDCORE — amplitude máxima
    def __init__(self): self.trauma = 0.0; self._noise_t = 0.0
    def shake(self, v): self.trauma = min(1.0, self.trauma + v)
    def update(self): self.trauma = max(0.0, self.trauma - 0.032)
    def offset(self):
        if self.trauma < 0.01: return (0,0)
        t2 = self.trauma**2
        # Perlin-like: use sin with different frequencies for smooth shake
        self._noise_t += 0.18
        ox = self.MAX * t2 * math.sin(self._noise_t * 2.3 + 1.1)
        oy = self.MAX * t2 * math.sin(self._noise_t * 1.7 + 2.5)
        # Add high-freq jitter on strong hits
        if self.trauma > 0.4:
            ox += random.uniform(-4, 4) * t2
            oy += random.uniform(-4, 4) * t2
        return (int(ox), int(oy))


# ══════════════════════════════════════════════════════════════════
#  SCREEN FLASH
# ══════════════════════════════════════════════════════════════════
class FlashFX:
    def __init__(self): self.alpha=0; self.color=WHITE
    def flash(self, c, a=130): self.color=c; self.alpha=a
    def update(self): self.alpha=max(0,self.alpha-16)
    def draw(self, surf):
        if self.alpha>4:
            s=pygame.Surface((SW,SH),pygame.SRCALPHA)
            s.fill((*self.color,self.alpha)); surf.blit(s,(0,0))


# ══════════════════════════════════════════════════════════════════
#  CRT OVERLAY (pre-computed)
# ══════════════════════════════════════════════════════════════════
def _make_crt(w, h):
    s = pygame.Surface((w,h), pygame.SRCALPHA)
    for y in range(0, h, 2):
        pygame.draw.line(s, (0,0,0,50), (0,y), (w,y))
    for i in range(70):
        a = min(255, max(0, int(2.8*(69-i))))
        pygame.draw.rect(s, (0,0,0,a), (i,i,w-i*2,h-i*2), 1)
    return s


# ══════════════════════════════════════════════════════════════════
#  MARCH SOUND
# ══════════════════════════════════════════════════════════════════
class MarchSound:
    def __init__(self): self._i=0
    def on_move(self, sfx): sfx.play_march(self._i); self._i=(self._i+1)%4


# ══════════════════════════════════════════════════════════════════
#  STARS
# ══════════════════════════════════════════════════════════════════
class Stars:
    def __init__(self):
        self.pts = [(random.randint(0,SW), random.randint(0,SH),
                     random.uniform(0.2,1.0)) for _ in range(160)]
    def draw(self, surf):
        for x,y,b in self.pts:
            v=int(70*b); sz=2 if b>0.85 else 1
            pygame.draw.rect(surf,(v,v,int(v*1.1)),(x,y,sz,sz))


# ══════════════════════════════════════════════════════════════════
#  PARTICLE  (small ASCII-style sparks — like reference explosion)
# ══════════════════════════════════════════════════════════════════
class Particle:
    __slots__=('x','y','vx','vy','color','life','max_life','sz','star')
    def __init__(self, x, y, color, star=False):
        self.x,self.y=float(x),float(y)
        self.vx=random.uniform(-3.5,3.5)
        self.vy=random.uniform(-4.5,0.5)
        self.color=color
        self.life=random.randint(14,36)
        self.max_life=self.life
        self.sz=random.randint(2,4)
        self.star=star  # render as '*' shape
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.25; self.life-=1
    def draw(self, surf):
        a=self.life/self.max_life
        c=tuple(int(ch*a) for ch in self.color)
        s=max(1,int(self.sz*a))
        if self.star and s>1:
            cx,cy=int(self.x),int(self.y)
            pygame.draw.line(surf,c,(cx-s,cy),(cx+s,cy),1)
            pygame.draw.line(surf,c,(cx,cy-s),(cx,cy+s),1)
        else:
            pygame.draw.rect(surf,c,(int(self.x),int(self.y),s,s))
    @property
    def alive(self): return self.life>0


# ══════════════════════════════════════════════════════════════════
#  EXHAUST PARTICLE
# ══════════════════════════════════════════════════════════════════
class Exhaust:
    __slots__=('x','y','vx','vy','life','max_life')
    def __init__(self,x,y):
        self.x,self.y=float(x),float(y)
        self.vx=random.uniform(-0.7,0.7)
        self.vy=random.uniform(1.5,3.8)
        self.life=random.randint(8,16)
        self.max_life=self.life
    def update(self): self.x+=self.vx; self.y+=self.vy; self.life-=1
    def draw(self,surf):
        a=self.life/self.max_life
        g=int(180*a); b=int(255*a); s=max(1,int(3*a))
        pygame.draw.rect(surf,(int(20*a),g,b),(int(self.x),int(self.y),s,s))
    @property
    def alive(self): return self.life>0


# ══════════════════════════════════════════════════════════════════
#  FLAME PARTICLE  (dense fire beam)
# ══════════════════════════════════════════════════════════════════
class FlamePart:
    __slots__=('x','y','vx','vy','life','max_life','phase')
    def __init__(self,x,y,vy=-1):
        self.x,self.y=float(x),float(y)
        self.vx=random.uniform(-1.2,1.2)
        self.vy=random.uniform(vy-1,vy+0.5)
        self.life=random.randint(6,18)
        self.max_life=self.life
        self.phase=random.random()*math.pi*2
    def update(self): self.x+=self.vx; self.y+=self.vy; self.life-=1
    def draw(self,surf):
        a=self.life/self.max_life
        r=int(255*min(1,a*1.6)); g=int(140*max(0,a-0.25)); b=0
        s=max(2,int(5*a))
        pygame.draw.rect(surf,(r,g,b),(int(self.x),int(self.y),s,s))
    @property
    def alive(self): return self.life>0


# ══════════════════════════════════════════════════════════════════
#  BULLET
# ══════════════════════════════════════════════════════════════════
class Bullet:
    W=3; H=12
    TRAIL=5
    def __init__(self,x,y,vx,vy,color,enemy=False):
        self.x=float(x)-self.W/2; self.y=float(y)
        self.vx=vx; self.vy=vy
        self.color=color; self.enemy=enemy; self.alive=True
        self._tr:list[tuple]=[]
    def update(self):
        self._tr.append((int(self.x),int(self.y)))
        if len(self._tr)>self.TRAIL: self._tr.pop(0)
        self.x+=self.vx; self.y+=self.vy
        if self.y<-20 or self.y>SH+20 or self.x<-20 or self.x>SW+20:
            self.alive=False
    def draw(self,surf):
        cr,cg,cb=self.color
        for i,(tx,ty) in enumerate(self._tr):
            a=(i+1)/(len(self._tr)+1)*0.45
            pygame.draw.rect(surf,(int(cr*a),int(cg*a),int(cb*a)),(tx,ty,self.W,4))
        if self.enemy:
            ix,iy=int(self.x),int(self.y)
            pts=[(ix,iy),(ix+self.W,iy+4),(ix,iy+8),(ix+self.W,iy+12)]
            pygame.draw.lines(surf,self.color,False,pts,2)
        else:
            pygame.draw.rect(surf,self.color,(int(self.x),int(self.y),self.W,self.H))
            pygame.draw.rect(surf,WHITE,(int(self.x),int(self.y),self.W,3))
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)


# ══════════════════════════════════════════════════════════════════
#  MUZZLE FLASH
# ══════════════════════════════════════════════════════════════════
class MuzzleFlash:
    def __init__(self): self.life=0; self.x=self.y=0; self.color=YELLOW
    def fire(self,x,y,col=YELLOW): self.x,self.y,self.color=x,y,col; self.life=4
    def update(self):
        if self.life>0: self.life-=1
    def draw(self,surf):
        if self.life<=0: return
        a=self.life/4; r=int(16*a)
        cr,cg,cb=self.color
        pygame.draw.circle(surf,(min(255,cr+60),min(255,cg+60),min(255,cb+60)),(self.x,self.y),r)
        if r>3: pygame.draw.circle(surf,WHITE,(self.x,self.y),r//2)


# ══════════════════════════════════════════════════════════════════
#  POWERUP DROP
# ══════════════════════════════════════════════════════════════════
WEAPON_NORMAL='normal'; WEAPON_MG='mg'; WEAPON_MULTI='multi'; WEAPON_FLAME='flame'

class Powerup:
    FALL=1.6
    def __init__(self,x,y,kind):
        self.x,self.y=float(x),float(y)
        self.kind=kind; self.alive=True; self._f=0
        col={WEAPON_MG:PU_MG,WEAPON_MULTI:PU_MULTI,WEAPON_FLAME:PU_FL}[kind]
        key={'mg':'pu_mg','multi':'pu_multi','flame':'pu_fl'}[kind]
        self._s=_surf(key,col,3)
        self.W=self._s.get_width(); self.H=self._s.get_height()
        self._col=col
        self._fn=pygame.font.SysFont("Courier New",9,bold=True)
    def update(self):
        self.y+=self.FALL; self._f+=1
        self.alive=self.y<SH+self.H
    def draw(self,surf):
        bob=int(math.sin(self._f*0.12)*3)
        ga=int(100+80*math.sin(self._f*0.2))
        gs=pygame.Surface((self.W+12,self.H+12),pygame.SRCALPHA)
        pygame.draw.rect(gs,(*self._col,ga),(0,0,self.W+12,self.H+12),2,border_radius=4)
        surf.blit(gs,(int(self.x)-6,int(self.y)+bob-6))
        surf.blit(self._s,(int(self.x),int(self.y)+bob))
        nm={'mg':'MG','multi':'3X','flame':'FIRE'}[self.kind]
        lbl=self._fn.render(nm,True,self._col)
        surf.blit(lbl,(int(self.x)+self.W//2-lbl.get_width()//2,
                       int(self.y)+bob+self.H+2))
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)


# ══════════════════════════════════════════════════════════════════
#  PLAYER
# ══════════════════════════════════════════════════════════════════
class Player:
    INV=150
    def __init__(self):
        self._s   = _surf("player",CYAN,SC)
        self.W    = self._s.get_width()
        self.H    = self._s.get_height()
        self.bullets:list[Bullet]=[]
        self.exhaust:list[Exhaust]=[]
        self.flame_parts:list[FlamePart]=[]
        self.weapon=WEAPON_NORMAL; self.wtimer=0; self.shoot_cd=0
        self.invincible=0; self.blink=0
        self.flash=MuzzleFlash()
        # flame beam state
        self.flame_beam=False; self.flame_beam_x=0
        self.reset_pos()

    def reset_pos(self):
        self.x=SW//2-self.W//2; self.y=SH-72

    def collect(self,kind,sfx):
        self.weapon=kind; self.wtimer=POWERUP_DURATION; sfx.play('powerup')

    def update(self,keys,sfx):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.x-=PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x+=PLAYER_SPEED
        self.x=max(0,min(SW-self.W,self.x))

        if self.wtimer>0:
            self.wtimer-=1
            if self.wtimer==0: self.weapon=WEAPON_NORMAL

        if self.shoot_cd>0: self.shoot_cd-=1

        # MG auto-fire
        if self.weapon==WEAPON_MG and keys[pygame.K_SPACE] and self.shoot_cd==0:
            self._fire_mg(sfx)

        # Flame beam — active while space held
        if self.weapon==WEAPON_FLAME and keys[pygame.K_SPACE]:
            self.flame_beam=True
            self.flame_beam_x=int(self.x)+self.W//2
            # spawn dense flame particles filling column
            for _ in range(10):
                px=self.flame_beam_x+random.randint(-FLAME_BEAM_W//2,FLAME_BEAM_W//2)
                py=random.randint(40, self.y)
                self.flame_parts.append(FlamePart(px,py,vy=random.uniform(-3,-1)))
        else:
            self.flame_beam=False

        if self.invincible>0:
            self.invincible-=1
            self.blink=(self.blink+1)%12

        # engine exhaust
        cx=int(self.x)+self.W//2
        for _ in range(3 if self.weapon==WEAPON_MG else 2):
            self.exhaust.append(Exhaust(cx+random.randint(-7,7), self.y+self.H))

        self.flash.update()
        for b in self.bullets: b.update()
        for e in self.exhaust: e.update()
        for f in self.flame_parts: f.update()
        self.bullets=[b for b in self.bullets if b.alive]
        self.exhaust=(self.exhaust[-60:])
        self.exhaust=[e for e in self.exhaust if e.alive]
        self.flame_parts=[f for f in self.flame_parts if f.alive]

    def shoot(self,sfx):
        cx=int(self.x)+self.W//2
        if self.weapon==WEAPON_NORMAL and self.shoot_cd==0:
            self.bullets.append(Bullet(cx,self.y,0,-BULLET_SPD,YELLOW))
            self.flash.fire(cx,self.y,YELLOW)
            self.shoot_cd=18; sfx.play('shoot')
        elif self.weapon==WEAPON_MULTI and self.shoot_cd==0:
            # 3-way spread
            for a in [-12,0,12]:
                rad=math.radians(a-90)
                vx=MULTI_SPD*math.cos(rad); vy=MULTI_SPD*math.sin(rad)
                self.bullets.append(Bullet(cx,self.y,vx,vy,PU_MULTI))
            self.flash.fire(cx,self.y,PU_MULTI)
            self.shoot_cd=22; sfx.play('multi')
        elif self.weapon==WEAPON_FLAME and self.shoot_cd==0:
            self.shoot_cd=FLAME_COOLDOWN; sfx.play('flame')

    def _fire_mg(self,sfx):
        if len(self.bullets)>=MG_MAX: return
        cx=int(self.x)+self.W//2
        sp=random.uniform(-1.6,1.6)
        self.bullets.append(Bullet(cx+sp,self.y,sp*0.2,-MG_SPD,PU_MG))
        self.flash.fire(cx,self.y,PU_MG)
        self.shoot_cd=MG_COOLDOWN; sfx.play_mg()

    def flame_beam_rect(self):
        if self.flame_beam:
            return pygame.Rect(self.flame_beam_x-FLAME_BEAM_W//2,
                               0, FLAME_BEAM_W, self.y)
        return pygame.Rect(-9999,-9999,0,0)

    def draw(self,surf):
        for e in self.exhaust: e.draw(surf)
        for f in self.flame_parts: f.draw(surf)

        if self.flame_beam:
            # render beam glow column
            bx=self.flame_beam_x-FLAME_BEAM_W//2
            gs=pygame.Surface((FLAME_BEAM_W,self.y),pygame.SRCALPHA)
            for row in range(0,self.y,4):
                a=int(30+20*random.random())
                pygame.draw.rect(gs,(255,int(60*random.random()),0,a),(0,row,FLAME_BEAM_W,4))
            surf.blit(gs,(bx,0))

        if self.invincible>0 and self.blink<6: return

        # weapon aura
        if self.weapon==WEAPON_MG:
            gs=pygame.Surface((self.W+10,self.H+10),pygame.SRCALPHA)
            pygame.draw.ellipse(gs,(*PU_MG,45),(0,0,self.W+10,self.H+10))
            surf.blit(gs,(int(self.x)-5,self.y-5))
        elif self.weapon==WEAPON_FLAME:
            gs=pygame.Surface((self.W+14,self.H+14),pygame.SRCALPHA)
            pygame.draw.ellipse(gs,(*PU_FL,50),(0,0,self.W+14,self.H+14))
            surf.blit(gs,(int(self.x)-7,self.y-7))
        elif self.weapon==WEAPON_MULTI:
            gs=pygame.Surface((self.W+10,self.H+10),pygame.SRCALPHA)
            pygame.draw.ellipse(gs,(*PU_MULTI,45),(0,0,self.W+10,self.H+10))
            surf.blit(gs,(int(self.x)-5,self.y-5))

        surf.blit(self._s,(int(self.x),self.y))
        for b in self.bullets: b.draw(surf)
        self.flash.draw(surf)

    @property
    def rect(self): return pygame.Rect(int(self.x),self.y,self.W,self.H)

    def hit(self):
        self.invincible=self.INV; self.blink=0
        self.weapon=WEAPON_NORMAL; self.wtimer=0


# ══════════════════════════════════════════════════════════════════
#  ENEMY
# ══════════════════════════════════════════════════════════════════
_ROW_KEYS=[('yel0','yel1'),('yel0','yel1'),
           ('grn0','grn1'),('mag0','mag1'),('mag0','mag1')]

class Enemy:
    def __init__(self,col,row,x,y):
        self.col=col; self.row=row; self.x=x; self.y=y
        self.alive=True; self.frame=0; self.hit_flash=0
        self.color=ROW_COLORS[row]; self.points=ROW_PTS[row]
        k0,k1=_ROW_KEYS[row]
        self._s0=_surf(k0,self.color,SC); self._s1=_surf(k1,self.color,SC)
        self.W=self._s0.get_width(); self.H=self._s0.get_height()
    @property
    def surf(self): return self._s0 if self.frame==0 else self._s1
    @property
    def cx(self): return int(self.x)+self.W//2
    @property
    def cy(self): return int(self.y)+self.H//2
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    def draw(self,surf):
        if self.hit_flash>0:
            ws=self.surf.copy()
            ws.fill((255,255,255,180),special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(ws,(int(self.x),int(self.y))); self.hit_flash-=1
        else:
            surf.blit(self.surf,(int(self.x),int(self.y)))


# ══════════════════════════════════════════════════════════════════
#  ENEMY GRID
# ══════════════════════════════════════════════════════════════════
class EnemyGrid:
    def __init__(self,level=1):
        self.level=level; self.dx=1; self.tick=0; self.anim=0
        self.bullets:list[Bullet]=[]
        self.powerups:list[Powerup]=[]
        self._grid:list[Enemy]=[]
        self._march=MarchSound()
        self._spawn()

    def _spawn(self):
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                d=_surf(_ROW_KEYS[row][0],ROW_COLORS[row],SC)
                cx=GRID_X+col*CELL_W+(CELL_W-d.get_width())//2
                cy=GRID_Y+row*CELL_H+(CELL_H-d.get_height())//2
                self._grid.append(Enemy(col,row,cx,cy))

    @property
    def alive(self): return [e for e in self._grid if e.alive]

    def _delay(self):
        r=len(self.alive)/max(1,ENEMY_ROWS*ENEMY_COLS)
        return max(2,int(34*r)-(self.level-1)*3)

    def update(self,sfx):
        alive=self.alive
        if not alive: return
        self.tick+=1
        if self.tick>=self._delay():
            self.tick=0; self.anim^=1
            for e in alive: e.frame=self.anim
            left=min(e.x for e in alive); right=max(e.x+e.W for e in alive)
            drop=False
            if self.dx==1 and right>=SW-8: self.dx=-1; drop=True
            elif self.dx==-1 and left<=8:  self.dx=1;  drop=True
            for e in alive:
                if drop: e.y+=ENEMY_STEP_Y
                else:    e.x+=self.dx*ENEMY_STEP_X
            self._march.on_move(sfx)

        prob=ENEMY_SHOOT_BASE*(1+(self.level-1)*0.25)
        for e in alive:
            if random.random()<prob:
                self.bullets.append(Bullet(e.cx,e.y+e.H,0,ENEMY_BULLET_SPD,ORANGE,enemy=True))

        for b in self.bullets: b.update()
        for p in self.powerups: p.update()
        self.bullets=[b for b in self.bullets if b.alive]
        self.powerups=[p for p in self.powerups if p.alive]

    def kill(self,e:Enemy)->list:
        e.alive=False
        if random.random()<POWERUP_DROP:
            kind=random.choice([WEAPON_MG,WEAPON_MULTI,WEAPON_FLAME])
            self.powerups.append(Powerup(e.cx-12,e.cy,kind))
        # ASCII-style star+dot explosion particles
        parts=[]
        for _ in range(12):
            parts.append(Particle(e.cx,e.cy,e.color,star=True))
        for _ in range(8):
            parts.append(Particle(e.cx,e.cy,WHITE))
        return parts

    def draw(self,surf):
        for e in self._grid:
            if e.alive: e.draw(surf)
        for b in self.bullets: b.draw(surf)
        for p in self.powerups: p.draw(surf)

    def lowest_y(self):
        a=self.alive; return max((e.y+e.H for e in a),default=0)
    def all_dead(self): return not self.alive


# ══════════════════════════════════════════════════════════════════
#  UFO
# ══════════════════════════════════════════════════════════════════
class UFO:
    VALS=[50,100,150,200,300]
    def __init__(self):
        self._s=_surf("ufo",RED,3)
        self.W=self._s.get_width(); self.H=self._s.get_height()
        self.active=False; self.x=0.0; self.dx=2
        self._timer=random.randint(450,1200)
        self._trail:list=[]
    def update(self,sfx):
        if not self.active:
            self._timer-=1
            if self._timer<=0:
                self.active=True
                if random.random()<0.5: self.x=-self.W; self.dx=2
                else: self.x=SW; self.dx=-2
                sfx.play('ufo')
        else:
            self._trail.append((int(self.x+self.W//2),42+self.H//2))
            if len(self._trail)>10: self._trail.pop(0)
            self.x+=self.dx
            if self.x<-self.W-20 or self.x>SW+20: self._reset()
    def _reset(self):
        self.active=False; self._timer=random.randint(450,1200); self._trail=[]
    def hit(self):
        pts=random.choice(self.VALS); self._reset(); return pts
    def draw(self,surf):
        if not self.active: return
        for i,(tx,ty) in enumerate(self._trail):
            a=(i+1)/(len(self._trail)+1); r=int(180*a); sz=max(1,int(4*a))
            pygame.draw.rect(surf,(r,0,0),(tx-sz//2,ty-sz//2,sz,sz))
        surf.blit(self._s,(int(self.x),42))
    @property
    def rect(self):
        return pygame.Rect(int(self.x),42,self.W,self.H) \
               if self.active else pygame.Rect(-9999,-9999,0,0)


# ══════════════════════════════════════════════════════════════════
#  FLOAT TEXT
# ══════════════════════════════════════════════════════════════════
class FloatText:
    def __init__(self,text,x,y,color,font):
        self.text=text; self.x=x; self.y=float(y); self.color=color
        self.font=font; self.life=50; self.max_life=50
    def update(self): self.y-=0.9; self.life-=1
    def draw(self,surf):
        a=self.life/self.max_life
        cr,cg,cb=self.color
        lbl=self.font.render(self.text,True,(int(cr*a),int(cg*a),int(cb*a)))
        surf.blit(lbl,(self.x-lbl.get_width()//2,int(self.y)))
    @property
    def alive(self): return self.life>0


# ══════════════════════════════════════════════════════════════════
#  BOSS — OMEGA DREADNOUGHT  (Level 5)
# ══════════════════════════════════════════════════════════════════
BOSS_SC     = 16       # scale do sprite UFO boss (12 cols × 16 = 192 px)
BOSS_WPN_SC = 7        # scale das armas  (6 cols × 7 = 42 px)
BOSS_W      = 192      # 12 cols × BOSS_SC  (usa shape "ufo")
BOSS_H      = 96       # 6 rows  × BOSS_SC
BOSS_WPN_W  = 42       # 6 cols  × BOSS_WPN_SC
BOSS_WPN_H  = 63       # 9 rows  × BOSS_WPN_SC
BOSS_HEALTH = 40       # hits para matar o boss
BOSS_SPD    = 1.4
BOSS_COLOR  = RED      # mesmo vermelho do UFO normal
BOSS_WPN_C  = ( 55, 200,  55)
BOSS_SCORE  = 5000
BOMB_SPD    = 2.2
BOMB_COL    = (180,  80, 255)
EXPL_RAD    = 72


class BossExplosion:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.life = 40; self.max_life = 40
        self.alive    = True
        self._damaged = False   # True once it has hurt the player

    def update(self):
        self.life -= 1
        if self.life <= 0: self.alive = False

    def draw(self, surf):
        t = self.life / self.max_life
        r = int(EXPL_RAD * (1.0 - t) * 2.6)
        if r < 2: return
        for w, col in [(5,(255,200,50)),(3,(255,100,20)),(1,(255,40,0))]:
            try: pygame.draw.circle(surf, col, (self.x, self.y), r, w)
            except: pass
        if t > 0.5:
            ir = max(2, int(EXPL_RAD * 0.5 * t))
            gs = pygame.Surface((ir*2, ir*2), pygame.SRCALPHA)
            gs.fill((255, 220, 80, int(180*(t-0.5)/0.5)))
            surf.blit(gs, (self.x-ir, self.y-ir))

    @property
    def damage_rect(self):
        return pygame.Rect(self.x-EXPL_RAD, self.y-35, EXPL_RAD*2, 55)


class BossBomb:
    def __init__(self, x, y):
        self.x = float(x); self.y = float(y)
        self.vy = BOMB_SPD
        self.alive = True
        self._trail: list = []

    def update(self):
        self._trail.append((int(self.x), int(self.y)))
        if len(self._trail) > 14: self._trail.pop(0)
        self.y += self.vy
        self.vy = min(self.vy + 0.05, 6.0)
        if self.y >= SH - 22: self.alive = False

    def draw(self, surf):
        for i,(tx,ty) in enumerate(self._trail):
            a = (i+1)/max(1,len(self._trail))
            pygame.draw.circle(surf,(int(160*a),int(50*a),int(220*a)),(tx,ty),max(1,int(a*4)))
        bx,by = int(self.x),int(self.y)
        pygame.draw.ellipse(surf, BOMB_COL,       (bx-8, by-12, 16, 22))
        pygame.draw.ellipse(surf, (220,140,255),   (bx-5, by-8,  10, 14))
        pygame.draw.circle(surf,  (255,220,50), (bx, by-14), 4)
        pygame.draw.circle(surf,  WHITE,         (bx, by-14), 2)

    @property
    def rect(self): return pygame.Rect(int(self.x)-8, int(self.y)-12, 16, 22)


class BossWeapon:
    W = BOSS_WPN_W
    H = BOSS_WPN_H

    def __init__(self, side: str, boss):
        self.side      = side
        self.boss      = boss
        self.hit_flash = 0

    @property
    def x(self):
        return self.boss.x + 8 if self.side=='left' else self.boss.x + BOSS_W - 8 - self.W

    @property
    def y(self):  return self.boss.y + BOSS_H + 4   # hangs below boss body

    @property
    def cx(self): return self.x + self.W // 2

    @property
    def cy(self): return self.y + self.H // 2

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def hit(self) -> bool:
        """Dano direto na vida do boss. Retorna True se morreu."""
        self.hit_flash = 10
        self.boss.health_hp = max(0, self.boss.health_hp - 1)
        self.boss._hit_flash = 6
        if self.boss.health_hp <= 0:
            self.boss.alive = False
            return True
        return False

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        fla  = self.hit_flash > 0
        self.hit_flash = max(0, self.hit_flash - 1)
        col = WHITE if fla else BOSS_WPN_C
        frm = (self.boss._frame // 20) % 2
        s   = _surf(f'boss_wpn{frm}', col, BOSS_WPN_SC)
        surf.blit(s, (x, y))
        # muzzle glow
        pulse = int(100 + 80*math.sin(pygame.time.get_ticks()*0.005))
        pygame.draw.rect(surf, (255, pulse, 0),
                         (x + self.W//2 - BOSS_WPN_SC, y + self.H + 2,
                          BOSS_WPN_SC*2, BOSS_WPN_SC), border_radius=2)


class Boss:
    def __init__(self):
        self.x           = float((SW - BOSS_W) // 2)
        self.y           = float(-(BOSS_H + 60))
        self._target_y   = 32.0
        self._enter_done = False
        self.dx          = 1
        self.health_hp   = BOSS_HEALTH
        self.alive       = True
        self._frame      = 0
        self._hit_flash  = 0
        self.weapon_l    = BossWeapon('left',  self)
        self.weapon_r    = BossWeapon('right', self)
        self._blt_timer  = 0
        self._bmb_timer  = 0
        self._blt_cd     = 80
        self._bmb_cd     = 300
        self.bullets_down: list = []
        self.bombs:        list = []
        self.explosions:   list = []
        self.flame_parts:  list = []
        self._burst_count  = 0
        self._burst_timer  = 0
        self._flame_timer  = 0
        self._atk_mode     = 'normal'

    @property
    def cx(self): return int(self.x + BOSS_W // 2)

    @property
    def cy(self): return int(self.y + BOSS_H // 2)

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), BOSS_W, BOSS_H)

    def update(self, sfx, tgt_fn):
        self._frame += 1
        if not self._enter_done:
            self.y = min(self.y + 2.0, self._target_y)
            if self.y >= self._target_y:
                self._enter_done = True
                sfx.play('boss_intro')
            self._upd_proj(); return
        self.x += self.dx * BOSS_SPD
        if self.x + BOSS_W >= SW - 10: self.dx = -1
        if self.x <= 10:               self.dx =  1
        self._blt_timer += 1
        if self._blt_timer >= self._blt_cd:
            self._blt_timer = 0; self._fire_blt(sfx)
        self._bmb_timer += 1
        if self._bmb_timer >= self._bmb_cd:
            self._bmb_timer = 0; self._drop_bomb(sfx)
        # MG burst — fires one bullet every 5 frames until burst depleted
        if self._burst_count > 0:
            self._burst_timer += 1
            if self._burst_timer >= 5:
                self._burst_timer = 0; self._burst_count -= 1
                w = random.choice([self.weapon_l, self.weapon_r])
                self.bullets_down.append(
                    Bullet(w.cx + random.randint(-4, 4), w.y + w.H + 6,
                           random.uniform(-1.5, 1.5), ENEMY_BULLET_SPD + 3,
                           PU_MG, enemy=True))
                sfx.play_mg()
        # Flame beam — spawns FlamePart particles going downward
        if self._flame_timer > 0:
            self._flame_timer -= 1
            for w in (self.weapon_l, self.weapon_r):
                for _ in range(3):
                    px = w.cx + random.randint(-FLAME_BEAM_W//2, FLAME_BEAM_W//2)
                    py = w.y + w.H + random.randint(0, 12)
                    self.flame_parts.append(FlamePart(px, py, vy=random.uniform(3, 6)))
        self._upd_proj()
        self._hit_flash = max(0, self._hit_flash - 1)

    def _fire_blt(self, sfx):
        self._atk_mode = random.choice(['normal', 'normal', 'multi', 'mg', 'flame'])
        if self._atk_mode == 'normal':
            for w in (self.weapon_l, self.weapon_r):
                self.bullets_down.append(
                    Bullet(w.cx, w.y + w.H + 6, 0, ENEMY_BULLET_SPD + 2,
                           (255, 50, 50), enemy=True))
            sfx.play('shoot')
        elif self._atk_mode == 'multi':
            for w in (self.weapon_l, self.weapon_r):
                for ang in [-18, 0, 18]:
                    rad = math.radians(90 + ang)
                    vx  = (ENEMY_BULLET_SPD + 2) * math.cos(rad)
                    vy  = (ENEMY_BULLET_SPD + 2) * math.sin(rad)
                    self.bullets_down.append(
                        Bullet(w.cx, w.y + w.H + 6, vx, vy, PU_MULTI, enemy=True))
            sfx.play('multi')
        elif self._atk_mode == 'mg':
            self._burst_count = 10; self._burst_timer = 0
            sfx.play_mg()
        elif self._atk_mode == 'flame':
            self._flame_timer = 90
            sfx.play('flame')

    def _drop_bomb(self, sfx):
        self.bombs.append(BossBomb(self.cx, self.y + BOSS_H + 2))
        sfx.play_expl('md')

    def _upd_proj(self):
        for b  in self.bullets_down: b.update()
        for ex in self.explosions:   ex.update()
        for fp in self.flame_parts:  fp.update()
        new_bombs = []
        for bomb in self.bombs:
            bomb.update()
            if not bomb.alive:
                self.explosions.append(BossExplosion(int(bomb.x), SH - 25))
            else:
                new_bombs.append(bomb)
        self.bombs        = new_bombs
        self.bullets_down = [b  for b  in self.bullets_down if b.alive]
        self.explosions   = [ex for ex in self.explosions   if ex.alive]
        self.flame_parts  = [fp for fp in self.flame_parts  if fp.alive]

    def draw(self, surf):
        bx, by = int(self.x), int(self.y)
        t   = self._frame
        fla = self._hit_flash > 0

        # ── pixel-art sprite — mesmo shape do UFO, porém ENORME
        col = WHITE if fla else BOSS_COLOR
        s   = _surf('ufo', col, BOSS_SC)
        surf.blit(s, (bx, by))

        # ── glow pulsante sob a última linha do UFO (simula propulsão)
        if not fla:
            pulse = int(80 + 70*math.sin(t * 0.1))
            gy = by + BOSS_H - BOSS_SC
            for i in range(4):
                gx = bx + (2 + i*3) * BOSS_SC
                pygame.draw.rect(surf, (255, pulse, 0), (gx, gy, BOSS_SC, BOSS_SC))

        # ── armas
        self.weapon_l.draw(surf)
        self.weapon_r.draw(surf)

        # ── flame beam visual (coluna de fogo apontando para baixo)
        if self._flame_timer > 0:
            for w in (self.weapon_l, self.weapon_r):
                bx2 = w.cx - FLAME_BEAM_W // 2
                bh  = SH - (int(w.y) + w.H)
                if bh > 0:
                    gs2 = pygame.Surface((FLAME_BEAM_W, bh), pygame.SRCALPHA)
                    for row in range(0, bh, 4):
                        a2 = int(25 + 20 * random.random())
                        pygame.draw.rect(gs2, (255, int(60*random.random()), 0, a2),
                                         (0, row, FLAME_BEAM_W, 4))
                    surf.blit(gs2, (bx2, int(w.y) + w.H))

        # ── projéteis
        for b  in self.bullets_down: b.draw(surf)
        for bm in self.bombs:        bm.draw(surf)
        for ex in self.explosions:   ex.draw(surf)
        for fp in self.flame_parts:  fp.draw(surf)

    def draw_bars(self, surf, font):
        bar_w = 400; bar_h = 14
        bx = SW//2 - bar_w//2
        by = SH - 50
        tit = font.render("OMEGA DREADNOUGHT", True, RED)
        surf.blit(tit, (SW//2 - tit.get_width()//2, by))
        pct = self.health_hp / BOSS_HEALTH
        r = int(255*(1-pct)); g = int(200*pct)
        pygame.draw.rect(surf, (38,7,7), (bx, by+18, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(surf, (r,g,0),  (bx, by+18, int(bar_w*pct), bar_h), border_radius=4)
        pygame.draw.rect(surf, WHITE,    (bx, by+18, bar_w, bar_h), 1, border_radius=4)
        lbl = font.render("HP", True, RED)
        surf.blit(lbl, (bx - lbl.get_width() - 8, by+17))


# ══════════════════════════════════════════════════════════════════
#  GAME
# ══════════════════════════════════════════════════════════════════
S_MENU='menu'; S_PLAY='play'; S_PAUSE='pause'
S_NEXT='next'; S_OVER='over'; S_WIN='win'; S_HI='hiscores'


class Game:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((SW,SH))
        pygame.display.set_caption(TITLE)
        self.clock=pygame.time.Clock()
        self.fonts={
            'title_big': pygame.font.SysFont("Courier New",72,bold=True),
            'title_med': pygame.font.SysFont("Courier New",54,bold=True),
            'pixel':     pygame.font.Font(None, 14),
            'lg':  pygame.font.SysFont("Courier New",32,bold=True),
            'md':  pygame.font.SysFont("Courier New",20,bold=True),
            'sm':  pygame.font.SysFont("Courier New",14),
            'xs':  pygame.font.SysFont("Courier New",11),
            'hud': pygame.font.SysFont("Courier New",15),
        }
        self.sfx=SoundManager()
        self.stars=Stars()
        self.shake=ScreenShake()
        self.flash=FlashFX()
        self.crt=_make_crt(SW,SH)
        self._gs=pygame.Surface((SW,SH))   # game surface for shake blit

        self.particles:list[Particle]=[]
        self.floats:list[FloatText]=[]
        self.hi_scores:list[int]=[0]*5     # top-5 scores
        self._st_timer=0; self._menu_frm=0
        self.state=S_MENU
        self._fps_display=0; self._fps_timer=0

    # ── helpers ──────────────────────────────────────────────────
    def _start(self,level=1):
        self.state=S_PLAY; self.score=0; self.lives=LIVES_START; self.level=level
        self.player=Player(); self.particles=[]; self.floats=[]
        self.boss_mode=False; self.boss=None
        self.enemies=EnemyGrid(level); self.ufo=UFO()

    def _parts(self,x,y,color,n=18):
        for _ in range(n):
            if len(self.particles)<MAX_PARTICLES:
                self.particles.append(Particle(x,y,color,star=random.random()<0.4))

    def _float(self,text,x,y,color):
        self.floats.append(FloatText(text,x,y,color,self.fonts['sm']))

    def _save_score(self):
        if self.score>0:
            self.hi_scores.append(self.score)
            self.hi_scores.sort(reverse=True)
            self.hi_scores=self.hi_scores[:5]

    # ── main loop ────────────────────────────────────────────────
    def run(self):
        while True:
            dt=self.clock.tick(FPS)
            # FPS display update
            self._fps_timer+=dt
            if self._fps_timer>=500:
                self._fps_display=int(1000/(dt if dt>0 else 1))
                self._fps_timer=0

            self._events()
            if   self.state==S_MENU:  self._upd_menu()
            elif self.state==S_PLAY:  self._upd_play()
            elif self.state==S_NEXT:  self._upd_next()
            elif self.state in(S_OVER,S_WIN): self._upd_end()

            self.shake.update(); self.flash.update()
            self._render()

    # ── events ───────────────────────────────────────────────────
    def _events(self):
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type!=pygame.KEYDOWN: continue
            k=ev.key
            if k==pygame.K_ESCAPE:
                if self.state in(S_PLAY,S_PAUSE): self._save_score(); self.state=S_MENU
                else: pygame.quit(); sys.exit()
            elif k==pygame.K_p:
                if   self.state==S_PLAY:  self.state=S_PAUSE
                elif self.state==S_PAUSE: self.state=S_PLAY
            elif k==pygame.K_m: self.sfx.muted=not self.sfx.muted
            elif self.state==S_MENU:
                if k==pygame.K_RETURN:    self._start()
                elif k==pygame.K_h:       self.state=S_HI
                elif k==pygame.K_q:       pygame.quit(); sys.exit()
            elif self.state==S_HI:
                if k in(pygame.K_ESCAPE,pygame.K_RETURN): self.state=S_MENU
            elif self.state==S_PLAY and k==pygame.K_SPACE:
                self.player.shoot(self.sfx)
            elif self.state in(S_OVER,S_WIN) and k in(pygame.K_RETURN,pygame.K_SPACE):
                self._save_score(); self.state=S_MENU

    # ── update: play ─────────────────────────────────────────────
    def _upd_play(self):
        keys=pygame.key.get_pressed()
        self.player.update(keys,self.sfx)
        if self.boss_mode:
            self._upd_boss_play(); return
        self.enemies.update(self.sfx)
        self.ufo.update(self.sfx)

        pb=self.player.bullets

        # player bullets ↔ enemies
        for b in pb[:]:
            if not b.alive: continue
            for e in self.enemies.alive:
                if b.rect.colliderect(e.rect):
                    b.alive=False; self.score+=e.points
                    self.particles+=self.enemies.kill(e)
                    self.shake.shake(0.15)
                    self._float(f"+{e.points}",e.cx,e.cy,e.color)
                    self.sfx.play_expl('sm' if e.row>=3 else 'md')
                    break

        # FLAME BEAM ↔ enemies  (column-based, instant kill)
        if self.player.flame_beam:
            br=self.player.flame_beam_rect()
            for e in self.enemies.alive:
                if br.colliderect(e.rect):
                    self.score+=e.points
                    self.particles+=self.enemies.kill(e)
                    self._parts(e.cx,e.cy,RED,12)
                    self._float(f"+{e.points}",e.cx,e.cy,ORANGE)
                    self.shake.shake(0.08)

        # player bullets ↔ UFO
        for b in pb[:]:
            if b.alive and b.rect.colliderect(self.ufo.rect):
                pts=self.ufo.hit(); b.alive=False; self.score+=pts
                ux=int(self.ufo.x+self.ufo.W//2)
                self._parts(ux,42,RED,28); self.shake.shake(0.5)
                self.flash.flash(RED,80); sfx=self.sfx
                sfx.play('ufo_hit'); self._float(f"+{pts} UFO!",ux,42,RED)

        # enemy bullets ↔ player
        for b in self.enemies.bullets[:]:
            if not b.alive: continue
            if b.rect.colliderect(self.player.rect) and self.player.invincible==0:
                b.alive=False; self.lives-=1
                self._parts(self.player.rect.centerx,
                            self.player.rect.centery,CYAN,30)
                self.shake.shake(0.65); self.flash.flash(WHITE,110)
                self.sfx.play('lose_life')
                if self.lives<=0:
                    self.sfx.play('gameover'); self._save_score()
                    self.state=S_OVER; return
                self.player.hit()

        # powerups ↔ player
        for pw in self.enemies.powerups[:]:
            if pw.alive and pw.rect.colliderect(self.player.rect):
                self.player.collect(pw.kind,self.sfx); pw.alive=False
                names={WEAPON_MG:'MACHINEGUN!',WEAPON_MULTI:'MULTI-SHOT!',
                       WEAPON_FLAME:'FLAMETHROWER!'}
                cols={WEAPON_MG:PU_MG,WEAPON_MULTI:PU_MULTI,WEAPON_FLAME:PU_FL}
                self._float(names[pw.kind],
                            self.player.rect.centerx,self.player.y-26,
                            cols[pw.kind])
                self.flash.flash(cols[pw.kind],55)

        if self.enemies.lowest_y()>=SH-80:
            self.sfx.play('gameover'); self._save_score(); self.state=S_OVER; return

        if self.enemies.all_dead():
            self.sfx.play('level_up'); self.flash.flash(GREEN,160)
            self.shake.shake(0.5); self._parts(SW//2,SH//2,YELLOW,60)
            if self.level>=5: self._save_score(); self.state=S_WIN
            else:
                self._st_timer=130; self.level+=1; self.state=S_NEXT
            return

        # ── HARDCORE ambient rumble ──────────────────────────────
        # Base tremor sempre presente durante a partida
        alive_n = len(self.enemies.alive)
        total_n = ENEMY_ROWS * ENEMY_COLS
        # Escala com proximidade dos inimigos ao jogador
        low_y   = self.enemies.lowest_y()
        prox    = max(0.0, (low_y - GRID_Y) / max(1, SH - GRID_Y - 80))
        rumble  = 0.004 + prox * 0.022           # base + proximity boost
        # Armas ativas intensificam tremor
        if self.player.weapon == WEAPON_MG:    rumble += 0.008
        if self.player.flame_beam:             rumble += 0.028
        if self.player.weapon == WEAPON_MULTI: rumble += 0.005
        # Menos inimigos = mais rápido = mais agitado
        speed_factor = 1.0 - alive_n / max(1, total_n)
        rumble += speed_factor * 0.016
        self.shake.shake(rumble)
        # ─────────────────────────────────────────────────────────

        for p in self.particles: p.update()
        for f in self.floats:    f.update()
        self.particles=[p for p in self.particles if p.alive]
        self.floats   =[f for f in self.floats    if f.alive]
        if self.score>self.hi_scores[0]: self.hi_scores[0]=self.score

    # ── boss play update ──────────────────────────────────────────
    def _upd_boss_play(self):
        self.boss.update(self.sfx, None)

        pb = self.player.bullets

        # ── player bullets / flame ↔ boss weapons (único modo de dano)
        for b in pb[:]:
            if not b.alive: continue
            hit_w = None
            for w in (self.boss.weapon_l, self.boss.weapon_r):
                if b.rect.colliderect(w.rect):
                    hit_w = w; break
            if hit_w is None: continue
            b.alive = False
            dead = hit_w.hit()
            pts = 100
            self.sfx.play('boss_hit'); self.shake.shake(0.25)
            self.score += pts
            self._float(f"+{pts}", int(hit_w.cx), int(hit_w.y), CYAN)
            if dead:
                self._boss_die(); return

        # flame beam ↔ weapons (throttled)
        if self.player.flame_beam:
            br = self.player.flame_beam_rect()
            for w in (self.boss.weapon_l, self.boss.weapon_r):
                if br.colliderect(w.rect) and random.random() < 0.12:
                    if w.hit():
                        self._boss_die(); return
                    self.sfx.play('boss_hit')

        # ── boss bullets ↔ player
        for b in self.boss.bullets_down[:]:
            if not b.alive: continue
            if b.rect.colliderect(self.player.rect) and self.player.invincible==0:
                b.alive=False; self.lives-=1
                self._parts(self.player.rect.centerx,self.player.rect.centery,CYAN,30)
                self.shake.shake(0.65); self.flash.flash(WHITE,110)
                self.sfx.play('lose_life')
                if self.lives<=0:
                    self.sfx.play('gameover'); self._save_score(); self.state=S_OVER; return
                self.player.hit()

        # ── bomb explosions ↔ player (area damage, one hit per explosion)
        for ex in self.boss.explosions:
            if (not ex._damaged and self.player.invincible==0
                    and ex.damage_rect.colliderect(self.player.rect)):
                ex._damaged=True; self.lives-=1
                self._parts(self.player.rect.centerx,self.player.rect.centery,CYAN,30)
                self.shake.shake(0.7); self.flash.flash(WHITE,120)
                self.sfx.play_expl('lg'); self.sfx.play('lose_life')
                if self.lives<=0:
                    self.sfx.play('gameover'); self._save_score(); self.state=S_OVER; return
                self.player.hit()

        # ── boss flame beam ↔ player (área de dano, throttled)
        if self.boss._flame_timer > 0:
            for w in (self.boss.weapon_l, self.boss.weapon_r):
                fr = pygame.Rect(w.cx - FLAME_BEAM_W//2, int(w.y) + w.H,
                                 FLAME_BEAM_W, SH - int(w.y) - w.H)
                if (fr.colliderect(self.player.rect)
                        and self.player.invincible == 0
                        and random.random() < 0.06):
                    self.lives -= 1
                    self._parts(self.player.rect.centerx, self.player.rect.centery, ORANGE, 20)
                    self.shake.shake(0.4); self.flash.flash(ORANGE, 80)
                    self.sfx.play('lose_life')
                    if self.lives <= 0:
                        self.sfx.play('gameover'); self._save_score()
                        self.state = S_OVER; return
                    self.player.hit()
                    break

        # ambient boss rumble
        self.shake.shake(0.008)

        for p in self.particles: p.update()
        for f in self.floats:    f.update()
        self.particles=[p for p in self.particles if p.alive]
        self.floats   =[f for f in self.floats    if f.alive]
        if self.score>self.hi_scores[0]: self.hi_scores[0]=self.score

    def _boss_die(self):
        for _ in range(3):
            ox=random.randint(-160,160); oy=random.randint(-30,30)
            self._parts(self.boss.cx+ox, self.boss.cy+oy, RED,    40)
            self._parts(self.boss.cx+ox, self.boss.cy+oy, ORANGE, 30)
            self._parts(self.boss.cx+ox, self.boss.cy+oy, YELLOW, 20)
        self.shake.shake(1.0); self.flash.flash(WHITE, 200)
        self.sfx.play('boss_expl')
        self.score += BOSS_SCORE
        self._float(f"+{BOSS_SCORE} BOSS DESTROYED!", self.boss.cx, self.boss.cy-40, YELLOW)
        self.boss.alive=False
        self._save_score(); self.state=S_WIN

    def _upd_next(self):
        self._st_timer-=1
        for p in self.particles: p.update()
        self.particles=[p for p in self.particles if p.alive]
        if self._st_timer<=0:
            if self.level==5:
                self.boss_mode=True
                self.boss=Boss()
                self.enemies=EnemyGrid(1); self.enemies._grid=[]   # empty — no enemies
                self.ufo=UFO(); self.ufo._timer=9999999            # UFO never spawns
            else:
                self.boss_mode=False; self.boss=None
                self.enemies=EnemyGrid(self.level); self.ufo=UFO()
            self.player.reset_pos(); self.player.weapon=WEAPON_NORMAL
            self.particles=[]; self.floats=[]; self.state=S_PLAY

    def _upd_end(self):
        for p in self.particles: p.update()
        self.particles=[p for p in self.particles if p.alive]

    def _upd_menu(self): self._menu_frm+=1

    # ── render ───────────────────────────────────────────────────
    def _render(self):
        gs=self._gs; gs.fill((4,4,14))
        self.stars.draw(gs)

        if   self.state==S_MENU:  self._draw_menu(gs)
        elif self.state==S_HI:    self._draw_hiscores(gs)
        elif self.state==S_PLAY:  self._draw_gameplay(gs)
        elif self.state==S_PAUSE:
            self._draw_gameplay(gs)
            self._overlay(gs,"— PAUSED —",YELLOW,"Press P to continue")
        elif self.state==S_NEXT:
            self._draw_gameplay(gs)
            if self.level==5:
                lbl=self.fonts['lg'].render(f"WAVE {self.level-1} CLEAR!",True,GREEN)
                gs.blit(lbl,(SW//2-lbl.get_width()//2,SH//2-45))
                w2=self.fonts['lg'].render("⚠  BOSS  INCOMING  ⚠",True,RED)
                gs.blit(w2,(SW//2-w2.get_width()//2,SH//2-5))
                sub=self.fonts['sm'].render("Destroy the OMEGA DREADNOUGHT's weapons!",True,ORANGE)
                gs.blit(sub,(SW//2-sub.get_width()//2,SH//2+34))
            else:
                lbl=self.fonts['lg'].render(f"WAVE {self.level-1} CLEAR!",True,GREEN)
                gs.blit(lbl,(SW//2-lbl.get_width()//2,SH//2-20))
                sub=self.fonts['sm'].render(f"Prepare for Wave {self.level}…",True,WHITE)
                gs.blit(sub,(SW//2-sub.get_width()//2,SH//2+24))
        elif self.state==S_OVER:
            self._draw_gameplay(gs); self._overlay(gs,"GAME OVER",RED,"ENTER — menu")
        elif self.state==S_WIN:
            self._draw_gameplay(gs); self._overlay(gs,"YOU WIN!!",YELLOW,"ENTER — menu")

        self.flash.draw(gs)
        gs.blit(self.crt,(0,0))
        self.screen.fill(BLACK)
        ox,oy=self.shake.offset()
        self.screen.blit(gs,(ox,oy))
        pygame.display.flip()

    def _draw_gameplay(self,surf):
        # ── HUD (matches reference: SCORE | WAVE | ♥♥♥ | FPS | [POWERUP Xs])
        pygame.draw.rect(surf,(0,0,0),(0,0,SW,28))
        pygame.draw.line(surf,MGRAY,(0,28),(SW,28),1)
        f=self.fonts['hud']
        # hearts for lives
        hearts='♥'*self.lives+'♡'*(LIVES_START-self.lives)
        # powerup indicator
        pu_txt=""
        if self.player.weapon!=WEAPON_NORMAL:
            secs=math.ceil(self.player.wtimer/60)
            name={'mg':'MACHINEGUN','multi':'MULTI','flame':'FLAME'}[self.player.weapon]
            pu_txt=f"  [{name} {secs}s]"
            pu_col={'mg':PU_MG,'multi':PU_MULTI,'flame':PU_FL}[self.player.weapon]
        wave_lbl = "BOSS" if self.boss_mode else f"{self.level:02d}"
        hud=f"SCORE: {self.score:05d}  |  WAVE: {wave_lbl}  |  {hearts}  |  FPS: {self._fps_display}"
        lbl=f.render(hud,True,WHITE)
        surf.blit(lbl,(10,7))
        if pu_txt:
            pl=f.render(pu_txt,True,pu_col)
            surf.blit(pl,(lbl.get_width()+10,7))

        # ground line (hidden in boss mode — bars use that space)
        if not self.boss_mode:
            pygame.draw.line(surf,DKGRAY,(0,SH-22),(SW,SH-22),1)

        if self.boss_mode and self.boss:
            self.boss.draw(surf)
            self.boss.draw_bars(surf, f)
        else:
            self.enemies.draw(surf)
            self.ufo.draw(surf)
        self.player.draw(surf)
        for p in self.particles: p.draw(surf)
        for f in self.floats:    f.draw(surf)

    def _draw_menu(self,surf):
        t = self._menu_frm
        frm = (t // 28) % 2

        # ── Scanline sweep glitch band
        band_y = int((t * 2.8) % (SH + 40)) - 20
        pygame.draw.rect(surf, (0, 255, 100, 18),
                         (0, band_y, SW, 6)) if False else None   # SRCALPHA needed
        gs_band = pygame.Surface((SW, 6), pygame.SRCALPHA)
        gs_band.fill((0, 220, 80, 22))
        surf.blit(gs_band, (0, band_y % SH))

        # ── TITLE  "SPACE" (cyan) + "INVADERS" (yellow) — pixel retro style
        pf = self.fonts['pixel']

        # "SPACE" — scale 9× → ~126 px blocky letters
        t1_scale = 9
        t1_surf  = pf.render("SPACE", False, CYAN)
        t1w      = t1_surf.get_width() * t1_scale
        t1h      = t1_surf.get_height() * t1_scale
        t1y      = 18
        draw_pixel_glitch_title(surf, "SPACE",
                                SW//2 - t1w//2, t1y, CYAN, pf, t1_scale, t, intensity=1.2)

        # "INVADERS" — scale 8× → ~112 px blocky letters, colado abaixo do "SPACE"
        t2_scale = 8
        t2w      = pf.render("INVADERS", False, YELLOW).get_width() * t2_scale
        iy       = t1y + t1h + 4 + int(3 * math.sin(t * 0.04))
        draw_pixel_glitch_title(surf, "INVADERS",
                                SW//2 - t2w//2, iy, YELLOW, pf, t2_scale, t + 30, intensity=1.0)

        # ── Subtitle
        sub = self.fonts['xs'].render(
            "MACHINEGUN  ·  MULTI-SHOT  ·  FLAMETHROWER  EDITION", True, MGRAY)
        surf.blit(sub, (SW//2 - sub.get_width()//2, 218))

        # ── Enemy parade (3 types scrolling left→right across screen)
        parade_y = 260
        parade_speed = 1.2
        for pi, (key_b, col, pts) in enumerate([
                ("yel", YELLOW, "30"), ("grn", GREEN, "20"), ("mag", MAGENTA, "10")]):
            es = _surf(f"{key_b}{frm}", col, SC)
            ew = es.get_width()
            # 6 enemies per row, scrolling
            for ei in range(7):
                ex = int((ei * 110 + t * parade_speed * (1 + pi*0.15)) % (SW + 110)) - 60
                surf.blit(es, (ex, parade_y + pi * 48))
            # score label at right
            slbl = self.fonts['xs'].render(f"= {pts} PTS", True, col)
            surf.blit(slbl, (SW - slbl.get_width() - 12,
                             parade_y + pi * 48 + es.get_height()//2 - 5))

        # ── Menu items (left-aligned block, centered)
        mf  = self.fonts['md']
        items = [
            ("[ENTER]", "Start Game",  WHITE,  CYAN),
            ("[H]",     "High Scores", WHITE,  YELLOW),
            ("[Q]",     "Quit",        WHITE,  RED),
        ]
        my = 416
        for key_lbl, desc, kc, dc in items:
            k = mf.render(key_lbl, True, kc)
            d = mf.render(f"  {desc}", True, dc)
            bx = SW//2 - (k.get_width() + d.get_width())//2
            surf.blit(k, (bx, my))
            surf.blit(d, (bx + k.get_width(), my))
            my += 34

        # ── Blinking "PRESS ENTER" at bottom
        if (t // 18) % 2 == 0:
            pe = self.fonts['md'].render("— PRESS  ENTER  TO  START —", True, YELLOW)
            surf.blit(pe, (SW//2 - pe.get_width()//2, my + 14))

        # ── HI-SCORE top right
        hi = self.fonts['sm'].render(
            f"HI  {max(self.hi_scores):07d}", True, YELLOW)
        surf.blit(hi, (SW - hi.get_width() - 14, 10))

        # ── Controls hint
        ctrl = self.fonts['xs'].render(
            "← →  Move   SPACE  Shoot   P  Pause   M  Mute", True, DKGRAY)
        surf.blit(ctrl, (SW//2 - ctrl.get_width()//2, SH - 14))

    def _draw_hiscores(self,surf):
        f=self.fonts['lg']
        lbl=f.render("HIGH SCORES",True,YELLOW)
        surf.blit(lbl,(SW//2-lbl.get_width()//2,120))
        fm=self.fonts['md']
        for i,sc in enumerate(sorted(self.hi_scores,reverse=True)):
            c=CYAN if i==0 else WHITE
            row=fm.render(f"{i+1}.  {sc:07d}",True,c)
            surf.blit(row,(SW//2-row.get_width()//2,200+i*44))
        back=self.fonts['sm'].render("ENTER — back",True,GRAY)
        surf.blit(back,(SW//2-back.get_width()//2,SH-30))

    def _overlay(self,surf,title,color,sub=""):
        panel=pygame.Surface((520,150),pygame.SRCALPHA)
        panel.fill((0,0,0,210)); surf.blit(panel,(SW//2-260,SH//2-75))
        lbl=self.fonts['lg'].render(title,True,color)
        surf.blit(lbl,(SW//2-lbl.get_width()//2,SH//2-58))
        if self.state in(S_OVER,S_WIN):
            sc=self.fonts['md'].render(f"SCORE  {self.score:05d}",True,WHITE)
            surf.blit(sc,(SW//2-sc.get_width()//2,SH//2-14))
        if sub:
            s=self.fonts['sm'].render(sub,True,GRAY)
            surf.blit(s,(SW//2-s.get_width()//2,SH//2+30))


# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    Game().run()
