"""
Traffic-aware UAV road inspection simulator
Author: Yumeng Sun
Paper: Submitted to Transportation Research Part C
Description:
Interactive simulation illustrating UAV scanning under dynamic traffic
and the effect of occlusion on pavement visibility completeness.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Slider, Button

# === Global Font and Style ===
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': 'black',
    'axes.labelcolor': 'black',
    'text.color': 'black'
})

# === Parameters Setting ===
L = 100.0
footprint = 20.0
mean_speed = 5.0
sd_speed = 1.0
car_length = 5.0
n_segments = 100
dt = 0.1
T_head = 1.5
max_cars = 50

rng = np.random.default_rng()

def init_sim(n_cars, v_uav):
    """Initialize Simulation Trajectory"""
    T_max = (L + footprint) / v_uav
    ts = np.arange(0, T_max + dt/2, dt)
    pos = rng.random(n_cars) * L
    speed = np.abs(rng.normal(mean_speed, sd_speed, n_cars))
    order = np.argsort(pos)[::-1]
    pos, speed = pos[order], speed[order]
    traj = np.zeros((len(ts), n_cars))
    for k in range(len(ts)):
        traj[k] = pos
        new_pos = np.zeros_like(pos)
        for i in range(n_cars):
            if i == 0:
                v_i = speed[0]
            else:
                raw_gap = pos[i-1] - pos[i] - car_length
                gap = raw_gap if raw_gap >= 0 else raw_gap + L
                v_i = min(speed[i], gap / T_head)
            new_pos[i] = (pos[i] + v_i * dt) % L
        pos = new_pos
    visited = np.zeros(n_segments, bool)
    ever_vis = np.zeros(n_segments, bool)
    return ts, traj, visited, ever_vis

# === Initial Value ===
v0, n0 = 10.0, 20
ts, traj, visited, ever_vis = init_sim(n0, v0)

# === Create a Canvas ===
fig = plt.figure(figsize=(8, 6))
gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 0.4])
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
plt.subplots_adjust(left=0.08, right=0.92, top=0.9, bottom=0.2, hspace=0.45)

# === Upper Figure：UAV + Cars ===
uav = Rectangle((0, 2), footprint, 0.5, color='#1f77b4', alpha=0.9, ec='black')
ax1.add_patch(uav)
cars = [ax1.add_patch(Rectangle((0, -1.5), car_length, 0.5,
        color='#7f7f7f', ec='none', visible=False)) for _ in range(max_cars)]

ax1.set_xlim(0, L)
ax1.set_ylim(-3, 4)
ax1.set_yticks([])
ax1.set_title("UAV Scanning & Traffic Flow", fontweight='bold', pad=8)

# === Lowerer Figure：Visibility Display ===
centers = np.linspace(0, L, n_segments, endpoint=False)
width = L / n_segments
bars = []
for c in centers:
    bar = Rectangle((c, 0), width, 1, color='lightgray', ec='none')
    ax2.add_patch(bar)
    bars.append(bar)

ax2.set_xlim(0, L)
ax2.set_ylim(0, 1)
ax2.set_yticks([])
ax2.set_xticks([])
ax2.set_title("Road Segment Visibility (Green if ever visible; Red if always occluded)",
              fontsize=11, pad=8)
vis_text = ax2.text(0.98, 0.92, "", transform=ax2.transAxes, ha='right', va='top', fontsize=11)

# === Slider Button Layout ===
ax_v = plt.axes([0.15, 0.12, 0.55, 0.03], facecolor='white')
ax_n = plt.axes([0.15, 0.07, 0.55, 0.03], facecolor='white')
slider_v = Slider(ax_v, "UAV Speed (m/s)", 1, 20, valinit=v0)
slider_n = Slider(ax_n, "Number of Cars", 0, max_cars, valinit=n0, valstep=1)

ax_play = plt.axes([0.78, 0.04, 0.08, 0.05])
ax_reset = plt.axes([0.88, 0.04, 0.08, 0.05])
btn_play = Button(ax_play, "Play", color='white', hovercolor='#d0d0d0')
btn_reset = Button(ax_reset, "Reset", color='white', hovercolor='#d0d0d0')

txt_v = ax_v.text(1.02, 0.5, f"{v0:.1f}", transform=ax_v.transAxes, va='center', fontsize=10)
txt_n = ax_n.text(1.02, 0.5, f"{n0}", transform=ax_n.transAxes, va='center', fontsize=10)

playing = False
timer = fig.canvas.new_timer(interval=int(dt * 1000))
timer.counter = 0

# === Update Function ===
def update(val=None):
    t = timer.counter * dt if playing else 0
    i = min(int(round(t / dt)), len(ts) - 1)
    uav.set_x(slider_v.val * t)

    nc = int(slider_n.val)
    for idx, c in enumerate(cars):
        if idx < nc:
            x = traj[i, idx]
            c.set_visible(0 <= x <= L)
            c.set_x(x)
        else:
            c.set_visible(False)

    for j, x in enumerate(centers):
        if uav.get_x() <= x <= uav.get_x() + footprint:
            visited[j] = True
            occl = any(cars[k].get_visible() and cars[k].get_x() <= x <= cars[k].get_x() + car_length
                       for k in range(nc))
            if not occl:
                ever_vis[j] = True
        bars[j].set_facecolor(
            'lightgray' if not visited[j]
            else '#2ca02c' if ever_vis[j]
            else '#d62728'
        )

    rate = (ever_vis.sum() / visited.sum() * 100) if visited.sum() > 0 else 0
    vis_text.set_text(f"Visible: {rate:.1f}%")
    fig.canvas.draw_idle()

# === Control Logic ===
def reset(event=None):
    global ts, traj, visited, ever_vis
    timer.counter = 0
    ts, traj, visited, ever_vis = init_sim(int(slider_n.val), slider_v.val)
    vis_text.set_text("")
    update()

def toggle_play(event):
    global playing
    playing = not playing
    btn_play.label.set_text('Pause' if playing else 'Play')
    if playing:
        timer.start()
    else:
        timer.stop()

def advance_time():
    timer.counter += 1
    update()

slider_v.on_changed(lambda v: (txt_v.set_text(f"{v:.1f}"), reset()))
slider_n.on_changed(lambda n: (txt_n.set_text(f"{int(n)}"), reset()))
btn_play.on_clicked(toggle_play)
btn_reset.on_clicked(reset)
timer.add_callback(advance_time)

reset()
plt.show()
