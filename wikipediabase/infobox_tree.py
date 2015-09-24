import re
from itertools import chain

from wikipediabase.config import configuration, Configurable, LazyItem

class InfoboxSuperclasses(Configurable):
    """
    A dict-like map ibox-name -> [categories]. It retrieves the page at

    https://en.wikipedia.org/wiki/Wikipedia:List_of_infoboxes

    And generates a tree structure. The infobox type supercategores
    are the parents of the node's parsed tree.
    """

    def __init__(self, configuration=configuration):
        self.category_rx = configuration.ref.mediawiki.infobox_category_rx
        self.infobox_rxs = configuration.ref.mediawiki.infobox_infobox_rxs

        self.fetcher = configuration.ref.fetcher
        self.src = LazyItem(lambda:self.fetcher.source("Wikipedia:List_of_infoboxes"))

        # Poor person's lazy seq
        self.typedict = {}
        self.typeiter = self.type_tree()

    def type_tree(self):
        for key, val in self.category_header_infobox(self.src):
            self.typedict[key] = val
            yield key, val

    def __getitem__(self, key):
        if key in self.typedict:
            return self.typedict[key]

        while True:
            try:
                type_, parents_ = next(self.typeiter)
            except TypeError:
                break

            if type_ == key:
                return parents_

    def get_categories(self, source):
        """
        (category_name, category_source) pairs
        """
        return [(m.group(1), self.fetcher.source(m.group(1)))
                for m in re.finditer(r'$\s*{{.*}}', source, re.MULTILINE)]

    def header_levels(self, source):
        head_rx = re.finditer(r"^\s*(=+)([^=]+)(=+)\s*$", source, re.MULTILINE)
        heads = [(len(m.group(1)), m.group(2), (m.start(), m.end()))
                    for m in head_rx if m.group(1) == m.group(3)]
        return self.levels(heads, source)

    def header_lists(self, source):
        return self.lists(self.header_levels(source))

    def infobox_levels(self, source):
        list_rx = re.finditer(r"^\s*(\*+)\s*\[\[Template:Infobox (.+)\]\]",
                              source, re.MULTILINE)
        ibxs = [(len(m.group(1)), m.group(2), (m.start(), m.end()))
                    for m in list_rx]
        return ((lvl, name, name) for lvl, name, _ in self.levels(ibxs, source))

    def infobox_lists(self, source):
        ret = self.lists(self.infobox_levels(source))
        # Skip the space between the first item and top
        next(ret)
        return ret

    def category_header_infobox(self, source):
        for ch, ct in self.get_categories(source):
            for hhs, ht in self.header_lists(ct):
                for iht, ihs in self.infobox_lists(ht):
                    yield (ihs, list(set([ch] + hhs + iht)))

    def levels(self, items, source):
        """
        Given [(level, name, (start, end))] and source create
        [(level, name, data)]
        """
        before = (0, None, (0,0))
        after = (0, None, (len(source),len(source)))

        for cur, nxt in zip([before] + items, items + [after]):
            _, _, (end, _) = nxt
            level, title, (_, start) = cur
            yield level, title and title.strip(" "), \
                source[start: end].strip("[ \n]")

    def lists(self, levels):
        """
        Given the output ov levels produce
        [([headers], data)]
        """
        last_list = []
        for lvl, head, data in levels:
            prefix = last_list[:lvl-1] if lvl > 0 else []
            inter = [None] * (lvl - len(last_list) - 1)
            postfix = [head] if head else []
            last_list = prefix + inter + postfix
            yield last_list, data
