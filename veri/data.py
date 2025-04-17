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
    with open(filepath, 'rb') as f:
        content = f.read()

    try:
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
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        ensure_table(cursor)
        print("🔧 Tablo hazır.")

        for entry in os.scandir(directory_path):
            if not entry.is_file() or not entry.name.lower().endswith('.txt'):
                continue

            filename = entry.name
            filepath = entry.path

            if insert_file(cursor, filename, filepath):
                conn.commit()  # commit işlemi
                try:
                    os.remove(filepath)
                    print(f"🗑️ '{filename}' silindi.")
                except Exception as rm_err:
                    print(f"⚠️ '{filename}' silinirken hata: {rm_err}")

        print("🎉 İşlem tamamlandı.")

    except Error as e:
        print("❌ Genel MySQL bağlantı hatası:", e)
    finally:
        try:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
        except:
            pass

if __name__ == '__main__':
    klasor_yolu = r"C:\Users\taha.ozen\Documents\GitHub\HELIX-NEBULA-ADP-2\veri"
    insert_all_txt_files(klasor_yolu)
