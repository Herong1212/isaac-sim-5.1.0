"""
Create a table of contents file in index.rst that references all of the OmniGraph node generated
documentation files that live in that directory.

This processing is highly tied to the formatting of the OGN generated documentation files so if they
change this has to as well.

The table of contents will be in two sections.

    A table consisting of columns with [node name, node version, link to node doc file, link to node appendix entry]
    An appendix with headers consisting of the node name and body consisting of the node's description
"""

from _impl.node_generator import main_docs

main_docs.main_docs()
