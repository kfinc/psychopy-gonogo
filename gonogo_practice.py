#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Go/No-Go — Practice Block
--------------------------
20 trials (75% Go / 25% No-Go) with trial-by-trial feedback.
Run this before gonogo_task.py.
No data saved.
"""

from psychopy import visual, core, event, gui
import random

# ── Participant info (minimal — just to match main task flow) ────────────────
exp_info = {'Participant ID': ''}
dlg = gui.DlgFromDict(exp_info, title='Go/No-Go Practice')
if not dlg.OK:
    core.quit()

# ── Window & stimuli ─────────────────────────────────────────────────────────
win       = visual.Window(fullscr=True, color='#404040', units='height')
fixation  = visual.TextStim(win, '+', height=0.06, color='white')
# Okabe-Ito colorblind-safe palette (Okabe & Ito, 2008)
go_stim   = visual.Circle(win, radius=0.12, fillColor='#56B4E9', lineColor='#56B4E9')  # sky blue
nogo_stim = visual.Circle(win, radius=0.12, fillColor='#E69F00', lineColor='#E69F00')  # orange
feedback  = visual.TextStim(win, '', height=0.06, bold=True)
msg       = visual.TextStim(win, '', height=0.04, wrapWidth=1.6, color='white')

# ── Timing (seconds) ─────────────────────────────────────────────────────────
FIX_DUR      = 0.500
STIM_DUR     = 1.000
FEEDBACK_DUR = 0.600
ITI_MIN      = 0.300
ITI_MAX      = 0.700

# ── Trial list ───────────────────────────────────────────────────────────────
N_PRACTICE = 20
n_go       = int(N_PRACTICE * 0.75)   # 15 Go, 5 No-Go
trials     = ['go'] * n_go + ['nogo'] * (N_PRACTICE - n_go)
random.shuffle(trials)

rt_clock = core.Clock()

# ── Helper ───────────────────────────────────────────────────────────────────
def show_msg(text, wait_keys=('space',)):
    msg.text = text
    msg.draw()
    win.flip()
    event.waitKeys(keyList=list(wait_keys))

FEEDBACK_CFG = {
    'hit':               ('Correct!',       '#2ECC71'),
    'miss':              ('Too slow!',       '#E67E22'),
    'false_alarm':       ('Oops — no press!','#E74C3C'),
    'correct_rejection': ('Correct!',        '#2ECC71'),
}

# ── Instructions ─────────────────────────────────────────────────────────────
show_msg(
    "PRACTICE\n\n"
    "BLUE circle    →  Press SPACE as quickly as you can\n"
    "ORANGE circle  →  Do NOT press anything\n\n"
    "You will receive feedback after each trial.\n"
    "The real task has no feedback.\n\n"
    "[Press SPACE to begin practice]"
)

# ── Practice loop ─────────────────────────────────────────────────────────────
n_correct = 0

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

    win.flip()

    if keys and keys[0][0] == 'escape':
        break

    responded = bool(keys)

    if trial_type == 'go':
        outcome = 'hit'          if responded else 'miss'
    else:
        outcome = 'false_alarm'  if responded else 'correct_rejection'

    if outcome in ('hit', 'correct_rejection'):
        n_correct += 1

    # Feedback
    label, colour = FEEDBACK_CFG[outcome]
    feedback.text  = label
    feedback.color = colour
    feedback.draw()
    win.flip()
    core.wait(FEEDBACK_DUR)

# ── Summary ───────────────────────────────────────────────────────────────────
show_msg(
    f"Practice complete!\n\n"
    f"You got {n_correct} / {N_PRACTICE} correct.\n\n"
    "The real task will now begin.\n"
    "Remember: no feedback will be shown.\n\n"
    "[Press SPACE to continue]"
)

win.close()
core.quit()
