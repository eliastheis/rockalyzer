# Rockalyzer: Rocket League Boxcars-Replay Analyzer

[![Version](https://img.shields.io/pypi/v/rockalyzer)](https://pypi.org/project/rockalyzer/#history)
[![Downloads](https://static.pepy.tech/personalized-badge/rockalyzer?period=total&units=international_system&left_color=black&right_color=blue&left_text=Total+Downloads)](https://pepy.tech/project/rockalyzer)
[![Downloads](https://static.pepy.tech/personalized-badge/rockalyzer?period=week&units=international_system&left_color=black&right_color=blue&left_text=Downloads/Week)](https://pepy.tech/project/rockalyzer)

# Features
- Replay and analyze Rocket League [Boxcars](https://github.com/nickbabcock/boxcars) replays (you can use [rrrocket](https://github.com/nickbabcock/rrrocket) or [boxcars-py](https://github.com/SaltieRL/boxcars-py) to parse a `.replay`-file into a useable `.json`-file)
- Extract **general** info
  - game playlist (`casual_duel`, `ranked_double`, ...)
  - date and time
  - replay-name and unique replay-id
  - map-name
- Extract info about **players**
  - name, scores, goals, saves, assists, shots
  - platform (`Steam`, `PlayStation`, `PsyNet`, and `Xbox`) and unique platform_id
  - MMR, if available (using [BakkesMod](https://bakkesmod.com/index.php))
  - title
  - ping (including min, max, and average)
- Extract info about **goals**
  - when, where, who
  - ball speed (in km/h)
- Extract some debug stuff like
  - complete history of player and ball positions
  - complete history of some more abstract values (see `stats['debug']`)
- And more. Feel free to explore it!

## Installation
Run the following to install:
```python
pip install rockalyzer
```

## Usage
Make sure you parsed the replay to a json file first using one of the tools mentioned above.
```python
from rockalyzer import Replayer

# load replay as JSON file and set render mode
replayer = Replayer('path/to/replay.json', render=True)

# print header infos
replayer.print_header_info()

# replay file
stats = replayer.replay()
```

### Simple render
If you set `render=True` when creating the `Replayer`-object, you get a simple (almost real-time) render of the game using [matplotlib](https://matplotlib.org/)
![Screenshot of render](https://raw.githubusercontent.com/eliastheis/rockalyzer/master/render_screenshot.png)

## Build and upload package to PyPi
```python
python ./setup.py bdist_wheel sdist
python -m twine upload dist/*
```
