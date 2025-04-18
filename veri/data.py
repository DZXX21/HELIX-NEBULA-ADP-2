import os
import mysql.connector
from mysql.connector import Error

# ——————— Veritabanı Konfigürasyonu ———————
db_config = {
    'host':     '127.0.0.1',
    'port':     3307,
    'user':     'root',
    'password': 'my-secret-pw',
    'database': 'testdb',
    'autocommit': False,
}

def ensure_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dosyalar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            dosya_adi VARCHAR(255) UNIQUE,
            icerik LONGBLOB
        )
    """)

def insert_file(cursor, filename, filepath):
    """Tek bir dosyayı okuyup INSERT IGNORE ile veritabanına ekler."""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        cursor.execute(
            "INSERT IGNORE INTO dosyalar (dosya_adi, icerik) VALUES (%s, %s)",
            (filename, content)
        )

        if cursor.rowcount:
            print(f"✅ '{filename}' eklendi ({len(content)} bytes).")
            return True
        else:
            print(f"⚠️ '{filename}' zaten var, atlandı.")
            return False

    except Error as err:
        print(f"❌ '{filename}' eklenirken MySQL hatası: {err}")
        return False
    except Exception as ex:
        print(f"❌ '{filename}' okunurken beklenmeyen hata: {ex}")
        return False

def insert_all_txt_files(directory_path):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        ensure_table(cursor)
        print("🔧 Tablo hazır.")

        txt_files = [entry for entry in os.scandir(directory_path) if entry.is_file() and entry.name.lower().endswith('.txt')]

        if not txt_files:
            print("📭 Hiç .txt dosyası bulunamadı.")
            return

        for entry in txt_files:
            filename = entry.name
            filepath = entry.path

            if insert_file(cursor, filename, filepath):
                conn.commit()
                try:
                    os.remove(filepath)
                    print(f"🗑️ '{filename}' silindi.")
                except Exception as rm_err:
                    print(f"⚠️ '{filename}' silinirken hata: {rm_err}")
            else:
                conn.rollback()

        print("🎉 Tüm işlemler tamamlandı.")

    except Error as e:
        print("❌ Genel MySQL bağlantı hatası:", e)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    klasor_yolu = "/home/dzx/Belgeler/GitHub/HELIX-NEBULA-ADP-2/veri"
    insert_all_txt_files(klasor_yolu)
