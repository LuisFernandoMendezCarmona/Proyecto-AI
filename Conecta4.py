"""
Conecta 4 - Juego con Agente Inteligente (IA) y Gráficos Vectoriales HD
Desarrollado para el proyecto de Inteligencia Artificial.

Técnica de IA: Algoritmo Minimax con Poda Alfa-Beta y Función de Evaluación Heurística Posicional.
Dificultades:
  - Fácil: Jugadas semi-aleatorias con detección básica de victorias directas.
  - Medio: Minimax a profundidad 2 con bloqueo defensivo de amenazas inmediatas.
  - Difícil: Minimax con Poda Alfa-Beta a profundidad 5 con ordenamiento táctico de columnas.
"""

import sys
import math
import random
import time
import os
import subprocess
# pyrefly: ignore [missing-import]
import pygame

# -----------------------------------------------------------------------------
# CONFIGURACIÓN Y CONSTANTES
# -----------------------------------------------------------------------------
ROWS = 6
COLS = 7

# Piezas del tablero
EMPTY = 0
HUMAN_PIECE = 1  # Rojo
AI_PIECE = 2     # Amarillo

# Dimensiones visuales
SQUARE_SIZE = 100
RADIUS = int(SQUARE_SIZE / 2 - 8)

WIDTH = COLS * SQUARE_SIZE
HEIGHT = (ROWS + 2) * SQUARE_SIZE  # 800px

BOARD_OFFSET_Y = 2 * SQUARE_SIZE

# Colores (Paleta Cyberpunk/Slate HD con neones y acabados metálicos)
COLOR_BG = (11, 17, 32)            # Dark Navy Slate #0B1120
COLOR_HEADER = (17, 24, 39)        # Slate #111827
COLOR_BOARD_OUTER = (15, 34, 75)   # Marco exterior azul metálico
COLOR_BOARD = (23, 49, 110)        # Cuerpo principal del tablero
COLOR_BOARD_INNER = (37, 99, 235)  # Brillo azul neón #2563EB
COLOR_SLOT = (11, 17, 32)          # Fondo de ranura vacía
COLOR_SLOT_SHADOW = (5, 8, 18)     # Sombra interna de ranura

# Pieza Humano (Rojo Carmesí Neón 3D)
COLOR_HUMAN = (239, 68, 68)        # Red-500
COLOR_HUMAN_DARK = (153, 27, 27)   # Red-900 Sombra 3D
COLOR_HUMAN_GLOW = (254, 202, 202) # Brillo superior de cristal

# Pieza IA (Oro Ámbar Neón 3D)
COLOR_AI = (245, 158, 11)          # Amber-500
COLOR_AI_DARK = (146, 64, 14)      # Amber-900 Sombra 3D
COLOR_AI_GLOW = (254, 240, 138)    # Brillo superior de cristal

COLOR_WHITE = (248, 250, 252)      # Texto puro
COLOR_GRAY = (148, 163, 184)       # Texto secundario
COLOR_DARK_GRAY = (47, 63, 86)     # Fondos de botones secundarios
COLOR_GOLD = (250, 204, 21)        # Oro resplandeciente para victorias
COLOR_CYAN = (56, 189, 248)        # Cyan neón interactivo

# Botones de dificultad
BTN_FACIL_COLOR = (34, 197, 94)    # Verde
BTN_MEDIO_COLOR = (234, 179, 8)    # Amarillo
BTN_DIFICIL_COLOR = (239, 68, 68)  # Rojo

# Dificultades
EASY = "FACIL"
MEDIUM = "MEDIO"
HARD = "DIFICIL"

# Estados de la aplicación
STATE_START_MENU = 0
STATE_DIFFICULTY_MENU = 1
STATE_GAMEPLAY = 2
STATE_INSTRUCTIONS = 3

# Nombre del archivo de audio de fondo
AUDIO_FILENAME = "El Chavo Animado OST - Tema Churros.mp3"


# -----------------------------------------------------------------------------
# DIBUJO DE ICONOS VECTORIALES
# -----------------------------------------------------------------------------
def draw_vector_icon(surface, icon_type, x, y, size=14, color=COLOR_WHITE):
    """Dibuja iconos geométricos nativos en Pygame para evitar caracteres faltantes[cite: 1]."""
    if icon_type == "play":
        points = [(x - size // 2, y - size // 2), (x + size // 2, y), (x - size // 2, y + size // 2)]
        pygame.draw.polygon(surface, color, points)
    elif icon_type == "back":
        points = [(x + size // 2, y - size // 2), (x - size // 2, y), (x + size // 2, y + size // 2)]
        pygame.draw.polygon(surface, color, points)
    elif icon_type == "info":
        pygame.draw.circle(surface, color, (x, y), size // 2 + 1, width=2)
        pygame.draw.circle(surface, color, (x, y - 3), 1)
        pygame.draw.line(surface, color, (x, y - 1), (x, y + 4), 2)
    elif icon_type == "home":
        roof = [(x, y - size // 2 - 1), (x - size // 2 - 2, y - 1), (x + size // 2 + 2, y - 1)]
        pygame.draw.polygon(surface, color, roof)
        pygame.draw.rect(surface, color, (x - size // 2 + 1, y - 1, size - 2, size // 2 + 2), border_radius=1)
    elif icon_type == "reset":
        pygame.draw.arc(surface, color, (x - size // 2, y - size // 2, size, size), 0.3, 5.8, 2)
        arrow_head = [(x + size // 2 - 1, y - 4), (x + size // 2 + 4, y + 1), (x + size // 2 - 4, y + 1)]
        pygame.draw.polygon(surface, color, arrow_head)
    elif icon_type == "arrow_down":
        points = [(x - size, y - size // 2), (x + size, y - size // 2), (x, y + size // 2)]
        pygame.draw.polygon(surface, color, points)
    elif icon_type == "target":
        pygame.draw.circle(surface, color, (x, y), size // 2, width=2)
        pygame.draw.circle(surface, color, (x, y), size // 4)
    elif icon_type == "gamepad":
        pygame.draw.rect(surface, color, (x - size // 2 - 2, y - size // 4, size + 4, size // 2 + 2), border_radius=3)
        pygame.draw.circle(surface, COLOR_BG, (x - 4, y), 2)
        pygame.draw.circle(surface, COLOR_BG, (x + 4, y), 2)
    elif icon_type == "cpu":
        pygame.draw.rect(surface, color, (x - size // 2, y - size // 2, size, size), width=2, border_radius=2)
        pygame.draw.rect(surface, color, (x - size // 4, y - size // 4, size // 2, size // 2))
    elif icon_type == "bulb":
        pygame.draw.circle(surface, color, (x, y - 2), size // 3 + 1)
        pygame.draw.rect(surface, color, (x - 2, y + 2, 4, 3))


# -----------------------------------------------------------------------------
# SISTEMA DE PARTÍCULAS VISUALES
# -----------------------------------------------------------------------------
class Particle:
    """Representa una partícula animada para efectos ambientales e interacción[cite: 1]."""

    def __init__(self, x, y, vx, vy, color, size, lifetime, p_type="spark"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.p_type = p_type
        self.rotation = random.uniform(0, 360)
        self.v_rot = random.uniform(-6, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.rotation += self.v_rot

        if self.p_type == 'spark':
            self.vy += 0.35
            self.size = max(0.5, self.size * 0.94)
        elif self.p_type == 'confetti':
            self.vy += 0.12
            self.vx *= 0.98
        elif self.p_type == 'bg' and self.y < -10:
            self.y = HEIGHT + 10
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))
        if alpha <= 0:
            return

        if self.p_type == 'bg':
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))
        elif self.p_type == 'spark':
            s = pygame.Surface((int(self.size * 2 + 4), int(self.size * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size + 2), int(self.size + 2)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))
        elif self.p_type == 'confetti':
            sz = max(2, int(self.size))
            s = pygame.Surface((sz, sz), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            rotated = pygame.transform.rotate(s, self.rotation)
            surface.blit(rotated, (int(self.x - rotated.get_width() / 2), int(self.y - rotated.get_height() / 2)))


# -----------------------------------------------------------------------------
# GESTOR DE MÚSICA DE FONDO
# -----------------------------------------------------------------------------
class MusicManager:
    """Maneja la reproducción en bucle de la canción de fondo[cite: 1]."""

    def __init__(self, filename):
        self.filename = filename
        self.is_muted = False
        self.ps_proc = None
        self.mode = None
        self.start_music()

    def start_music(self):
        if not os.path.exists(self.filename):
            print(f"[Música] El archivo '{self.filename}' no se encuentra en el directorio actual[cite: 1].")
            return

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(self.filename)
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
            self.mode = "pygame"
            return
        except Exception:
            pass

        if os.name == 'nt':
            try:
                abs_path = os.path.abspath(self.filename)
                ps_script = f"""
                Add-Type -AssemblyName PresentationCore
                $player = New-Object System.Windows.Media.MediaPlayer
                $player.Open('{abs_path}')
                $player.Volume = 0.35
                $player.MediaEnded += {{ $player.Position = [System.TimeSpan]::Zero; $player.Play() }}
                $player.Play()
                while ($true) {{ Start-Sleep -Seconds 1 }}
                """
                self.ps_proc = subprocess.Popen(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.mode = "powershell"
            except Exception as e:
                print("[Música] No se pudo iniciar el reproductor secundario:", e)

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.mode == "pygame":
            pygame.mixer.music.pause() if self.is_muted else pygame.mixer.music.unpause()
        elif self.mode == "powershell" and self.ps_proc:
            if self.is_muted:
                try: self.ps_proc.terminate()
                except Exception: pass
            else:
                self.start_music()

    def stop(self):
        if self.mode == "pygame":
            try: pygame.mixer.music.stop()
            except Exception: pass
        elif self.mode == "powershell" and self.ps_proc:
            try: self.ps_proc.terminate()
            except Exception: pass


# -----------------------------------------------------------------------------
# LÓGICA DEL MOTOR DE JUEGO (UNIFICADA)
# -----------------------------------------------------------------------------
class Connect4Engine:
    """Maneja la matriz del juego, movimientos y detección de victoria optimizada[cite: 1]."""

    def __init__(self):
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

    def reset(self):
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

    def is_valid_location(self, col):
        return self.board[ROWS - 1][col] == EMPTY

    def get_next_open_row(self, col):
        for r in range(ROWS):
            if self.board[r][col] == EMPTY:
                return r
        return None

    def drop_piece(self, row, col, piece):
        self.board[row][col] = piece

    def winning_move(self, piece, board=None):
        """Verifica si la pieza dada ha ganado en un tablero específico o el actual[cite: 1]."""
        b = board if board is not None else self.board
        
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                if b[r][c] == piece and b[r][c+1] == piece and b[r][c+2] == piece and b[r][c+3] == piece:
                    return True, [(r, c), (r, c+1), (r, c+2), (r, c+3)]

        # Vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                if b[r][c] == piece and b[r+1][c] == piece and b[r+2][c] == piece and b[r+3][c] == piece:
                    return True, [(r, c), (r+1, c), (r+2, c), (r+3, c)]

        # Diagonal Positiva (/)
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if b[r][c] == piece and b[r+1][c+1] == piece and b[r+2][c+2] == piece and b[r+3][c+3] == piece:
                    return True, [(r, c), (r+1, c+1), (r+2, c+2), (r+3, c+3)]

        # Diagonal Negativa (\)
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if b[r][c] == piece and b[r-1][c+1] == piece and b[r-2][c+2] == piece and b[r-3][c+3] == piece:
                    return True, [(r, c), (r-1, c+1), (r-2, c+2), (r-3, c+3)]

        return False, []

    def get_valid_locations(self):
        center_order = [3, 2, 4, 1, 5, 0, 6]
        return [col for col in center_order if self.is_valid_location(col)]

    def is_terminal_node(self):
        return self.winning_move(HUMAN_PIECE)[0] or self.winning_move(AI_PIECE)[0] or len(self.get_valid_locations()) == 0


# -----------------------------------------------------------------------------
# AGENTE INTELIGENTE (OPTIMIZADO CON BACKTRACKING)
# -----------------------------------------------------------------------------
class Connect4AI:
    """Agente de IA optimizado con Minimax, Poda Alfa-Beta y Backtracking[cite: 1]."""

    def __init__(self, engine):
        self.engine = engine

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = HUMAN_PIECE if piece == AI_PIECE else AI_PIECE

        piece_count = window.count(piece)
        empty_count = window.count(EMPTY)
        opp_count = window.count(opp_piece)

        if piece_count == 4:
            score += 10000
        elif piece_count == 3 and empty_count == 1:
            score += 100
        elif piece_count == 2 and empty_count == 2:
            score += 10

        if opp_count == 3 and empty_count == 1:
            score -= 120
        elif opp_count == 2 and empty_count == 2:
            score -= 8

        return score

    def score_position(self, board, piece):
        score = 0
        # Centro
        score += [board[r][3] for r in range(ROWS)].count(piece) * 6

        # Horizontales
        for r in range(ROWS):
            row_array = board[r]
            for c in range(COLS - 3):
                score += self.evaluate_window(row_array[c:c+4], piece)

        # Verticales
        for c in range(COLS):
            col_array = [board[r][c] for r in range(ROWS)]
            for r in range(ROWS - 3):
                score += self.evaluate_window(col_array[r:r+4], piece)

        # Diagonales Positivas
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                score += self.evaluate_window([board[r+i][c+i] for i in range(4)], piece)

        # Diagonales Negativas
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                score += self.evaluate_window([board[r-i][c+i] for i in range(4)], piece)

        return score

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        """Algoritmo Minimax optimizado mediante modificación in-place y backtracking[cite: 1]."""
        valid_locations = [col for col in [3, 2, 4, 1, 5, 0, 6] if board[ROWS - 1][col] == EMPTY]

        if self.engine.winning_move(AI_PIECE, board)[0]:
            return None, 1000000000
        if self.engine.winning_move(HUMAN_PIECE, board)[0]:
            return None, -1000000000
        if not valid_locations or depth == 0:
            return None, self.score_position(board, AI_PIECE)

        if maximizingPlayer:
            value = -math.inf
            best_col = random.choice(valid_locations)
            for col in valid_locations:
                row = next(r for r in range(ROWS) if board[r][col] == EMPTY)
                board[row][col] = AI_PIECE
                new_score = self.minimax(board, depth - 1, alpha, beta, False)[1]
                board[row][col] = EMPTY  # Backtracking (evita copiar tableros)

                if new_score > value:
                    value = new_score
                    best_col = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return best_col, value
        else:
            value = math.inf
            best_col = random.choice(valid_locations)
            for col in valid_locations:
                row = next(r for r in range(ROWS) if board[r][col] == EMPTY)
                board[row][col] = HUMAN_PIECE
                new_score = self.minimax(board, depth - 1, alpha, beta, True)[1]
                board[row][col] = EMPTY  # Backtracking

                if new_score < value:
                    value = new_score
                    best_col = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return best_col, value

    def get_best_move(self, difficulty):
        valid_cols = self.engine.get_valid_locations()
        if not valid_cols:
            return None

        if difficulty == EASY:
            if random.random() < 0.7:
                return random.choice(valid_cols)
            col, _ = self.minimax(self.engine.board, 1, -math.inf, math.inf, True)
            return col if col is not None else random.choice(valid_cols)

        elif difficulty == MEDIUM:
            for col in valid_cols:
                row = self.engine.get_next_open_row(col)
                self.engine.board[row][col] = AI_PIECE
                if self.engine.winning_move(AI_PIECE)[0]:
                    self.engine.board[row][col] = EMPTY
                    return col
                self.engine.board[row][col] = EMPTY

            for col in valid_cols:
                row = self.engine.get_next_open_row(col)
                self.engine.board[row][col] = HUMAN_PIECE
                if self.engine.winning_move(HUMAN_PIECE)[0]:
                    self.engine.board[row][col] = EMPTY
                    return col
                self.engine.board[row][col] = EMPTY

            col, _ = self.minimax(self.engine.board, 2, -math.inf, math.inf, True)
            return col if col is not None else random.choice(valid_cols)

        elif difficulty == HARD:
            col, _ = self.minimax(self.engine.board, 5, -math.inf, math.inf, True)
            return col if col is not None else random.choice(valid_cols)

        return random.choice(valid_cols)


# -----------------------------------------------------------------------------
# INTERFAZ GRÁFICA DE USUARIO (PYGAME GUI)
# -----------------------------------------------------------------------------
class Connect4GUI:
    """Maneja la ventana gráfica, renderizado 3D HD y animaciones[cite: 1]."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Conecta 4 - IA & Gráficos Ultra HD")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_super_title = pygame.font.SysFont("Segoe UI", 44, bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.font_main = pygame.font.SysFont("Segoe UI", 17, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.font_banner = pygame.font.SysFont("Segoe UI", 34, bold=True)

        self.engine = Connect4Engine()
        self.ai = Connect4AI(self.engine)
        self.music = MusicManager(AUDIO_FILENAME)

        self.particles = []
        self.init_bg_particles()

        self.app_state = STATE_START_MENU
        self.difficulty = MEDIUM
        self.turn = HUMAN_PIECE
        self.game_over = False
        self.winner_msg = ""
        self.winning_coords = []
        self.pulse_timer = 0

        self.score_human = 0
        self.score_ai = 0
        self.score_draws = 0

        # Rectángulos UI
        self.btn_facil_rect = pygame.Rect(15, 14, 72, 32)
        self.btn_medio_rect = pygame.Rect(93, 14, 72, 32)
        self.btn_dificil_rect = pygame.Rect(171, 14, 72, 32)
        self.btn_reset_rect = pygame.Rect(WIDTH - 245, 14, 90, 32)
        self.btn_menu_game_rect = pygame.Rect(WIDTH - 145, 14, 90, 32)
        self.btn_mute_rect = pygame.Rect(WIDTH - 45, 14, 32, 32)

        self.btn_play_start = pygame.Rect(WIDTH // 2 - 210, HEIGHT // 2 + 130, 200, 56)
        self.btn_instructions_start = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 130, 200, 56)

        card_w, card_h = 520, 78
        self.btn_diff_easy = pygame.Rect(WIDTH // 2 - card_w // 2, 220, card_w, card_h)
        self.btn_diff_medium = pygame.Rect(WIDTH // 2 - card_w // 2, 315, card_w, card_h)
        self.btn_diff_hard = pygame.Rect(WIDTH // 2 - card_w // 2, 410, card_w, card_h)
        self.btn_back_to_menu = pygame.Rect(WIDTH // 2 - 110, 520, 220, 46)

        self.btn_inst_play = pygame.Rect(WIDTH // 2 + 10, HEIGHT - 85, 220, 50)
        self.btn_inst_back = pygame.Rect(WIDTH // 2 - 230, HEIGHT - 85, 220, 50)

    def init_bg_particles(self):
        for _ in range(35):
            self.particles.append(Particle(
                x=random.randint(0, WIDTH), y=random.randint(0, HEIGHT),
                vx=random.uniform(-0.3, 0.3), vy=random.uniform(-0.6, -0.2),
                color=(56, 189, 248), size=random.uniform(1.5, 3.5),
                lifetime=random.randint(200, 500), p_type='bg'
            ))

    def reset_game(self):
        self.engine.reset()
        self.game_over = False
        self.winner_msg = ""
        self.winning_coords = []
        self.turn = HUMAN_PIECE

    def draw_disc_3d(self, surface, x, y, piece, custom_radius=None, glow=False):
        r = custom_radius if custom_radius else RADIUS
        col_main, col_dark, col_glow = (
            (COLOR_HUMAN, COLOR_HUMAN_DARK, COLOR_HUMAN_GLOW) if piece == HUMAN_PIECE 
            else (COLOR_AI, COLOR_AI_DARK, COLOR_AI_GLOW) if piece == AI_PIECE 
            else (None, None, None)
        )
        if not col_main:
            return

        shadow_surf = pygame.Surface((r * 2 + 12, r * 2 + 12), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 110), (r + 6, r + 8), r)
        surface.blit(shadow_surf, (x - r - 6, y - r - 6))

        if glow:
            glow_surf = pygame.Surface((r * 2 + 24, r * 2 + 24), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*col_main, 120), (r + 12, r + 12), r + 8)
            surface.blit(glow_surf, (x - r - 12, y - r - 12))

        pygame.draw.circle(surface, col_dark, (int(x), int(y)), r)
        pygame.draw.circle(surface, col_main, (int(x), int(y)), r - 3)
        pygame.draw.circle(surface, col_dark, (int(x), int(y)), r - 10, width=2)
        pygame.draw.circle(surface, col_main, (int(x), int(y)), r - 12)

        shine_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shine_surf, (*col_glow, 160), pygame.Rect(r // 3, r // 4, int(r * 1.1), int(r * 0.55)))
        surface.blit(shine_surf, (x - r, y - r))
        pygame.draw.circle(surface, (*col_glow, 90), (int(x - r * 0.2), int(y - r * 0.2)), int(r * 0.15))

    def draw_glass_button(self, rect, text, bg_color, is_selected=False, hover=False, icon_type=None):
        color = bg_color if (is_selected or hover) else COLOR_DARK_GRAY
        border_color = COLOR_CYAN if hover else (COLOR_WHITE if is_selected else (71, 85, 105))

        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 90), shadow_surf.get_rect(), border_radius=10)
        self.screen.blit(shadow_surf, rect.move(0, 3))

        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, rect, width=2 if (is_selected or hover) else 1, border_radius=10)

        highlight_surf = pygame.Surface((rect.width, rect.height // 2), pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, 18))
        self.screen.blit(highlight_surf, rect.topleft)

        txt_surface = self.font_small.render(text, True, COLOR_WHITE)
        if icon_type:
            total_width = txt_surface.get_width() + 18
            start_x = rect.centerx - total_width // 2
            draw_vector_icon(self.screen, icon_type, start_x + 6, rect.centery, size=12, color=COLOR_WHITE)
            self.screen.blit(txt_surface, (start_x + 22, rect.centery - txt_surface.get_height() // 2))
        else:
            self.screen.blit(txt_surface, txt_surface.get_rect(center=rect.center))

    def draw_mute_button(self, rect):
        is_hover = rect.collidepoint(pygame.mouse.get_pos())
        color = (239, 68, 68) if self.music.is_muted else (34, 197, 94)
        pygame.draw.rect(self.screen, COLOR_DARK_GRAY, rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_WHITE if is_hover else color, rect, width=2, border_radius=8)

        cx, cy = rect.center
        pygame.draw.polygon(self.screen, COLOR_WHITE, [(cx - 6, cy - 3), (cx - 2, cy - 3), (cx + 3, cy - 7), (cx + 3, cy + 7), (cx - 2, cy + 3), (cx - 6, cy + 3)])
        if self.music.is_muted:
            pygame.draw.line(self.screen, (239, 68, 68), (cx - 6, cy - 6), (cx + 7, cy + 7), 2)
            pygame.draw.line(self.screen, (239, 68, 68), (cx + 7, cy - 6), (cx - 6, cy + 7), 2)
        else:
            pygame.draw.arc(self.screen, COLOR_WHITE, (cx - 1, cy - 5, 8, 10), -math.pi / 3, math.pi / 3, 2)
            pygame.draw.arc(self.screen, COLOR_WHITE, (cx + 2, cy - 8, 10, 16), -math.pi / 3, math.pi / 3, 2)

    def spawn_landing_sparks(self, x, y, color):
        for _ in range(16):
            angle = random.uniform(math.pi * 1.1, math.pi * 1.9)
            speed = random.uniform(3, 8)
            self.particles.append(Particle(x, y, math.cos(angle) * speed, math.sin(angle) * speed, color, random.uniform(2, 5), random.randint(15, 35), 'spark'))

    def spawn_victory_confetti(self):
        colors = [(239, 68, 68), (245, 158, 11), (56, 189, 248), (34, 197, 94), (250, 204, 21), (168, 85, 247)]
        for _ in range(90):
            self.particles.append(Particle(random.randint(50, WIDTH - 50), random.randint(-20, 100), random.uniform(-4, 4), random.uniform(1, 5), random.choice(colors), random.uniform(6, 11), random.randint(120, 250), 'confetti'))

    def update_and_draw_particles(self):
        for p in self.particles[:]:
            p.update()
            p.draw(self.screen)
            if p.lifetime <= 0 and p.p_type != 'bg':
                self.particles.remove(p)

    def render_start_menu(self):
        self.screen.fill(COLOR_BG)
        self.pulse_timer += 0.04
        self.update_and_draw_particles()
        self.draw_mute_button(self.btn_mute_rect)

        title_txt = self.font_super_title.render("CONECTA 4", True, COLOR_GOLD)
        title_rect = title_txt.get_rect(center=(WIDTH // 2, 90))
        title_shadow = self.font_super_title.render("CONECTA 4", True, (0, 0, 0))
        self.screen.blit(title_shadow, title_rect.move(3, 3))
        self.screen.blit(title_txt, title_rect)

        sub_txt = self.font_main.render("Agente Inteligente con Inteligencia Artificial", True, COLOR_CYAN)
        self.screen.blit(sub_txt, sub_txt.get_rect(center=(WIDTH // 2, 135)))

        center_x, center_y = WIDTH // 2, HEIGHT // 2 - 75
        card_rect = pygame.Rect(center_x - 220, center_y - 70, 440, 140)
        pygame.draw.rect(self.screen, COLOR_BOARD_OUTER, card_rect, border_radius=20)
        pygame.draw.rect(self.screen, COLOR_BOARD, card_rect.inflate(-8, -8), border_radius=16)
        pygame.draw.rect(self.screen, COLOR_BOARD_INNER, card_rect, width=3, border_radius=20)

        offset_y_float = int(math.sin(self.pulse_timer) * 4)
        for offset_x, _ in [(-135, 1), (-45, 1), (45, 1), (135, 1)]:
            self.draw_disc_3d(self.screen, center_x + offset_x, center_y + offset_y_float, HUMAN_PIECE, custom_radius=32, glow=True)
        pygame.draw.line(self.screen, COLOR_GOLD, (center_x - 135, center_y + offset_y_float), (center_x + 135, center_y + offset_y_float), 4)

        rules_box = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 + 25, 520, 85)
        pygame.draw.rect(self.screen, (17, 24, 39), rules_box, border_radius=12)
        pygame.draw.rect(self.screen, (51, 65, 85), rules_box, width=1, border_radius=12)
        draw_vector_icon(self.screen, "target", rules_box.x + 24, rules_box.y + 20, size=12, color=COLOR_GOLD)
        self.screen.blit(self.font_small.render("OBJETIVO RÁPIDO:", True, COLOR_GOLD), (rules_box.x + 36, rules_box.y + 12))
        self.screen.blit(self.font_small.render("• Forma una línea de 4 fichas de tu color (Horizontal, Vertical o Diagonal).", True, COLOR_WHITE), (rules_box.x + 15, rules_box.y + 34))
        self.screen.blit(self.font_small.render("• Compite contra el Agente IA con algoritmo Minimax y Poda Alfa-Beta.", True, COLOR_GRAY), (rules_box.x + 15, rules_box.y + 56))

        mouse_pos = pygame.mouse.get_pos()
        self.draw_glass_button(self.btn_play_start, "JUGAR", (22, 163, 74), hover=self.btn_play_start.collidepoint(mouse_pos), icon_type="play")
        self.draw_glass_button(self.btn_instructions_start, "Instrucciones", (37, 99, 235), hover=self.btn_instructions_start.collidepoint(mouse_pos), icon_type="info")
        
        footer_txt = self.font_small.render("Proyecto de IA - Minimax con Poda Alfa-Beta | IA & Gráficos Vectoriales HD", True, COLOR_GRAY)
        self.screen.blit(footer_txt, footer_txt.get_rect(center=(WIDTH // 2, HEIGHT - 22)))

    def render_difficulty_menu(self):
        self.screen.fill(COLOR_BG)
        self.update_and_draw_particles()
        self.draw_mute_button(self.btn_mute_rect)

        self.screen.blit(self.font_super_title.render("SELECCIONA DIFICULTAD", True, COLOR_WHITE), self.font_super_title.render("SELECCIONA DIFICULTAD", True, COLOR_WHITE).get_rect(center=(WIDTH // 2, 90)))
        self.screen.blit(self.font_main.render("Elige la capacidad de procesamiento del Agente Inteligente:", True, COLOR_CYAN), self.font_main.render("Elige la capacidad de procesamiento del Agente Inteligente:", True, COLOR_CYAN).get_rect(center=(WIDTH // 2, 145)))

        self.draw_difficulty_card(self.btn_diff_easy, "Nivel Fácil", "Agente casual: Jugadas semi-casuales con detección básica.", BTN_FACIL_COLOR)
        self.draw_difficulty_card(self.btn_diff_medium, "Nivel Medio", "Agente defensivo: Minimax a profundidad 2 e interceptación de victoria.", BTN_MEDIO_COLOR)
        self.draw_difficulty_card(self.btn_diff_hard, "Nivel Difícil (Maestro)", "Agente experto: Minimax + Poda Alfa-Beta a profundidad 5 con ordenamiento táctico.", BTN_DIFICIL_COLOR)

        mouse_pos = pygame.mouse.get_pos()
        self.draw_glass_button(self.btn_back_to_menu, "Menú Principal", COLOR_DARK_GRAY, hover=self.btn_back_to_menu.collidepoint(mouse_pos), icon_type="back")

    def draw_difficulty_card(self, rect, title, description, accent_color):
        is_hover = rect.collidepoint(pygame.mouse.get_pos())
        bg_color = (30, 41, 59) if not is_hover else (47, 63, 86)
        
        s_rect = rect.move(0, 4)
        s_surf = pygame.Surface((s_rect.width, s_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s_surf, (0, 0, 0, 80), s_surf.get_rect(), border_radius=14)
        self.screen.blit(s_surf, s_rect)

        pygame.draw.rect(self.screen, bg_color, rect, border_radius=14)
        pygame.draw.rect(self.screen, accent_color if is_hover else (71, 85, 105), rect, width=3 if is_hover else 1, border_radius=14)
        pygame.draw.circle(self.screen, accent_color, (rect.x + 30, rect.y + 26), 9)
        pygame.draw.circle(self.screen, COLOR_WHITE, (rect.x + 30, rect.y + 26), 9, width=1)
        self.screen.blit(self.font_title.render(title, True, accent_color), (rect.x + 48, rect.y + 12))
        self.screen.blit(self.font_small.render(description, True, COLOR_GRAY), (rect.x + 48, rect.y + 46))

    def render_instructions_menu(self):
        self.screen.fill(COLOR_BG)
        self.update_and_draw_particles()
        self.draw_mute_button(self.btn_mute_rect)

        self.screen.blit(self.font_super_title.render("GUÍA E INSTRUCCIONES", True, COLOR_GOLD), self.font_super_title.render("GUÍA E INSTRUCCIONES", True, COLOR_GOLD).get_rect(center=(WIDTH // 2, 65)))
        self.screen.blit(self.font_main.render("Aprende a jugar y domina la estrategia contra la Inteligencia Artificial", True, COLOR_CYAN), self.font_main.render("Aprende a jugar y domina la estrategia contra la Inteligencia Artificial", True, COLOR_CYAN).get_rect(center=(WIDTH // 2, 110)))

        cards = [
            {"rect": pygame.Rect(40, 140, 295, 230), "icon_type": "target", "title": "Reglas y Objetivo", "color": COLOR_CYAN, "lines": ["• Tu objetivo es alinear 4 fichas del", "  mismo color en dirección horizontal,", "  vertical o diagonal.", "• Tú juegas con las fichas Rojas.", "• El Agente IA juega con Amarillas.", "• El primero en hacer 4 en línea gana."]},
            {"rect": pygame.Rect(365, 140, 295, 230), "icon_type": "gamepad", "title": "Controles y Mecánica", "color": BTN_FACIL_COLOR, "lines": ["• Mueve el cursor sobre las columnas", "  para previsualizar la columna.", "• Haz clic en cualquier columna para", "  soltar tu ficha en la casilla libre.", "• Puedes reiniciar la partida o cambiar", "  de dificultad en cualquier momento."]},
            {"rect": pygame.Rect(40, 390, 295, 220), "icon_type": "cpu", "title": "Niveles de IA", "color": BTN_MEDIO_COLOR, "lines": ["• Fácil: IA casual y amigable.", "• Medio: IA defensiva a 2 niveles.", "• Difícil: Minimax + Poda Alfa-Beta", "  a profundidad 5. ¡Un desafío total", "  con evaluación heurística posicional!"]},
            {"rect": pygame.Rect(365, 390, 295, 220), "icon_type": "bulb", "title": "Estrategias Clave", "color": COLOR_GOLD, "lines": ["• Control del Centro: Dominar la", "  columna 3 abre más combinaciones.", "• Trampa Doble (Fork): Intenta crear", "  dos amenazas simultáneas para que", "  la IA no pueda bloquear ambas."]}
        ]

        for card in cards:
            r = card["rect"]
            s_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            pygame.draw.rect(s_surf, (0, 0, 0, 90), s_surf.get_rect(), border_radius=14)
            self.screen.blit(s_surf, r.move(0, 4))
            pygame.draw.rect(self.screen, (17, 24, 39), r, border_radius=14)
            pygame.draw.rect(self.screen, card["color"], r, width=2, border_radius=14)
            draw_vector_icon(self.screen, card["icon_type"], r.x + 24, r.y + 28, size=14, color=card["color"])
            self.screen.blit(self.font_title.render(card['title'], True, card["color"]), (r.x + 44, r.y + 15))
            
            curr_y = r.y + 55
            for line in card["lines"]:
                self.screen.blit(self.font_small.render(line, True, COLOR_WHITE), (r.x + 15, curr_y))
                curr_y += 24

        mouse_pos = pygame.mouse.get_pos()
        self.draw_glass_button(self.btn_inst_back, "Volver al Menú", COLOR_DARK_GRAY, hover=self.btn_inst_back.collidepoint(mouse_pos), icon_type="back")
        self.draw_glass_button(self.btn_inst_play, "¡Jugar Ahora!", (22, 163, 74), hover=self.btn_inst_play.collidepoint(mouse_pos), icon_type="play")

    def render_gameplay(self, hover_col=None):
        self.screen.fill(COLOR_BG)
        self.pulse_timer += 0.05
        self.update_and_draw_particles()
        mouse_pos = pygame.mouse.get_pos()

        pygame.draw.rect(self.screen, COLOR_HEADER, (0, 0, WIDTH, BOARD_OFFSET_Y))
        pygame.draw.line(self.screen, COLOR_BOARD_INNER, (0, BOARD_OFFSET_Y - 1), (WIDTH, BOARD_OFFSET_Y - 1), 2)

        self.draw_glass_button(self.btn_facil_rect, "Fácil", BTN_FACIL_COLOR, is_selected=(self.difficulty == EASY), hover=self.btn_facil_rect.collidepoint(mouse_pos))
        self.draw_glass_button(self.btn_medio_rect, "Medio", BTN_MEDIO_COLOR, is_selected=(self.difficulty == MEDIUM), hover=self.btn_medio_rect.collidepoint(mouse_pos))
        self.draw_glass_button(self.btn_dificil_rect, "Difícil", BTN_DIFICIL_COLOR, is_selected=(self.difficulty == HARD), hover=self.btn_dificil_rect.collidepoint(mouse_pos))
        self.draw_glass_button(self.btn_reset_rect, "Reiniciar", COLOR_DARK_GRAY, hover=self.btn_reset_rect.collidepoint(mouse_pos), icon_type="reset")
        self.draw_glass_button(self.btn_menu_game_rect, "Menú", COLOR_DARK_GRAY, hover=self.btn_menu_game_rect.collidepoint(mouse_pos), icon_type="home")
        self.draw_mute_button(self.btn_mute_rect)

        score_text = f"Humano: {self.score_human}   |   IA: {self.score_ai}   |   Empates: {self.score_draws}"
        self.screen.blit(self.font_small.render(score_text, True, COLOR_GRAY), (15, 55))

        status_txt, status_color = (
            ("Tu turno (Rojo)", COLOR_HUMAN) if not self.game_over and self.turn == HUMAN_PIECE 
            else ("Pensando Agente IA...", COLOR_AI) if not self.game_over 
            else ("¡Partida finalizada!", COLOR_GOLD)
        )
        txt_status = self.font_main.render(status_txt, True, status_color)
        self.screen.blit(txt_status, (WIDTH - txt_status.get_width() - 15, 52))

        board_rect = pygame.Rect(0, BOARD_OFFSET_Y, WIDTH, HEIGHT - BOARD_OFFSET_Y)
        pygame.draw.rect(self.screen, COLOR_BOARD_OUTER, board_rect)
        pygame.draw.rect(self.screen, COLOR_BOARD, board_rect.inflate(-8, -8), border_radius=12)
        pygame.draw.rect(self.screen, COLOR_BOARD_INNER, board_rect, width=3, border_radius=12)

        if hover_col is not None and not self.game_over and self.turn == HUMAN_PIECE and self.engine.is_valid_location(hover_col):
            col_surf = pygame.Surface((SQUARE_SIZE, HEIGHT - BOARD_OFFSET_Y), pygame.SRCALPHA)
            col_surf.fill((56, 189, 248, 25))
            self.screen.blit(col_surf, (hover_col * SQUARE_SIZE, BOARD_OFFSET_Y))

        for r in range(ROWS):
            for c in range(COLS):
                screen_y = int(HEIGHT - (r + 1) * SQUARE_SIZE + SQUARE_SIZE / 2)
                screen_x = int(c * SQUARE_SIZE + SQUARE_SIZE / 2)
                piece = self.engine.board[r][c]
                if piece == EMPTY:
                    pygame.draw.circle(self.screen, COLOR_SLOT_SHADOW, (screen_x, screen_y), RADIUS + 1)
                    pygame.draw.circle(self.screen, COLOR_SLOT, (screen_x, screen_y), RADIUS)
                    pygame.draw.circle(self.screen, (20, 30, 55), (screen_x, screen_y), RADIUS, width=2)
                else:
                    self.draw_disc_3d(self.screen, screen_x, screen_y, piece, glow=((r, c) in self.winning_coords))

        if self.game_over and self.winning_coords:
            glow_pulse = int(abs(math.sin(self.pulse_timer * 2)) * 6)
            for (r, c) in self.winning_coords:
                screen_y = int(HEIGHT - (r + 1) * SQUARE_SIZE + SQUARE_SIZE / 2)
                screen_x = int(c * SQUARE_SIZE + SQUARE_SIZE / 2)
                pygame.draw.circle(self.screen, COLOR_GOLD, (screen_x, screen_y), RADIUS + 4 + glow_pulse, width=4)

            r0, c0 = self.winning_coords[0]
            r3, c3 = self.winning_coords[3]
            pygame.draw.line(self.screen, COLOR_GOLD, 
                             (int(c0 * SQUARE_SIZE + SQUARE_SIZE / 2), int(HEIGHT - (r0 + 1) * SQUARE_SIZE + SQUARE_SIZE / 2)), 
                             (int(c3 * SQUARE_SIZE + SQUARE_SIZE / 2), int(HEIGHT - (r3 + 1) * SQUARE_SIZE + SQUARE_SIZE / 2)), 6)

        if hover_col is not None and not self.game_over and self.turn == HUMAN_PIECE and self.engine.is_valid_location(hover_col):
            drop_x = int(hover_col * SQUARE_SIZE + SQUARE_SIZE / 2)
            drop_y = int(BOARD_OFFSET_Y - SQUARE_SIZE / 2 + math.sin(self.pulse_timer * 3) * 4)
            self.draw_disc_3d(self.screen, drop_x, drop_y, HUMAN_PIECE, custom_radius=RADIUS - 4, glow=True)
            draw_vector_icon(self.screen, "arrow_down", drop_x, drop_y + RADIUS + 10, size=6, color=COLOR_CYAN)

        if self.game_over:
            self.draw_victory_banner()

    def animate_drop(self, col, target_row, piece):
        start_y = BOARD_OFFSET_Y - SQUARE_SIZE / 2
        target_y = HEIGHT - (target_row + 1) * SQUARE_SIZE + SQUARE_SIZE / 2
        x = int(col * SQUARE_SIZE + SQUARE_SIZE / 2)
        vy, gravity, curr_y = 2.0, 3.2, start_y

        while curr_y < target_y:
            vy += gravity
            curr_y = min(target_y, curr_y + vy)
            self.render_gameplay()
            self.draw_disc_3d(self.screen, x, int(curr_y), piece)
            pygame.display.update()
            self.clock.tick(60)

        self.spawn_landing_sparks(x, int(target_y), COLOR_HUMAN if piece == HUMAN_PIECE else COLOR_AI)

    def draw_victory_banner(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        banner_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 60, 500, 120)
        pygame.draw.rect(self.screen, COLOR_HEADER, banner_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLOR_GOLD, banner_rect, width=3, border_radius=16)

        self.screen.blit(self.font_banner.render(self.winner_msg, True, COLOR_GOLD), self.font_banner.render(self.winner_msg, True, COLOR_GOLD).get_rect(center=(WIDTH // 2, HEIGHT // 2 - 16)))
        self.screen.blit(self.font_main.render("Haz clic en cualquier lugar para jugar otra partida", True, COLOR_WHITE), self.font_main.render("Haz clic en cualquier lugar para jugar otra partida", True, COLOR_WHITE).get_rect(center=(WIDTH // 2, HEIGHT // 2 + 26)))

    def handle_click(self, pos):
        if self.btn_mute_rect.collidepoint(pos):
            self.music.toggle_mute()
            return

        if self.app_state == STATE_START_MENU:
            if self.btn_play_start.collidepoint(pos): self.app_state = STATE_DIFFICULTY_MENU
            elif self.btn_instructions_start.collidepoint(pos): self.app_state = STATE_INSTRUCTIONS
        elif self.app_state == STATE_DIFFICULTY_MENU:
            if self.btn_diff_easy.collidepoint(pos): self.difficulty, self.app_state = EASY, STATE_GAMEPLAY
            elif self.btn_diff_medium.collidepoint(pos): self.difficulty, self.app_state = MEDIUM, STATE_GAMEPLAY
            elif self.btn_diff_hard.collidepoint(pos): self.difficulty, self.app_state = HARD, STATE_GAMEPLAY
            elif self.btn_back_to_menu.collidepoint(pos): self.app_state = STATE_START_MENU
            if self.app_state == STATE_GAMEPLAY: self.reset_game()
        elif self.app_state == STATE_INSTRUCTIONS:
            if self.btn_inst_back.collidepoint(pos): self.app_state = STATE_START_MENU
            elif self.btn_inst_play.collidepoint(pos): self.app_state = STATE_DIFFICULTY_MENU
        elif self.app_state == STATE_GAMEPLAY:
            x, y = pos
            if y < BOARD_OFFSET_Y:
                if self.btn_facil_rect.collidepoint(pos): self.difficulty = EASY; self.reset_game()
                elif self.btn_medio_rect.collidepoint(pos): self.difficulty = MEDIUM; self.reset_game()
                elif self.btn_dificil_rect.collidepoint(pos): self.difficulty = HARD; self.reset_game()
                elif self.btn_reset_rect.collidepoint(pos): self.reset_game()
                elif self.btn_menu_game_rect.collidepoint(pos): self.app_state = STATE_START_MENU
                return

            if self.game_over:
                self.reset_game()
                return

            if self.turn == HUMAN_PIECE and y >= BOARD_OFFSET_Y:
                col = int(x // SQUARE_SIZE)
                if self.engine.is_valid_location(col):
                    row = self.engine.get_next_open_row(col)
                    self.animate_drop(col, row, HUMAN_PIECE)
                    self.engine.drop_piece(row, col, HUMAN_PIECE)

                    is_win, coords = self.engine.winning_move(HUMAN_PIECE)
                    if is_win:
                        self.game_over, self.winner_msg, self.winning_coords = True, "¡HAS GANADO!", coords
                        self.score_human += 1
                        self.spawn_victory_confetti()
                    elif not self.engine.get_valid_locations():
                        self.game_over, self.winner_msg, self.score_draws = True, "¡EMPATE!", self.score_draws + 1
                    else:
                        self.turn = AI_PIECE

    def run(self):
        running = True
        while running:
            hover_col = int(pygame.mouse.get_pos()[0] // SQUARE_SIZE) if self.app_state == STATE_GAMEPLAY and pygame.mouse.get_pos()[1] >= BOARD_OFFSET_Y else None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.music.stop()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            if self.app_state == STATE_START_MENU: self.render_start_menu()
            elif self.app_state == STATE_DIFFICULTY_MENU: self.render_difficulty_menu()
            elif self.app_state == STATE_INSTRUCTIONS: self.render_instructions_menu()
            elif self.app_state == STATE_GAMEPLAY:
                if not self.game_over and self.turn == AI_PIECE:
                    self.render_gameplay()
                    pygame.display.update()
                    time.sleep(0.3)

                    ai_col = self.ai.get_best_move(self.difficulty)
                    if ai_col is not None and self.engine.is_valid_location(ai_col):
                        row = self.engine.get_next_open_row(ai_col)
                        self.animate_drop(ai_col, row, AI_PIECE)
                        self.engine.drop_piece(row, ai_col, AI_PIECE)

                        is_win, coords = self.engine.winning_move(AI_PIECE)
                        if is_win:
                            self.game_over, self.winner_msg, self.winning_coords = True, "¡LA IA HA GANADO!", coords
                            self.score_ai += 1
                            self.spawn_victory_confetti()
                        elif not self.engine.get_valid_locations():
                            self.game_over, self.winner_msg, self.score_draws = True, "¡EMPATE!", self.score_draws + 1
                        else:
                            self.turn = HUMAN_PIECE
                self.render_gameplay(hover_col)

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Connect4GUI()
    game.run()