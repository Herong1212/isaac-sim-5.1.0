"""For internal use - so that autonode_generator and node_generator can share imports"""

from .node_generator import ThreadsafeOpen

__all__ = ["ThreadsafeOpen"]
