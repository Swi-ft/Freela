import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'freela.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('client', 'freelancer')),
            full_name TEXT NOT NULL,
            avatar_initials TEXT,
            
            -- Freelancer private reputation profile (for demonstration & credential issuance)
            rating_score REAL DEFAULT 4.9,        -- e.g. 4.9 (out of 5.0)
            completed_jobs INTEGER DEFAULT 35,    -- e.g. 35 completed jobs
            on_time_rate INTEGER DEFAULT 98,      -- e.g. 98%
            dispute_count INTEGER DEFAULT 0,      -- e.g. 0 disputes
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            icon TEXT NOT NULL
        )
    ''')

    # Jobs / Gigs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            budget REAL NOT NULL,
            delivery_days INTEGER DEFAULT 7,
            
            -- ZK Eligibility Criteria (Public inputs for the circuit)
            min_rating REAL DEFAULT 4.5,            -- minimum rating required (scaled in circuit)
            min_completed_jobs INTEGER DEFAULT 10,  -- minimum jobs completed
            min_on_time_rate INTEGER DEFAULT 90,    -- minimum % on-time
            max_disputes INTEGER DEFAULT 1,         -- maximum allowable disputes
            
            status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'completed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES users(id)
        )
    ''')

    # Applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            freelancer_id INTEGER NOT NULL,
            cover_note TEXT,
            bid_amount REAL,
            
            -- ZK Proof Verification info
            proof_verified INTEGER DEFAULT 0,       -- 1 if valid ZK proof submitted
            zk_proof_hex TEXT,                      -- Proof bytes / string
            zk_public_inputs TEXT,                  -- JSON string of public inputs
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (freelancer_id) REFERENCES users(id)
        )
    ''')

    # Seed categories
    categories = [
        ('Web Development', 'code'),
        ('Design & Graphics', 'palette'),
        ('Writing & Content', 'file-text'),
        ('Data & Analytics', 'bar-chart'),
        ('Business', 'briefcase'),
        ('Others', 'more-horizontal')
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO categories (name, icon) VALUES (?, ?)
    ''', categories)

    # Seed users if empty
    cursor.execute('SELECT COUNT(*) as count FROM users')
    if cursor.fetchone()['count'] == 0:
        # Default mock users (password: 'password123' hashed with simple SHA-256 for easy review/test)
        import hashlib
        pwd_hash = hashlib.sha256('password123'.encode('utf-8')).hexdigest()
        
        users_seed = [
            # Clients
            ('client_alice', 'alice@freela.io', pwd_hash, 'client', 'Alice Morgan', 'AM', 0, 0, 0, 0),
            ('client_techcorp', 'tech@corp.io', pwd_hash, 'client', 'Nexus Global Tech', 'NT', 0, 0, 0, 0),
            
            # Freelancers with private stats
            ('alex_dev', 'alex@freela.io', pwd_hash, 'freelancer', 'Alex Rivera', 'AR', 4.9, 120, 99, 0),
            ('sara_design', 'sara@freela.io', pwd_hash, 'freelancer', 'Sara Chen', 'SC', 4.8, 95, 96, 1),
            ('john_writer', 'john@freela.io', pwd_hash, 'freelancer', 'John Miller', 'JM', 4.9, 210, 97, 0),
            ('data_guru', 'guru@freela.io', pwd_hash, 'freelancer', 'Devin Vance', 'DV', 4.8, 75, 94, 1),
            ('elena_ui', 'elena@freela.io', pwd_hash, 'freelancer', 'Elena Rostova', 'ER', 4.95, 88, 100, 0)
        ]
        
        cursor.executemany('''
            INSERT INTO users (username, email, password_hash, role, full_name, avatar_initials, rating_score, completed_jobs, on_time_rate, dispute_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', users_seed)

    # Seed initial jobs if empty
    cursor.execute('SELECT COUNT(*) as count FROM jobs')
    if cursor.fetchone()['count'] == 0:
        jobs_seed = [
            (
                1, # client Alice
                'Build a modern responsive website',
                'Web Development',
                'Looking for an expert full-stack developer to build a modern, high-converting landing page and dashboard using HTML5/CSS and modern APIs. Must deliver clean code and responsive layouts.',
                850.0,
                5,
                4.8, # min rating
                25,  # min completed jobs
                95,  # min 95% on-time
                1    # max 1 dispute
            ),
            (
                1,
                'Create a clean and modern brand identity',
                'Design & Graphics',
                'We need a complete brand identity package including primary and secondary logo variants, color palette, typography hierarchy, and a 12-page brand guideline manual.',
                650.0,
                7,
                4.7,
                15,
                90,
                2
            ),
            (
                2, # client TechCorp
                'Write SEO-optimized blog posts for AI SaaS',
                'Writing & Content',
                'Seeking an experienced technical content strategist to write 4 comprehensive, research-backed articles on applied cryptography and zero-knowledge privacy.',
                400.0,
                4,
                4.8,
                20,
                92,
                0
            ),
            (
                2,
                'Data analysis and interactive visualization dashboard',
                'Data & Analytics',
                'Transform large-scale user metrics into clean, interactive analytics dashboards. Requires experience in metric modeling, chart representations, and SQLite integration.',
                950.0,
                10,
                4.8,
                30,
                95,
                1
            ),
            (
                1,
                'SaaS Landing page UI/UX wireframes and prototype',
                'Design & Graphics',
                'Design modern dark and light mode UI screens with sleek glassmorphic aesthetics for a privacy-first web3 productivity suite.',
                500.0,
                6,
                4.6,
                10,
                88,
                2
            ),
            (
                2,
                'Python REST API optimization and database indexing',
                'Web Development',
                'Audit, profile, and optimize an existing SQLite / PostgreSQL database and Flask backend API to handle high concurrency with sub-100ms response times.',
                720.0,
                4,
                4.8,
                35,
                96,
                0
            )
        ]
        
        cursor.executemany('''
            INSERT INTO jobs (client_id, title, category, description, budget, delivery_days, min_rating, min_completed_jobs, min_on_time_rate, max_disputes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', jobs_seed)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at:", DB_PATH)
