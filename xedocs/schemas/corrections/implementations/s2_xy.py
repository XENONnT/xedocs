"""
# S2(x,y) correction codes
**Jianyu Long (jylong@uchicago.edu)**

```python
__version__='4.1.0'
```

Position dependent electron extraction efficiency, secondary scintillation gain and light detection efficiency, S2 signals in LXeTPC has a large position dependence. In order to make a precise energy reconstruction, we need a “correction” map to overcome its spatial dependence. This usually requires a selection of S2s originated from the same number of electrons, and then derive its average value.

See [description in the Team C overview page](https://xe1t-wiki.lngs.infn.it/doku.php?id=xenon:xenonnt:analysis:reconstruction_team#s2_x_y_correction)

## Brief info

- The map is created based on a crude Kr selection by default, if you want to investigate more monoenergetic sources, follow the instruction below
- The script contains a Cartesian map and a Polar map. They are independent from the other. You can inherite from either one for your purpose.
- To use, you must have an output from straxen/event_info about electron lifetime correction coefficient (it is used in .do_elifetime_correct)


"""

from ..base_references import BaseMap


class S2XYMap(BaseMap):
    _ALIAS = "s2_xy_maps"
