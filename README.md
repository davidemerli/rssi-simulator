# RSSI Simulator

## Demo



## Legend

### Circles

![#f03c15](https://via.placeholder.com/15/1c20ff/000000?text=+) Blue: represent antennas which signal is actually received (i.e. not lost) at a given time

![#f03c15](https://via.placeholder.com/15/ffff00/000000?text=+) Yellow: represents the estimated point using all data from the antennas

![#f03c15](https://via.placeholder.com/15/78e8ff/000000?text=+) Light Blue: represents the estimated location using median on the last SIM_WINDOW simulations (last SIM_WINDOW yellow circles)

![#f03c15](https://via.placeholder.com/15/ff991c/000000?text=+) Orange: shown on the antenna that gives the strongest signal at a given instance of the simulation

### Blocks
<img src="legend.png " width="400">

## Settings

All settings are stored in ```settings.json```

| setting            | description                                                         | default value |
|--------------------|---------------------------------------------------------------------|---------------|
| TRASMITTED_POWER   | Power transmitted by the beacon                                     | -4 (dBm)      |
| COUPLING_FACTOR    | value of free path loss calculations given by the antenna coupling  | 1 dB          |
| WAVE_FACTOR        | wave factor contribution                                            | 40            |
| PATH_LOSS_PERIM    | Wall path loss in dB from perimetral walls (thicker)                | -14 (dB)      |
| PATH_LOSS_INTERNAL | Wall path loss in dB from internal walls (thinner)                  | -3 (dB)       |
| NOISE              | Noise value constraints applied on exponential distribution         | [-30, 0] (dB) |
| THRESHOLD          | when an antenna is considered too far away and is therefore ignored | -95 (dB)      |
| PACKET_LOSS        | Probability to lose an antenna measurement at a given time          | 0.1 (10%)     |
| DELAY              | Delay between simulations                                           | 0.3 (seconds) |
| SIM_WINDOW         | Number of simulations required to estimate the median coordinates   | 5             |
