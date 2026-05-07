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
fixation  = visual.TextStim(win, '+', height=0.06, color='white', font='Arial')
# Okabe-Ito colorblind-safe palette (Okabe & Ito, 2008)
go_stim   = visual.Circle(win, radius=0.12, fillColor='#56B4E9', lineColor='#56B4E9')  # sky blue
nogo_stim = visual.Circle(win, radius=0.12, fillColor='#E69F00', lineColor='#E69F00')  # orange
feedback  = visual.TextStim(win, '', height=0.06, bold=True, font='Arial')
msg       = visual.TextStim(win, '', height=0.042, wrapWidth=1.4, color='white', font='Arial')

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
            text='ĆWICZENIE',
            font='Arial', height=0.065, bold=True,
            color='white', pos=(0, 0.35)),
        # Separator
        visual.Rect(win,
            width=0.72, height=0.003,
            fillColor='#606060', lineColor='#606060',
            pos=(0, 0.24)),
        # Go row — circle
        visual.Circle(win,
            radius=0.038, fillColor='#56B4E9', lineColor='#56B4E9',
            pos=(-0.42, 0.12)),
        # Go row — arrow
        visual.TextStim(win,
            text='→', font='Arial', height=0.042, color='#888888',
            pos=(-0.27, 0.12)),
        # Go row — label
        visual.TextStim(win,
            text='Naciśnij SPACJĘ jak najszybciej',
            font='Arial', height=0.038, color='white',
            pos=(0.07, 0.12), wrapWidth=0.70),
        # No-go row — circle
        visual.Circle(win,
            radius=0.038, fillColor='#E69F00', lineColor='#E69F00',
            pos=(-0.42, -0.03)),
        # No-go row — arrow
        visual.TextStim(win,
            text='→', font='Arial', height=0.042, color='#888888',
            pos=(-0.27, -0.03)),
        # No-go row — label
        visual.TextStim(win,
            text='NIE naciskaj nic',
            font='Arial', height=0.038, color='white',
            pos=(0.07, -0.03), wrapWidth=0.70),
        # Feedback note
        visual.TextStim(win,
            text='Po każdej próbie otrzymasz informację zwrotną.\n'
                 'W głównym zadaniu nie będzie informacji zwrotnej.',
            font='Arial', height=0.033, color='#999999',
            pos=(0, -0.20), wrapWidth=1.3),
        # Prompt
        visual.TextStim(win,
            text='[ Naciśnij SPACJĘ, aby rozpocząć ćwiczenie ]',
            font='Arial', height=0.029, color='#666666',
            pos=(0, -0.38)),
    ]
    for el in elements:
        el.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

FEEDBACK_CFG = {
    'hit':               ('Dobrze!',       '#2ECC71'),
    'miss':              ('Za wolno!',      '#E67E22'),
    'false_alarm':       ('Nie naciskaj!',  '#E74C3C'),
    'correct_rejection': ('Dobrze!',        '#2ECC71'),
}

# ── Instructions ─────────────────────────────────────────────────────────────
show_instructions()

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
    f"Ćwiczenie zakończone!\n\n"
    f"Poprawne odpowiedzi: {n_correct} / {N_PRACTICE}\n\n"
    "Za chwilę rozpocznie się główne zadanie.\n"
    "Pamiętaj: nie będzie informacji zwrotnej.\n\n"
    "[Naciśnij SPACJĘ, aby kontynuować]"
)

win.close()
core.quit()
