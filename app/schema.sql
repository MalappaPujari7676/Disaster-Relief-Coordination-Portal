DROP TABLE IF EXISTS assignments_log;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS help_requests;
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS volunteers;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'citizen'
        CHECK (role IN ('admin','coordinator','volunteer','citizen')),
    phone TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    skills TEXT,
    location TEXT,
    available INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    severity INTEGER NOT NULL DEFAULT 1 CHECK (severity BETWEEN 1 AND 5),
    location TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','contained','resolved')),
    created_by INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE help_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE SET NULL,
    requester_name TEXT NOT NULL,
    contact TEXT NOT NULL,
    need_type TEXT NOT NULL,
    description TEXT,
    urgency TEXT NOT NULL DEFAULT 'medium' CHECK (urgency IN ('low','medium','high','critical')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','assigned','fulfilled','cancelled')),
    assigned_to INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    unit TEXT NOT NULL DEFAULT 'units',
    location TEXT,
    low_threshold INTEGER NOT NULL DEFAULT 10,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
