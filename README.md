# Rocket League Boxcars-Replay Analyzer
Here will be the documentation

[![Downloads](https://static.pepy.tech/personalized-badge/rockalyzer?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/rockalyzer)

## Installation
Run the following to install:
```python
pip install rockalyzer
```

## Usage
```python
from rockalyzer import Replayer

# load replay as json file and set render mode
replayer = Replayer('path/to/replay.json', render=True)

# replay file
replayer.replay()

# get stats
stats = replayer.get_stats()
```
