from wikipediabase.util import get_article


def sort_by_length(*args):
    key = lambda a: len(' '.join(get_article(a).paragraphs()))
    return sorted(args, reverse=True, key=key)


def sort_named(named, *args):
    # TODO: clean up, this was directly translated from Ruby WikipediaBase
    article_lengths = {}
    for a in args:
        try:
            article_lengths[a] = len(' '.join(get_article(a).paragraphs()))
        except LookupError:
            pass
    
    def compare(a, b):
        named_eq = lambda x: x == named
        named_ieq = lambda x: x.lower() == named.lower()

        if named_eq(a) != named_eq(b):
            return -1 if named_eq(a) else 1
        elif named_ieq(a) != named_ieq(b):
            return -1 if named_ieq(a) else 1
        else:
            len_a = article_lengths[a]
            len_b = article_lengths[b]
            if len_a < len_b: return -1
            elif len_a == len_b: return 0
            elif len_a > len_b: return 1

    return sorted(article_lengths.keys(), cmp=compare)
