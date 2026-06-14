import aiosqlite

DB = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            type TEXT,
            file_id TEXT,
            text TEXT
        )
        """)

        await db.commit()

# USERS
async def add_user(user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        await db.commit()

async def get_users():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT id FROM users")
        return await cur.fetchall()

# CODES
async def add_code(code, type_, file_id=None, text=None):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO codes (code, type, file_id, text) VALUES (?, ?, ?, ?)",
            (code, type_, file_id, text)
        )
        await db.commit()

async def get_codes():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT id, code, type FROM codes")
        return await cur.fetchall()

async def get_code_by_text(code):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT * FROM codes WHERE code=?", (code,))
        return await cur.fetchone()

# 🗑 DELETE CODE
async def delete_code(code_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM codes WHERE id=?", (code_id,))
        await db.commit()