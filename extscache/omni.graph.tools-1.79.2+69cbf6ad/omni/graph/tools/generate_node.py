"""Command line script to run the node generator scripts

Mainly a separate script to create a package for the node generator scripts so that the files can use shorter names
and relative imports. See node_generator/README.md for the usage information.
"""

from _impl.node_generator import main

main.main()
