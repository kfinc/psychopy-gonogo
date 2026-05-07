# psychopy-gonogo

A classical Go/No-Go task implemented in [PsychoPy](https://www.psychopy.org/), with colorblind-safe stimuli and a separate practice block.

## Task design

Participants see a coloured circle on each trial:

- **Sky blue circle (Go)** — press SPACE as quickly as possible
- **Orange circle (No-Go)** — withhold the response

The 75/25 Go/No-Go ratio creates a prepotent response tendency that the No-Go trials probe. This design choice is supported by Wessel (2018), who showed that fast-paced tasks with rare No-Go trials reliably evoke prepotent motor activity, while equiprobable or slow-paced variants reduce inhibition-related activity by ~75%.

### Parameters

| Parameter | Value |
|---|---|
| Total trials | 160 (120 Go, 40 No-Go) |
| Practice trials | 20 (with feedback) |
| Fixation duration | 500 ms |
| Stimulus + response window | 1000 ms |
| Inter-trial interval | 300–700 ms (jittered) |
| Response key | SPACE |
| Background | dark grey (`#404040`) |
| Stimulus colors | Okabe-Ito sky blue (`#56B4E9`) / orange (`#E69F00`) |

### Stimulus design rationale

The sky-blue / orange pair comes from the [Okabe-Ito colorblind-safe palette](https://jfly.uni-koeln.de/color/) (Okabe & Ito, 2008), which is distinguishable to people with deuteranopia and protanopia (the two most common forms of color vision deficiency).

## Files

- `gonogo_practice.py` — 20-trial practice block with trial-by-trial feedback
- `gonogo_task.py` — 160-trial main task, no feedback, saves data to `data/`

## Requirements

- Python 3.8+
- PsychoPy 2024.1+

Install with:

```bash
pip install -r requirements.txt
```

## Running

Recommended order:

```bash
python gonogo_practice.py    # familiarisation, no data saved
python gonogo_task.py        # main task, data saved to data/
```

Both scripts can also be opened in PsychoPy Coder and run with the green ▶ button.

A dialog will prompt for participant ID, session number, age, and gender.

## Output

Data is saved to `data/gonogo_sub-<ID>_ses-<N>_<timestamp>.csv` with columns:

| Column | Description |
|---|---|
| `participant`, `session`, `age`, `gender` | Demographics from dialog |
| `trial` | Trial number (1-indexed) |
| `trial_type` | `go` or `nogo` |
| `responded` | 1 if SPACE pressed, 0 otherwise |
| `rt_ms` | Reaction time in milliseconds (blank if no response) |
| `outcome` | `hit`, `miss`, `false_alarm`, or `correct_rejection` |

### Standard derived measures

- **Hit rate** = hits / (hits + misses)
- **False alarm rate** = false_alarms / (false_alarms + correct_rejections)
- **d′** = z(hit rate) − z(false alarm rate) — sensitivity (signal detection)
- **Mean RT** on hits only — typically the primary speed measure

## Citation

If you use this implementation in published work, please cite:

> Finc, K. (2026). *psychopy-gonogo: A classical Go/No-Go task in PsychoPy*. GitHub. https://github.com/<your-username>/psychopy-gonogo

### Key references for the design

- **Go/No-Go paradigm**: Garavan, H., Ross, T. J., & Stein, E. A. (1999). Right hemispheric dominance of inhibitory control: An event-related functional MRI study. *PNAS, 96*(14), 8301–8306.
- **75/25 ratio rationale**: Wessel, J. R. (2018). Prepotent motor activity and inhibitory control demands in different variants of the go/no-go paradigm. *Psychophysiology, 55*(3), e12871.
- **fMRI meta-analysis**: Simmonds, D. J., Pekar, J. J., & Mostofsky, S. H. (2008). Meta-analysis of Go/No-go tasks demonstrating that fMRI activation associated with response inhibition is task-dependent. *Neuropsychologia, 46*(1), 224–232.
- **Colorblind-safe palette**: Okabe, M., & Ito, K. (2008). Color Universal Design (CUD): How to make figures and presentations that are friendly to colorblind people.

## License

MIT — see [LICENSE](LICENSE).
