import sqlite3
import json
import uuid

# Connect to the database
conn = sqlite3.connect('session.db')
cursor = conn.cursor()

# Create sessions table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        app_name TEXT,
        user_id TEXT,
        session_id TEXT,
        state TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create initial state dictionary with all norm weights
initial_state = {
    # China norms
    "China_norm_multilateral_cooperation": -0.2,
    "China_norm_sovereignty_as_responsibility": -0.8,
    "China_norm_human_rights_universalism": -0.6,
    "China_norm_diplomatic_engagement": 0.3,
    "China_norm_norm_entrepreneurship": -0.5,
    "China_norm_peaceful_dispute_resolution": 0.0,
    "China_norm_diffuse_reciprocity": 0.4,
    "China_norm_collective_identity_formation": -0.3,
    "China_norm_legitimacy_through_consensus": -0.4,
    "China_norm_transparency_accountability": -0.5,
    
    # USA norms
    "USA_norm_multilateral_cooperation": 0.5,
    "USA_norm_sovereignty_as_responsibility": 0.6,
    "USA_norm_human_rights_universalism": 0.8,
    "USA_norm_diplomatic_engagement": 0.4,
    "USA_norm_norm_entrepreneurship": 0.7,
    "USA_norm_peaceful_dispute_resolution": 0.5,
    "USA_norm_diffuse_reciprocity": 0.3,
    "USA_norm_collective_identity_formation": 0.7,
    "USA_norm_legitimacy_through_consensus": 0.4,
    "USA_norm_transparency_accountability": 0.6,
    
    # Russia norms
    "Russia_norm_multilateral_cooperation": -0.3,
    "Russia_norm_sovereignty_as_responsibility": -0.9,
    "Russia_norm_human_rights_universalism": -0.7,
    "Russia_norm_diplomatic_engagement": 0.2,
    "Russia_norm_norm_entrepreneurship": -0.4,
    "Russia_norm_peaceful_dispute_resolution": -0.2,
    "Russia_norm_diffuse_reciprocity": 0.1,
    "Russia_norm_collective_identity_formation": -0.6,
    "Russia_norm_legitimacy_through_consensus": -0.5,
    "Russia_norm_transparency_accountability": -0.8,
    
    # EU norms
    "EU_norm_multilateral_cooperation": 0.9,
    "EU_norm_sovereignty_as_responsibility": 0.7,
    "EU_norm_human_rights_universalism": 0.8,
    "EU_norm_diplomatic_engagement": 0.7,
    "EU_norm_norm_entrepreneurship": 0.8,
    "EU_norm_peaceful_dispute_resolution": 0.9,
    "EU_norm_diffuse_reciprocity": 0.8,
    "EU_norm_collective_identity_formation": 0.9,
    "EU_norm_legitimacy_through_consensus": 0.8,
    "EU_norm_transparency_accountability": 0.7,
}

# Update existing sessions with the state
cursor.execute("""
    UPDATE sessions 
    SET state = ?
    WHERE state IS NULL OR state = '{}'
""", (json.dumps(initial_state),))

# If no sessions exist, create one
cursor.execute("SELECT COUNT(*) FROM sessions")
if cursor.fetchone()[0] == 0:
    session_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO sessions (id, app_name, user_id, session_id, state)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, "international_system", "user1", session_id, json.dumps(initial_state)))

conn.commit()
conn.close()

print("Session database initialized with initial state!")
print(f"Initial state keys: {len(initial_state)}")