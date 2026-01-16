from .cycle_motif_generator import CycleMotifGenerator
from .house_motif_generator import HouseMotifGenerator
from .chain_motif_generator import ChainMotifGenerator
from .star_motif_generator import StarMotifGenerator
from .gate_motif_generator import GateMotifGenerator

__all__ = ['CycleMotifGenerator', 'HouseMotifGenerator', 'ChainMotifGenerator', 'StarMotifGenerator', 'GateMotifGenerator']

motif_generators = {
    "cycle": CycleMotifGenerator,
    "house": HouseMotifGenerator,
    "chain": ChainMotifGenerator,
    "star": StarMotifGenerator,
    "gate": GateMotifGenerator,
}