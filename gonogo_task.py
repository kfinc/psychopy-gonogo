#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classical Go/No-Go Task
-----------------------
Go  (sky-blue circle): press SPACE as fast as possible
No-Go (orange circle): withhold response

Outputs: data/gonogo_sub-<ID>_ses-<N>_<timestamp>.csv
"""

from psychopy import visual, core, event, gui
import random, os, csv
from datetime import datetime

# ── Participant info ─────────────────────────────────────────────────────────
exp_info = {'Participant ID': '', 'Session': '1'}
dlg = gui.DlgFromDict(
    exp_info, title='Go/No-Go Task',
    order=['Participant ID', 'Session']
)
if not dlg.OK:
    core.quit()

# ── Window & stimuli ─────────────────────────────────────────────────────────
win       = visual.Window(fullscr=True, color='#404040', units='height')
fixation  = visual.TextStim(win, '+', height=0.06, color='white', font='Arial')
# Okabe-Ito colorblind-safe palette (Okabe & Ito, 2008)
go_stim   = visual.Circle(win, radius=0.12, fillColor='#56B4E9', lineColor='#56B4E9')  # sky blue
nogo_stim = visual.Circle(win, radius=0.12, fillColor='#E69F00', lineColor='#E69F00')  # orange
msg       = visual.TextStim(win, '', height=0.042, wrapWidth=1.4, color='white', font='Arial')

# ── Timing (seconds) ─────────────────────────────────────────────────────────
FIX_DUR  = 0.500          # fixation cross duration
STIM_DUR = 1.000          # stimulus on-screen + response window
ITI_MIN  = 0.300          # blank interval (jittered)
ITI_MAX  = 0.700

# ── Trial list ───────────────────────────────────────────────────────────────
N_TRIALS = 160
GO_PROP  = 0.75           # 75% Go, 25% No-Go (prepotent response)
n_go     = int(N_TRIALS * GO_PROP)
trials   = ['go'] * n_go + ['nogo'] * (N_TRIALS - n_go)
random.shuffle(trials)

# ── Output file ──────────────────────────────────────────────────────────────
pid     = exp_info['Participant ID']
ts      = datetime.now().strftime('%Y%m%d_%H%M%S')
outdir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(outdir, exist_ok=True)
outfile = os.path.join(outdir, f'gonogo_sub-{pid}_ses-{exp_info["Session"]}_{ts}.csv')

FIELDS  = ['participant', 'session', 'trial', 'trial_type', 'responded', 'rt_ms', 'outcome']

rt_clock = core.Clock()

# ── Helpers ───────────────────────────────────────────────────────────────────
def show_msg(text, wait_keys=('space',)):
    msg.text = text
    msg.draw()
    win.flip()
    event.waitKeys(keyList=list(wait_keys))

def show_instructions():
    elements = [
        # Title
        visual.TextStim(win,
            text='ZADANIE GO / NO-GO',
            font='Arial', height=0.065, bold=True,
            color='white', pos=(0, 0.32)),
        # Separator
        visual.Rect(win,
            width=0.72, height=0.003,
            fillColor='#606060', lineColor='#606060',
            pos=(0, 0.21)),
        # Go row — circle
        visual.Circle(win,
            radius=0.038, fillColor='#56B4E9', lineColor='#56B4E9',
            pos=(-0.42, 0.09)),
        # Go row — arrow
        visual.TextStim(win,
            text='→', font='Arial', height=0.042, color='#888888',
            pos=(-0.27, 0.09)),
        # Go row — label
        visual.TextStim(win,
            text='Naciśnij SPACJĘ jak najszybciej',
            font='Arial', height=0.038, color='white',
            pos=(0.07, 0.09), wrapWidth=0.70),
        # No-go row — circle
        visual.Circle(win,
            radius=0.038, fillColor='#E69F00', lineColor='#E69F00',
            pos=(-0.42, -0.06)),
        # No-go row — arrow
        visual.TextStim(win,
            text='→', font='Arial', height=0.042, color='#888888',
            pos=(-0.27, -0.06)),
        # No-go row — label
        visual.TextStim(win,
            text='NIE naciskaj nic',
            font='Arial', height=0.038, color='white',
            pos=(0.07, -0.06), wrapWidth=0.70),
        # Subtitle
        visual.TextStim(win,
            text='Reaguj szybko, ale staraj się nie popełniać błędów.',
            font='Arial', height=0.033, color='#999999',
            pos=(0, -0.23), wrapWidth=1.3),
        # Prompt
        visual.TextStim(win,
            text='[ Naciśnij SPACJĘ, aby rozpocząć ]',
            font='Arial', height=0.029, color='#666666',
            pos=(0, -0.38)),
    ]
    for el in elements:
        el.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

# ── Instructions ─────────────────────────────────────────────────────────────
show_instructions()

# ── Main loop ─────────────────────────────────────────────────────────────────
rows = []

for t, trial_type in enumerate(trials):

    if event.getKeys(['escape']):
        break

    # Fixation visible throughout ITI
    fixation.draw()
    win.flip()
    core.wait(random.uniform(ITI_MIN, ITI_MAX))

    # Pre-stimulus fixation
    fixation.draw()
    win.flip()
    core.wait(FIX_DUR)

    # Stimulus + response window
    stim = go_stim if trial_type == 'go' else nogo_stim
    event.clearEvents()
    stim.draw()
    win.flip()
    rt_clock.reset()

    keys = event.waitKeys(
        maxWait=STIM_DUR,
        keyList=['space', 'escape'],
        timeStamped=rt_clock
    )

    win.flip()  # clear stimulus immediately after response or timeout

    if keys and keys[0][0] == 'escape':
        break

    responded = bool(keys)
    rt_ms     = round(keys[0][1] * 1000, 1) if responded else None

    if trial_type == 'go':
        outcome = 'hit'          if responded else 'miss'
    else:
        outcome = 'false_alarm'  if responded else 'correct_rejection'

    rows.append({
        'participant': pid,
        'session':     exp_info['Session'],
        'trial':       t + 1,
        'trial_type':  trial_type,
        'responded':   int(responded),
        'rt_ms':       rt_ms if rt_ms is not None else '',
        'outcome':     outcome,
    })

# ── Save data ─────────────────────────────────────────────────────────────────
with open(outfile, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)

# ── End screen ────────────────────────────────────────────────────────────────
show_msg(f"Gotowe!\n\nDane zapisano do:\n{outfile}\n\n[SPACJA, aby zakończyć]")
win.close()
core.quit()
