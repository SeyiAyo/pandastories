from django.core.management.base import BaseCommand
from blog.models import Post
from django.db import connection

class Command(BaseCommand):
    help = 'Fix author field in Post model'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # Get the current table structure
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='blog_post';")
                current_table = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'Current table structure:\n{current_table}'))
                
                # Turn off foreign key constraints
                cursor.execute("PRAGMA foreign_keys=off;")
                
                # Create new table
                cursor.execute("""
                    CREATE TABLE blog_post_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(255) NOT NULL,
                        slug VARCHAR(50) NOT NULL UNIQUE,
                        category_id INTEGER NOT NULL REFERENCES blog_category(id),
                        author VARCHAR(255) NOT NULL,
                        intro TEXT NULL,
                        content TEXT NULL,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        featured BOOL NOT NULL,
                        image VARCHAR(100) NULL,
                        meta_description VARCHAR(160) NULL
                    );
                """)
                
                # Copy data
                cursor.execute("""
                    INSERT INTO blog_post_new 
                    SELECT id, title, slug, category_id, author, intro, content, 
                           created_at, updated_at, status, featured, image,
                           meta_description
                    FROM blog_post;
                """)
                
                # Drop old table
                cursor.execute("DROP TABLE blog_post;")
                
                # Rename new table
                cursor.execute("ALTER TABLE blog_post_new RENAME TO blog_post;")
                
                # Turn on foreign key constraints
                cursor.execute("PRAGMA foreign_keys=on;")
                
                self.stdout.write(self.style.SUCCESS('Successfully fixed the author field'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                raise e
