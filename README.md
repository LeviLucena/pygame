![Python](https://img.shields.io/badge/Python-3.x-3776ab?style=flat-square&logo=python&logoColor=white) ![ScreenShake](https://img.shields.io/badge/ScreenShake-trauma--offset-111827?style=flat-square&logo=nothing&logoColor=white) ![FlashFX](https://img.shields.io/badge/FlashFX-color__flash-0ea5e9?style=flat-square&logo=flash&logoColor=white) ![CRT Overlay](https://img.shields.io/badge/CRT_Overlay-scanlines-37474f?style=flat-square&logo=monitor&logoColor=white) ![MarchSound](https://img.shields.io/badge/MarchSound-sound-1e88e5?style=flat-square&logo=music&logoColor=white) ![Stars](https://img.shields.io/badge/Stars-starfield-ffd66b?style=flat-square&logo=asterisk&logoColor=black) ![Particle](https://img.shields.io/badge/Particle-ASCII_sparks-6b7280?style=flat-square&logo=text&logoColor=white) ![Exhaust](https://img.shields.io/badge/Exhaust-exhaust-374151?style=flat-square&logo=fire&logoColor=white) ![FlamePart](https://img.shields.io/badge/FlamePart-flamethrower-ef4444?style=flat-square&logo=burning__eye&logoColor=white) ![Bullet](https://img.shields.io/badge/Bullet-projectile-3740a3?style=flat-square&logo=bullet&logoColor=white) ![MuzzleFlash](https://img.shields.io/badge/MuzzleFlash-flash-ffd000?style=flat-square&logo=zap&logoColor=000) ![Powerup](https://img.shields.io/badge/Powerup-drop__animation-16a34a?style=flat-square&logo=gift&logoColor=white) ![Player](https://img.shields.io/badge/Player-ship__modes-2563eb?style=flat-square&logo=space-invaders&logoColor=white) ![Enemy](https://img.shields.io/badge/Enemy-2frame__hitFlash-9b59b6?style=flat-square&logo=bug&logoColor=white) ![EnemyGrid](https://img.shields.io/badge/EnemyGrid-11x5-2e7d32?style=flat-square&logo=grid&logoColor=white) ![UFO](https://img.shields.io/badge/UFO-bonus__trail-ef4444?style=flat-square&logo=ufo&logoColor=white) ![FloatText](https://img.shields.io/badge/FloatText-score__float-0ea5e9?style=flat-square&logo=number-1&logoColor=white) ![BossWeapon](https://img.shields.io/badge/BossWeapon-turret__hitbox-9c27b0?style=flat-square&logo=shield&logoColor=white) ![BossBomb](https://img.shields.io/badge/BossBomb-gravity__trail-8e24aa?style=flat-square&logo=cloud-fog&logoColor=white) ![BossExplosion](https://img.shields.io/badge/BossExplosion-area-ef5350?style=flat-square&logo=boom&logoColor=white) ![Boss](https://img.shields.io/badge/Boss-OMEGA_DREADNOUGHT-263238?style=flat-square&logo=dragon&logoColor=white) ![HUD](https://img.shields.io/badge/HUD-monospaced__bar-455a64?style=flat-square&logo=code&logoColor=white)
# 👾 Space Invaders — Arcade Edition

> **MACHINEGUN · MULTI-SHOT · FLAMETHROWER · BOSS · CRT · HARDCORE SHAKE**

Um Space Invaders clássico completamente reimaginado com Python + pygame-ce, com 5 waves de dificuldade crescente e um boss épico no wave final.

https://github.com/user-attachments/assets/311e4f14-f0bb-4218-9288-5a72cd482761

---

## 🎮 Como Jogar

```bash
# Opção 1 — bat (Windows)
run.bat

# Opção 2 — direto
python main.py
```

### Controles

| Tecla | Ação |
|-------|------|
| `← →` / `A D` | Mover nave |
| `SPACE` | Atirar / Segurar para MachineGun ou Flame |
| `P` | Pausar |
| `M` | Mudo / Som |
| `H` | High Scores (no menu) |
| `ESC` | Voltar ao menu / Sair |

---

## ⚡ Powerups

Os inimigos dropam powerups ao morrer (20% de chance). Cada um dura **3 segundos** — o timer aparece no HUD.

| Ícone | Powerup | Efeito |
|-------|---------|--------|
| 🔵 **3X** | MULTI-SHOT | 3 balas em leque simultâneo |
| 🟡 **MG** | MACHINEGUN | Segurar SPACE = rajada automática contínua |
| 🔴 **FIRE** | FLAMETHROWER | Segurar SPACE = coluna vertical de fogo que queima tudo na linha |

---

## 👾 Inimigos

| Sprite | Tipo | Pontos |
|--------|------|--------|
| Arco amarelo `⌐¬` | Topo (2 fileiras) | 30 pts |
| Coroa verde `M` | Meio (1 fileira) | 20 pts |
| Forquilha magenta `Y` | Base (2 fileiras) | 10 pts |
| 🛸 UFO vermelho | Aparece aleatoriamente | 50–300 pts |

A formação de **55 inimigos** (11×5) acelera conforme são abatidos. A cada wave a dificuldade aumenta — velocidade, cadência de tiro e chance de powerup.

---

## 💀 BOSS — OMEGA DREADNOUGHT (Wave 5)

Ao completar a Wave 4, o **OMEGA DREADNOUGHT** aparece: um UFO vermelho gigante varrendo a tela de lado a lado.

### Como derrotá-lo

O único jeito de causar dano é acertando as **duas armas** (turrets verdes) penduradas abaixo do corpo. Cada hit remove 1 HP da barra.

### Ataques do boss

A cada ciclo de tiro, o boss escolhe aleatoriamente um dos 4 modos de ataque — os mesmos que o jogador pode usar:

| Modo | Visual | Descrição |
|------|--------|-----------|
| **NORMAL** | Balas vermelhas | 2 balas retas, uma de cada arma |
| **MULTI (3X)** | Balas cyan em leque | 6 balas (-18°, 0°, +18°) de cada arma simultaneamente |
| **MG** | Balas amarelas rápidas | Burst de 10 tiros rápidos disparados em sequência |
| **FLAME** | Coluna de fogo laranja | Chama apontando para baixo por 1.5s — dano de área contínuo |

Além dos tiros, o boss lança **bombas** que explodem no espaço causando dano de área.

**Recompensa:** 5000 pts ao destruir o boss.

---

## 🎨 Efeitos Visuais

- **CRT Overlay** — scanlines + vignette escura nas bordas, pré-computado
- **Screen Shake HARDCORE** — tremor contínuo proporcional à proximidade dos inimigos, potencializado por armas ativas e hits
- **Chromatic Aberration** — título com canais RGB deslocados, efeito de monitor descalibrado
- **Glitch animado** — fatias do título pulam de posição aleatoriamente
- **Scanline sweep** — banda verde varrendo a tela na tela inicial
- **Engine Exhaust** — chama cyan saindo da traseira da nave constantemente
- **Muzzle Flash** — clarão na boca do canhão a cada disparo
- **Bullet Trails** — rastro com fade atrás de cada projétil
- **Explosões ASCII** — faíscas `*` e `·` estilo terminal coloridas
- **Parade de inimigos** — 3 fileiras scrollando na tela inicial
- **UFO trail** — rastro vermelho seguindo o UFO
- **Boss flame beam** — coluna de fogo laranja apontando para o jogador
- **Boss explosões** — anel de ondas de choque ao destruir o boss

---

## 🔊 Sons (100% sintéticos)

Todos os sons são gerados em Python puro via síntese de onda — **nenhum arquivo de áudio externo**.

| Som | Técnica |
|-----|---------|
| Marcha dos inimigos | 4 notas (160→80 Hz) alternando em sincronia com o movimento |
| Disparo normal | Square wave com sweep de frequência |
| Machinegun | 3 variações aleatórias para evitar repetição |
| Flamethrower | Noise wave com alta mistura de ruído |
| Explosões | 3 tamanhos (sm/md/lg) com frequências diferentes |
| Perder vida | Tri wave descendente |
| UFO | Square wave pulsante |
| Boss hit | Noise burst curto |
| Boss intro | Tri wave grave de entrada |
| Boss explosão | Noise grave profundo |

---

## 🏆 Sistema de Score

```
SCORE: 00000  |  WAVE: 01  |  ♥♥♥  |  FPS: XXXX  |  [MACHINEGUN 3s]
```

- **Top 5 High Scores** persistentes na sessão (tela `[H]` no menu)
- **5 waves** de dificuldade crescente — Wave 5 = boss fight
- Wave `BOSS` aparece no HUD durante o confronto

---

## 🛠️ Instalação

### Requisitos

- Python 3.13+ (Anaconda recomendado)
- pygame-ce 2.5+

### Setup

```bash
# Com pip funcional
pip install pygame-ce

# Com conda (sem pip) — baixar wheel e extrair manualmente
python -m pip download pygame-ce --python-version 3.13 --only-binary :all: --platform win_amd64 -d ./wheels
python -c "import zipfile; zipfile.ZipFile('./wheels/pygame_ce-*.whl').extractall('site-packages/')"
```

---

## 📁 Estrutura

```
pygame/
├── main.py      # Jogo completo (~1800 linhas, single-file)
└── run.bat      # Launcher Windows
```

### Arquitetura interna (`main.py`)

```
ScreenShake      — sistema trauma-based com perlin-like offset
FlashFX          — flash de tela colorido em eventos
CRT Overlay      — scanlines + vignette pré-computados
MarchSound       — 4 notas sincronizadas com movimento dos inimigos
Stars            — starfield multi-layer
Particle         — sparks ASCII com star-mode
Exhaust          — partículas de exaustão da nave
FlamePart        — partículas densas do flamethrower (player e boss)
Bullet           — projétil com trail de 5 posições
MuzzleFlash      — clarão de 4 frames
Powerup          — drop animado com bob + glow pulsante
Player           — nave com 3 modos de arma
Enemy            — sprite 2-frame com hit flash
EnemyGrid        — formação 11×5, movimento clássico
UFO              — nave bônus com trail vermelho
FloatText        — pontuação flutuante sobre kills
BossWeapon       — turret hitbox (único ponto vulnerável do boss)
BossBomb         — bomba de gravidade com trail roxo
BossExplosion    — explosão de área com dano ao jogador
Boss             — OMEGA DREADNOUGHT, 4 modos de ataque aleatórios
HUD              — barra superior monospace estilo referência
Game             — state machine: MENU→PLAY→NEXT→OVER/WIN/BOSS
```

---

## 📜 Licença

MIT — faça o que quiser.
