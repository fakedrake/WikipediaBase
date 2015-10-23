import re

from peewee import CharField, IntegerField, Model, MySQLDatabase, TextField

db = MySQLDatabase('wikipediabase', user='root')


class Article(Model):
    id = IntegerField(primary_key=True)
    title = CharField(index=True)
    markup = TextField()

    class Meta:
        database = db
        db_table = 'articles'

IGNORE_PATTERNS = (
    re.compile(r"^:?image:", flags=re.I),
    re.compile(r"^:?file:", flags=re.I),
    re.compile(r"^:?TimedText:", flags=re.I),
    re.compile(r"^:?wikipedia:", flags=re.I),
    re.compile(r"^:?wiktionary:", flags=re.I),
    re.compile(r"^:?meta:", flags=re.I),
    re.compile(r"^:?category:", flags=re.I),
    re.compile(r"^:?portal:", flags=re.I),
    re.compile(r"^:?help:", flags=re.I),
    re.compile(r"^:?user:", flags=re.I),
    re.compile(r"^:?talk:", flags=re.I),
    re.compile(r"^:?media:", flags=re.I),
    re.compile(r"^:?mediawiki:", flags=re.I),
    re.compile(r"^:?template:", flags=re.I),
    re.compile(r"^:?book:", flags=re.I),
    re.compile(r"^:?List of", flags=re.I),
    re.compile(r"^:?Lists of", flags=re.I),
    re.compile(r"^:?Arbitration in ", flags=re.I),
    re.compile(r"^:?Communications in ", flags=re.I),
    re.compile(r"^:?Constitutional history of ", flags=re.I),
    re.compile(r"^:?Economy of ", flags=re.I),
    re.compile(r"^:?Demographics of ", flags=re.I),
    re.compile(r"^:?Foreign relations of ", flags=re.I),
    re.compile(r"^:?Geography of ", flags=re.I),
    re.compile(r"^:?History of ", flags=re.I),
    re.compile(r"^:?Military of ", flags=re.I),
    re.compile(r"^:?Politics of ", flags=re.I),
    re.compile(r"^:?Transport in ", flags=re.I),
    re.compile(r"^:?Transportation in ", flags=re.I),
    re.compile(r"^:?Outline of ", flags=re.I),
    re.compile(r" in \d\d\d\d$", flags=re.I),
    re.compile(r"^\d\d\d\d in ", flags=re.I),
    re.compile(r"\(disamb", flags=re.I),
    re.compile(r"#", flags=re.I),
)

REDIRECT_PATTERN = re.compile(r"<text.*?>\w*#REDIRECT:? ?\[\[(.*)?\]\]",
                              flags=re.I)


def is_good_title(title):
    for p in IGNORE_PATTERNS:
        if re.search(p, title):
            return False
    return True


def is_redirect(title):
    return re.search(REDIRECT_PATTERN, title) is not None
