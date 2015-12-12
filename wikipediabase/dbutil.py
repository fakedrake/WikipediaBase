import re

from peewee import DoesNotExist, IntegerField, Model, TextField
from playhouse.postgres_ext import PostgresqlExtDatabase, ServerSide
from playhouse.shortcuts import RetryOperationalError

from wikipediabase.util import encode

# -------
# Database connection
# -------


class PostgresqlExtRetryDatabase(RetryOperationalError, PostgresqlExtDatabase):

    """
    Automatically reconnect to the database and retry any queries that fail
    with an OperationalError
    """
    pass

db = PostgresqlExtRetryDatabase('wikipediabase', user='wikipediabase',
                                register_hstore=False)

# -------
# Models
# -------


class Article(Model):
    id = IntegerField(primary_key=True)
    title = TextField(index=True)
    markup = TextField()

    class Meta:
        database = db
        db_table = 'articles'

# -------
# Data access methods
# -------


def all_articles():
    """
    Returns an iterable of (page_id, title, markup)
    """
    db.connect()
    return ServerSide(Article.select().tuples())


def total_articles():
    """
    Returns the total number of articles
    """
    return Article.select().count()


def insert_article_batch(batch):
    db.connect()
    with db.atomic():
        Article.insert_many(batch).execute()
    db.close()


def get(symbol):
    """
    Gets an article from the backend
    Raises a LookupError if the symbol is not found in the DB
    """
    try:
        # TODO: remove when unicode issue in Allegro is fixed
        symbol = encode(symbol)

        db.connect()
        article = Article.get(Article.title == symbol)
        db.close()
        return article
    except DoesNotExist:
        db.close()
        raise LookupError("Error fetching: %s. Symbol not found in the db" %
                          (symbol))


def get_with_redirects(symbol):
    """
    Gets an article from the backend, following redirects
    Raises a LookupError if the symbol or any of its redirects are not found
    in the DB
    """
    article = get(symbol)
    redirect = extract_redirect(article.markup)

    while redirect is not None:
        article = get(redirect)
        redirect = extract_redirect(article.markup)
    return article


def get_markup(symbol):
    """
    Gets markup from the backend
    Raises a LookupError if the symbol is not found in the DB
    """
    return get_with_redirects(symbol).markup

# -------
# Markup utils
# -------

LINK_PATTERN = re.compile(r'\*+.*?\[\[(.*?)\]\]')
REDIRECT_PATTERN = re.compile(r"#REDIRECT:? ?\[\[(.*)?\]\]", flags=re.I)


def clean_symbol(symbol):
    symbol = unicode(symbol)
    symbol = symbol.replace(u'_', u' ')
    symbol = symbol.split(u'|')[0]
    symbol = symbol.split(u'#')[0]
    return symbol


def extract_redirect(markup):
    redirect_match = re.search(REDIRECT_PATTERN, markup)
    if redirect_match:
        r = redirect_match.group(1)
        return clean_symbol(r)
    return None


def is_disambiguation(title, markup):
    """
    Returns True if an article is a disambiguation page
    """
    if re.search(r'\(disamb\w+\)', title, flags=re.I):
        # disambiguation page specified in the title
        # e.g. "Anarchists (disambiguation)"
        return True

    # remove Template long comment
    # see https://en.wikipedia.org/wiki/Template:Long_comment
    long_comment = r"\{\{Short pages monitor\}\}\s*<!--.*?-->"
    markup = re.sub(long_comment, '', markup, flags=re.I | re.S).strip()

    # contains the {{disambiguation}} categories and sub-categories
    # e.g {{disambig}} or {{disambig|latin}}
    # see https://en.wikipedia.org/wiki/Template:Disambiguation for more info
    # the 250 character limit was chosen semi-arbitrarily to reduce false
    # positives. Some articles may contain a {{disambig|needed}} link in the
    # article text
    disambig = r'\{\{[\w\|\-= ]*(disamb|geodis|hndis|numberdis)[\w\|\-= ]*\}\}'
    if re.search(disambig, markup[-250:], flags=re.I):
        return True

    return False


def extract_disambiguation_links(markup):
    links = []

    # disambiguation pages may contain links to other articles under 'See also'
    markup = re.split('== *See +also *==', markup, flags=re.I)[0]

    for m in re.finditer(LINK_PATTERN, markup):
        link = m.group(1)
        link = clean_symbol(link)
        links.append(link)

    return links