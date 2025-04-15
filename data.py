import mysql.connector
import os

db_config = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'my-secret-pw',
    'database': 'testdb'
}

def insert_file_to_db(file_path):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dosyalar (
                id INT AUTO_INCREMENT PRIMARY KEY,
                dosya_adi VARCHAR(255),
                icerik LONGBLOB
            )
        """)

        dosya_adi = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            dosya_icerik = f.read()

        cursor.execute("INSERT INTO dosyalar (dosya_adi, icerik) VALUES (%s, %s)", (dosya_adi, dosya_icerik))
        conn.commit()

        print(f"✅ '{dosya_adi}' veritabanına başarıyla yüklendi.")

    except Exception as e:
        print("❌ Hata oluştu:", e)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    insert_file_to_db("veriler.txt")  # Buraya hangi dosyayı atmak istiyorsan onu yaz
