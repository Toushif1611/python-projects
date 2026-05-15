import pygame
import random
import math

pygame.init()

# Window layout
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gas Physics Simulation")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 80, 80)
BLUE = (80, 160, 255)
YELLOW = (255, 220, 80)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)

# Fonts
FONT_SMALL = pygame.font.SysFont(None, 18)
FONT_MEDIUM = pygame.font.SysFont(None, 22)
FONT_LARGE = pygame.font.SysFont(None, 28)

# Simulation panels
SIM_WIDTH = 760
PANEL_X = SIM_WIDTH + 10
PANEL_WIDTH = WIDTH - SIM_WIDTH - 20
BOX_BOTTOM = HEIGHT // 2 + 130
BOX_LEFT = SIM_WIDTH // 2 - 100
BOX_TOP_LIMIT = 60

# Physical constants
R = 0.1  # ideal gas constant in simulation units
GAMMA = 1.4  # adiabatic exponent for diatomic gas approximation

# Runtime state
selected_process = "None"
manual_volume_mode = False
target_temperature = None
target_pressure = None
adiabatic_constant = None

temperature_scale = 1.0
wall_collisions = 0.0
last_time = pygame.time.get_ticks()
pressure = 0.0
pv_history = []
max_pv_points = 200

# Molecule / piston state
num_molecules = 30
mass_scale = 1.0
collision_elasticity = 1.0
bottom_elasticity = 1.0
gravity = 0.0

# Slider interaction state
slider_y = HEIGHT - 50
dragging_slider = None

process_modes = ["None", "Isothermal", "Isochoric", "Isobaric", "Adiabatic"]
buttons = {}
button_y = 40
button_h = 32
for name in process_modes[1:]:
    buttons[name] = pygame.Rect(PANEL_X, button_y, PANEL_WIDTH, button_h)
    button_y += 42

sliders = {
    'width': {'x': 40, 'y': slider_y, 'width': 100, 'min': 120, 'max': 380, 'value': 200, 'label': 'Width'},
    'height': {'x': 150, 'y': slider_y, 'width': 100, 'min': 80, 'max': 260, 'value': 120, 'label': 'Height'},
    'radius': {'x': 260, 'y': slider_y, 'width': 100, 'min': 2, 'max': 12, 'value': 4, 'label': 'Radius'},
    'num': {'x': 370, 'y': slider_y, 'width': 100, 'min': 10, 'max': 100, 'value': 30, 'label': 'Num'},
    'mass': {'x': 480, 'y': slider_y, 'width': 100, 'min': 0.5, 'max': 5.0, 'value': 1.0, 'label': 'Mass'},
    'piston': {'x': 590, 'y': slider_y, 'width': 100, 'min': 10, 'max': 200, 'value': 50, 'label': 'Piston M'},
    'atm': {'x': 700, 'y': slider_y, 'width': 100, 'min': 0.05, 'max': 0.8, 'value': 0.18, 'label': 'Ambient P'},
    'elas': {'x': 40, 'y': slider_y - 40, 'width': 100, 'min': 0.4, 'max': 1.0, 'value': 1.0, 'label': 'Coll Elastic'},
    'wall': {'x': 150, 'y': slider_y - 40, 'width': 100, 'min': 0.4, 'max': 1.0, 'value': 1.0, 'label': 'Wall Elastic'}
}


class Piston:
    """A moving piston representing the top wall of the gas container."""

    def __init__(self, width, height, mass, ambient_pressure):
        self.width = width
        self.mass = mass
        self.external_pressure = ambient_pressure
        self.bottom = BOX_BOTTOM
        self.thickness = 12
        self.y = self.bottom - height - self.thickness
        self.velocity = 0.0
        self.impulse_sum = 0.0
        self.rest_y = self.y
        self.damping = 0.95

    @property
    def x(self):
        return SIM_WIDTH // 2 - self.width // 2

    @property
    def height(self):
        return max(20, self.bottom - (self.y + self.thickness))

    @property
    def gas_top(self):
        return self.y + self.thickness

    @property
    def rect(self):
        return pygame.Rect(self.x, int(self.y), self.width, self.thickness)

    def set_width(self, width):
        self.width = int(width)

    def set_mass(self, mass):
        self.mass = mass

    def set_external_pressure(self, pressure):
        self.external_pressure = pressure

    def add_impulse(self, impulse):
        self.impulse_sum += impulse

    def pressure_from_impulse(self, dt):
        if dt <= 0 or self.width <= 0:
            return 0.0
        p = self.impulse_sum / self.width / dt
        self.impulse_sum = 0.0
        return p

    def update(self, internal_pressure, dt, locked):
        if locked:
            self.velocity = 0.0
            return

        spring_force = -0.02 * (self.y - self.rest_y)
        net_force = (internal_pressure - self.external_pressure) * self.width + spring_force
        acceleration = net_force / (self.mass + 1e-5)
        self.velocity += acceleration * dt * 20
        self.velocity *= self.damping
        self.y += self.velocity * dt * 40
        self.y = max(BOX_TOP_LIMIT - self.thickness, min(self.y, self.bottom - self.thickness - 40))

    def lock_position(self):
        self.rest_y = self.y
        self.velocity = 0.0


def create_molecule(piston, color=GREEN):
    radius = int(sliders['radius']['value'])
    left = piston.x + radius
    right = piston.x + piston.width - radius
    top = piston.gas_top + radius
    bottom = piston.bottom - radius

    if top >= bottom:
        top = piston.gas_top
        bottom = top + 1

    return {
        'x': random.randint(left, right),
        'y': random.randint(int(top), int(bottom)),
        'dx': random.uniform(-3, 3),
        'dy': random.uniform(-3, 3),
        'mass': mass_scale,
        'radius': radius,
        'color': color
    }


def average_kinetic_energy(molecules):
    if not molecules:
        return 0.0
    return sum(0.5 * mol['mass'] * (mol['dx'] ** 2 + mol['dy'] ** 2) for mol in molecules) / len(molecules)


def average_speed(molecules):
    if not molecules:
        return 0.0
    return sum(math.hypot(mol['dx'], mol['dy']) for mol in molecules) / len(molecules)


def scale_velocities(molecules, factor):
    for mol in molecules:
        mol['dx'] *= factor
        mol['dy'] *= factor


def set_process_mode(mode, temperature, volume):
    global selected_process, target_temperature, target_pressure, adiabatic_constant
    selected_process = mode
    if mode == "Isothermal":
        target_temperature = temperature
    elif mode == "Isochoric":
        target_pressure = None
        adiabatic_constant = None
    elif mode == "Isobaric":
        target_pressure = pressure
    elif mode == "Adiabatic":
        adiabatic_constant = pressure * (volume ** GAMMA) if volume > 0 else None


def apply_process_constraints(molecules, volume, temperature, piston):
    global pressure
    if selected_process == "Isothermal" and target_temperature is not None and temperature > 0:
        factor = math.sqrt(max(0.001, target_temperature / temperature))
        scale_velocities(molecules, factor)
    elif selected_process == "Isobaric" and target_pressure is not None and pressure > 0:
        desired_temp = (target_pressure * volume) / (len(molecules) * R) if volume > 0 and molecules else 0
        if temperature > 0 and desired_temp > 0:
            factor = math.sqrt(desired_temp / temperature)
            scale_velocities(molecules, factor)
    elif selected_process == "Adiabatic" and adiabatic_constant is not None and volume > 0 and molecules:
        desired_pressure = adiabatic_constant / (volume ** GAMMA)
        desired_temp = (desired_pressure * volume) / (len(molecules) * R)
        if temperature > 0 and desired_temp > 0:
            factor = math.sqrt(desired_temp / temperature)
            scale_velocities(molecules, factor)
    if selected_process == "Isochoric":
        piston.lock_position()


def update_particles(molecules, piston):
    current_num = len(molecules)
    if num_molecules > current_num:
        for _ in range(num_molecules - current_num):
            molecules.append(create_molecule(piston))
    elif num_molecules < current_num:
        del molecules[num_molecules:]


def handle_molecule_collisions(molecules):
    for i in range(len(molecules)):
        for j in range(i + 1, len(molecules)):
            m1 = molecules[i]
            m2 = molecules[j]
            dx = m2['x'] - m1['x']
            dy = m2['y'] - m1['y']
            dist = math.hypot(dx, dy)
            min_dist = m1['radius'] + m2['radius']
            if 0 < dist < min_dist:
                nx = dx / dist
                ny = dy / dist
                overlap = min_dist - dist
                m1['x'] -= nx * overlap / 2
                m1['y'] -= ny * overlap / 2
                m2['x'] += nx * overlap / 2
                m2['y'] += ny * overlap / 2
                rvx = m2['dx'] - m1['dx']
                rvy = m2['dy'] - m1['dy']
                vel_norm = rvx * nx + rvy * ny
                if vel_norm > 0:
                    continue
                e = collision_elasticity
                impulse = -(1 + e) * vel_norm
                impulse /= (1 / m1['mass'] + 1 / m2['mass'])
                ix = impulse * nx
                iy = impulse * ny
                m1['dx'] -= ix / m1['mass']
                m1['dy'] -= iy / m1['mass']
                m2['dx'] += ix / m2['mass']
                m2['dy'] += iy / m2['mass']


def draw_slider(slider):
    label = FONT_SMALL.render(slider['label'], True, WHITE)
    screen.blit(label, (slider['x'], slider['y'] - 24))
    pygame.draw.rect(screen, WHITE, (slider['x'], slider['y'], slider['width'], 5))
    knob_x = slider['x'] + (slider['value'] - slider['min']) / (slider['max'] - slider['min']) * slider['width']
    pygame.draw.circle(screen, GREEN, (int(knob_x), slider['y'] + 2), 8)


def draw_sliders():
    for slider in sliders.values():
        draw_slider(slider)
    pygame.draw.rect(screen, RED, (40, HEIGHT - 120, 100, 30))
    pygame.draw.rect(screen, BLUE, (150, HEIGHT - 120, 100, 30))
    screen.blit(FONT_SMALL.render("Add Red", True, WHITE), (50, HEIGHT - 112))
    screen.blit(FONT_SMALL.render("Add Blue", True, WHITE), (158, HEIGHT - 112))


def draw_info_panel(temperature, theoretical_pressure, measured_pressure, n, piston):
    avg_spd = average_speed(molecules)
    lines = [
        f"Process: {selected_process}",
        f"Volume mode: {'Manual' if manual_volume_mode else 'Auto'}",
        f"Particles: {n}",
        f"Piston height: {int(piston.height)}",
        f"Volume: {int(piston.width * piston.height)}",
        f"Temperature: {temperature:.2f}",
        f"Measured P: {measured_pressure:.3f}",
        f"Ideal P: {theoretical_pressure:.3f}",
        f"Ambient P: {piston.external_pressure:.2f}",
        f"Avg speed: {avg_spd:.2f}",
        "H = heat, C = cool"
    ]
    x, y = 10, 10
    for line in lines:
        screen.blit(FONT_MEDIUM.render(line, True, WHITE), (x, y))
        y += 22


def draw_thermo_bars(temperature, piston):
    x = 20
    y = HEIGHT - 180
    width = 20
    temp_bar = min(100, temperature * 2)
    press_bar = min(100, pressure * 200)
    vol_bar = min(100, (piston.width * piston.height) / 50)
    pygame.draw.rect(screen, RED, (x, y - temp_bar, width, temp_bar))
    pygame.draw.rect(screen, BLUE, (x + 40, y - press_bar, width, press_bar))
    pygame.draw.rect(screen, GREEN, (x + 80, y - vol_bar, width, vol_bar))
    screen.blit(FONT_SMALL.render("T", True, WHITE), (x, y + 5))
    screen.blit(FONT_SMALL.render("P", True, WHITE), (x + 40, y + 5))
    screen.blit(FONT_SMALL.render("V", True, WHITE), (x + 80, y + 5))


def draw_process_buttons():
    screen.blit(FONT_LARGE.render("Iso-processes", True, WHITE), (PANEL_X, 10))
    for name, rect in buttons.items():
        color = YELLOW if selected_process == name else DARK_GRAY
        pygame.draw.rect(screen, color, rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
        text = FONT_MEDIUM.render(name, True, WHITE if selected_process != name else BLACK)
        screen.blit(text, text.get_rect(center=rect.center))
    clear_rect = pygame.Rect(PANEL_X, button_y + 10, PANEL_WIDTH, button_h)
    pygame.draw.rect(screen, GRAY, clear_rect, border_radius=6)
    pygame.draw.rect(screen, WHITE, clear_rect, 2, border_radius=6)
    screen.blit(FONT_MEDIUM.render("Clear / None", True, WHITE), clear_rect.center)

    manual_rect = pygame.Rect(PANEL_X, button_y + 10 + button_h + 10, PANEL_WIDTH, button_h)
    manual_color = BLUE if manual_volume_mode else DARK_GRAY
    pygame.draw.rect(screen, manual_color, manual_rect, border_radius=6)
    pygame.draw.rect(screen, WHITE, manual_rect, 2, border_radius=6)
    manual_text = "Manual Volume" if not manual_volume_mode else "Auto Volume"
    screen.blit(FONT_MEDIUM.render(manual_text, True, WHITE), manual_rect.center)
    return clear_rect, manual_rect


def draw_pv_plot():
    plot_x = PANEL_X
    plot_y = 300
    plot_w = PANEL_WIDTH
    plot_h = 220
    pygame.draw.rect(screen, DARK_GRAY, (plot_x, plot_y, plot_w, plot_h))
    pygame.draw.rect(screen, WHITE, (plot_x, plot_y, plot_w, plot_h), 2)
    screen.blit(FONT_MEDIUM.render("PV Cycle Plot", True, WHITE), (plot_x + 10, plot_y - 28))
    inner_pad = 30
    gx = plot_x + inner_pad
    gy = plot_y + 10
    gw = plot_w - inner_pad - 10
    gh = plot_h - inner_pad - 20
    pygame.draw.line(screen, WHITE, (gx, gy + gh), (gx + gw, gy + gh), 2)
    pygame.draw.line(screen, WHITE, (gx, gy), (gx, gy + gh), 2)
    screen.blit(FONT_SMALL.render("V", True, WHITE), (gx + gw - 10, gy + gh + 5))
    screen.blit(FONT_SMALL.render("P", True, WHITE), (gx - 20, gy - 5))
    if len(pv_history) < 2:
        return
    volumes = [p[0] for p in pv_history]
    pressures = [p[1] for p in pv_history]
    min_v, max_v = min(volumes), max(volumes)
    min_p, max_p = min(pressures), max(pressures)
    if max_v == min_v:
        max_v += 1
    if max_p == min_p:
        max_p += 1
    points = []
    for v, p in pv_history:
        px = gx + (v - min_v) / (max_v - min_v) * gw
        py = gy + gh - (p - min_p) / (max_p - min_p) * gh
        points.append((px, py))
    if len(points) >= 2:
        pygame.draw.lines(screen, GREEN, False, points, 2)
    for pt in points[-5:]:
        pygame.draw.circle(screen, YELLOW, (int(pt[0]), int(pt[1])), 3)
    screen.blit(FONT_SMALL.render(f"{min_v:.0f}", True, WHITE), (gx, gy + gh + 5))
    screen.blit(FONT_SMALL.render(f"{max_v:.0f}", True, WHITE), (gx + gw - 35, gy + gh + 5))
    screen.blit(FONT_SMALL.render(f"{min_p:.2f}", True, WHITE), (gx - 5, gy + gh - 15))
    screen.blit(FONT_SMALL.render(f"{max_p:.2f}", True, WHITE), (gx - 5, gy))


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


piston = Piston(width=sliders['width']['value'], height=sliders['height']['value'], mass=sliders['piston']['value'], ambient_pressure=sliders['atm']['value'])

molecules = [create_molecule(piston) for _ in range(num_molecules)]

running = True
while running:
    dt = clock.get_time() / 1000.0
    screen.fill(BLACK)
    clear_button_rect, manual_button_rect = draw_process_buttons()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if piston.x <= mouse_x <= piston.x + piston.width and piston.y <= mouse_y <= piston.y + piston.thickness:
                dragging_slider = None
            elif 40 <= mouse_x <= 140 and HEIGHT - 120 <= mouse_y <= HEIGHT - 90:
                molecules.append(create_molecule(piston))
                num_molecules = len(molecules)
                sliders['num']['value'] = num_molecules
            elif 150 <= mouse_x <= 250 and HEIGHT - 120 <= mouse_y <= HEIGHT - 90:
                molecules.append(create_molecule(piston, BLUE))
                num_molecules = len(molecules)
                sliders['num']['value'] = num_molecules
            elif clear_button_rect.collidepoint(mouse_x, mouse_y):
                selected_process = "None"
                target_temperature = None
                target_pressure = None
                adiabatic_constant = None
            elif manual_button_rect.collidepoint(mouse_x, mouse_y):
                manual_volume_mode = not manual_volume_mode
            else:
                clicked_button = False
                for name, rect in buttons.items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        current_temp = average_kinetic_energy(molecules)
                        current_vol = piston.width * piston.height
                        set_process_mode(name, current_temp, current_vol)
                        clicked_button = True
                        break
                if not clicked_button:
                    for key, slider in sliders.items():
                        knob_x = slider['x'] + (slider['value'] - slider['min']) / (slider['max'] - slider['min']) * slider['width']
                        if abs(mouse_x - knob_x) < 10 and abs(mouse_y - slider['y'] - 2) < 10:
                            dragging_slider = key
                            break
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = None
        elif event.type == pygame.MOUSEMOTION and dragging_slider is not None:
            mouse_x, _ = pygame.mouse.get_pos()
            slider = sliders[dragging_slider]
            rel_x = mouse_x - slider['x']
            ratio = clamp(rel_x / slider['width'], 0.0, 1.0)
            new_value = slider['min'] + ratio * (slider['max'] - slider['min'])
            slider['value'] = new_value
            if dragging_slider == 'width':
                if selected_process != "Isochoric":
                    piston.set_width(new_value)
            elif dragging_slider == 'height':
                if selected_process != "Isochoric":
                    piston.y = piston.bottom - new_value - piston.thickness
                    piston.rest_y = piston.y
            elif dragging_slider == 'radius':
                for mol in molecules:
                    mol['radius'] = int(new_value)
            elif dragging_slider == 'num':
                num_molecules = int(new_value)
                update_particles(molecules, piston)
            elif dragging_slider == 'mass':
                mass_scale = float(new_value)
                for mol in molecules:
                    mol['mass'] = mass_scale
            elif dragging_slider == 'piston':
                piston.set_mass(float(new_value))
            elif dragging_slider == 'atm':
                piston.set_external_pressure(float(new_value))
            elif dragging_slider == 'elas':
                collision_elasticity = float(new_value)
            elif dragging_slider == 'wall':
                bottom_elasticity = float(new_value)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                temperature_scale *= 1.1
            elif event.key == pygame.K_c:
                temperature_scale *= 0.9
            elif event.key == pygame.K_UP:
                gravity += 0.01
            elif event.key == pygame.K_DOWN:
                gravity -= 0.01

    if temperature_scale != 1.0:
        scale_velocities(molecules, temperature_scale)
        temperature_scale = 1.0

    for mol in molecules:
        mol['dy'] += gravity
        mol['x'] += mol['dx']
        mol['y'] += mol['dy']
        if mol['x'] <= piston.x + mol['radius']:
            mol['x'] = piston.x + mol['radius']
            mol['dx'] = abs(mol['dx']) * bottom_elasticity
        elif mol['x'] >= piston.x + piston.width - mol['radius']:
            mol['x'] = piston.x + piston.width - mol['radius']
            mol['dx'] = -abs(mol['dx']) * bottom_elasticity
        if mol['y'] >= piston.bottom - mol['radius']:
            mol['y'] = piston.bottom - mol['radius']
            mol['dy'] = -abs(mol['dy']) * bottom_elasticity
        if mol['y'] <= piston.gas_top + mol['radius']:
            if piston.x + mol['radius'] <= mol['x'] <= piston.x + piston.width - mol['radius']:
                mol['y'] = piston.gas_top + mol['radius']
                mol['dy'] = abs(mol['dy']) * bottom_elasticity
                impulse = 2 * mol['mass'] * abs(mol['dy'])
                piston.add_impulse(impulse)
            else:
                mol['x'] = clamp(mol['x'], piston.x + mol['radius'], piston.x + piston.width - mol['radius'])

    handle_molecule_collisions(molecules)

    temperature = average_kinetic_energy(molecules)
    volume = piston.width * piston.height
    measured_pressure = piston.pressure_from_impulse(dt)
    pressure = measured_pressure if measured_pressure > 0 else pressure
    apply_process_constraints(molecules, volume, temperature, piston)
    temperature = average_kinetic_energy(molecules)
    theoretical_pressure = (len(molecules) * R * temperature) / volume if volume > 0 else 0.0
    if not manual_volume_mode:
        piston.update(theoretical_pressure, dt, selected_process == "Isochoric")
    else:
        piston.velocity = 0.0
    update_particles(molecules, piston)

    if dragging_slider != 'height':
        sliders['height']['value'] = piston.height
    if dragging_slider != 'width':
        sliders['width']['value'] = piston.width

    if len(pv_history) == 0 or abs(volume - (pv_history[-1][0] if pv_history else 0)) > 5 or pygame.time.get_ticks() % 200 < 20:
        pv_history.append((volume, theoretical_pressure))
        if len(pv_history) > max_pv_points:
            pv_history.pop(0)

    pygame.draw.rect(screen, WHITE, (piston.x, piston.gas_top, piston.width, piston.height), 2)
    pygame.draw.rect(screen, GRAY, piston.rect)
    pygame.draw.line(screen, WHITE, (piston.x, piston.bottom), (piston.x + piston.width, piston.bottom), 2)
    pygame.draw.line(screen, GRAY, (SIM_WIDTH, 0), (SIM_WIDTH, HEIGHT), 2)

    for mol in molecules:
        pygame.draw.circle(screen, mol['color'], (int(mol['x']), int(mol['y'])), int(mol['radius']))

    draw_sliders()
    draw_info_panel(temperature, theoretical_pressure, measured_pressure, len(molecules), piston)
    draw_thermo_bars(temperature, piston)
    draw_pv_plot()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
