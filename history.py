from database import get_connection

def save_analysis_history(user_id, job_url, job_title, score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (user_id, job_url, job_title, ats_score)
        VALUES (?, ?, ?, ?)
    ''', (user_id, job_url, job_title, score))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT job_url, job_title, ats_score, created_at 
        FROM history 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        LIMIT 10
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
