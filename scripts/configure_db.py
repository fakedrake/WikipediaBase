from wikipediabase.dbutil import Article, db

# TODO: check if mysql is running, create database

def create_tables():
    db.connect()
    Article.create_table(fail_silently=True)

if __name__ == '__main__':
    create_tables()
