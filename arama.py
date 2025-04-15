import mysql.connector
import re

db_config = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'my-secret-pw',
    'database': 'testdb'
}

def extract_com_tr_entries():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = "SELECT dosya_adi, CONVERT(icerik USING utf8mb4) FROM dosyalar WHERE CONVERT(icerik USING utf8mb4) LIKE '%.com.tr%'"
    cursor.execute(query)

    regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com\.tr|https?:\/\/[^\s\"']+\.com\.tr|www\.[^\s\"']+\.com\.tr"

    toplam_eslesme = 0
    toplam_dosya = 0

    print("🔍 .com.tr geçen veriler:")

    for dosya_adi, icerik in cursor.fetchall():
        matches = re.findall(regex, icerik)
        if matches:
            toplam_dosya += 1
            print(f"\n📄 Dosya: {dosya_adi} ({len(matches)} eşleşme)")
            for m in matches:
                print(f"   → {m}")
            toplam_eslesme += len(matches)

    print("\n📊 Özet")
    print(f"📁 .com.tr geçen dosya sayısı: {toplam_dosya}")
    print(f"🔢 Toplam eşleşme sayısı: {toplam_eslesme}")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    extract_com_tr_entries()
