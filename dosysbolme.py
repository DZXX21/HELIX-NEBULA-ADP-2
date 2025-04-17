#!/usr/bin/env python3
import os
import argparse

MAX_BYTES = 1 * 1024**3  # 1 GB

def split_file(file_path):
    base = os.path.basename(file_path)
    name, _ = os.path.splitext(base)
    dirn = os.path.dirname(file_path) or '.'
    part = 1
    with open(file_path, 'rb') as src:
        while True:
            chunk = src.read(MAX_BYTES)
            if not chunk:
                break
            out_filename = f"{name}.part{part}.txt"
            out_path = os.path.join(dirn, out_filename)
            with open(out_path, 'wb') as dst:
                dst.write(chunk)
            print(f"[+] Oluşturuldu: {out_path}")
            part += 1

def main():
    p = argparse.ArgumentParser(
        description="1 GB üstü .txt dosyalarını parçalara böl"
    )
    p.add_argument("path", help="Dosya veya dizin yolu")
    args = p.parse_args()

    if os.path.isfile(args.path):
        if args.path.lower().endswith(".txt") and os.path.getsize(args.path) > MAX_BYTES:
            split_file(args.path)
        else:
            print("Bu dosya ya .txt değil ya da 1 GB sınırını aşmıyor.")
    elif os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for fn in files:
                if fn.lower().endswith(".txt"):
                    fp = os.path.join(root, fn)
                    if os.path.getsize(fp) > MAX_BYTES:
                        split_file(fp)
    else:
        print("Geçersiz yol: dosya veya dizin bulunamadı.")

if __name__ == "__main__":
    main()
