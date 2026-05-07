#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classical Go/No-Go Task
-----------------------
Go  (GREEN circle): press SPACE as fast as possible
No-Go (RED circle): withhold response

Outputs: data/gonogo_sub-<ID>_ses-<N>_<timestamp>.csv
"""

from psychopy import visual, core, event, gui
import random, os, csv
from datetime import datetime

# ── Participant info ─────────────────────────────────────────────────────────
exp_info = {'Participant ID': '', 'Session': '1', 'Age': '', 'Gender': ''}
dlg = gui.DlgFromDict(
    exp_info, title='Go/No-Go Task',
    order=['Participant ID', 'Session', 'Age', 'Gender']
)
if not dlg.OK:
    core.quit()

# ── Window & stimuli ─────────────────────────────────────────────────────────
win       = visual.Window(fullscr=True, color='#404040', units='height')
fixation  = visual.TextStim(win, '+', height=0.06, color='white')
# Okabe-Ito colorblind-safe palette (Okabe & Ito, 2008)
go_stim   = visual.Circle(win, radius=0.12, fillColor='#56B4E9', lineColor='#56B4E9')  # sky blue
nogo_stim = visual.Circle(win, radius=0.12, fillColor='#E69F00', lineColor='#E69F00')  # orange
msg       = visual.TextStim(win, '', height=0.04, wrapWidth=1.6, color='white')

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

FIELDS  = ['participant', 'session', 'age', 'gender',
           'trial', 'trial_type', 'responded', 'rt_ms', 'outcome']

rt_clock = core.Clock()

# ── Helper ───────────────────────────────────────────────────────────────────
def show_msg(text, wait_keys=('space',)):
    msg.text = text
    msg.draw()
    win.flip()
    event.waitKeys(keyList=list(wait_keys))

# ── Instructions ─────────────────────────────────────────────────────────────
show_msg(
    "GO / NO-GO TASK\n\n"
    "BLUE circle    →  Press SPACE as quickly as you can\n"
    "ORANGE circle  →  Do NOT press anything\n\n"
    "Respond quickly, but try to avoid mistakes.\n\n"
    "[Press SPACE to begin]"
)

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
        'age':         exp_info['Age'],
        'gender':      exp_info['Gender'],
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
show_msg(f"All done!\n\nData saved to:\n{outfile}\n\n[SPACE to exit]")
win.close()
core.quit()
