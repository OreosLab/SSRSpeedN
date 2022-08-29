import pstats
from pstats import SortKey

from tests import root

root()

p = pstats.Stats("data/restats")

p.sort_stats(SortKey.CUMULATIVE).print_stats(30)
