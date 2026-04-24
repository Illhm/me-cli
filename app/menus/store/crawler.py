from app.client.engsel import get_families
from app.menus.util import clear_screen, pause
from app.service.auth import AuthInstance
import time
import json
import os

WIDTH = 55

def run_crawler_menu(is_enterprise: bool = False):
    clear_screen()
    print("=" * WIDTH)
    print("🤖 CRAWLER FAMILY CODE (Cari Paket Murah/Rp 0) 🤖")
    print("=" * WIDTH)
    print("Script ini akan meraba list category code populer")
    print("dan mengumpulkan semua UUID Family Code yang didapat.")
    print("=" * WIDTH)

    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    if not tokens:
        print("Silahkan login terlebih dahulu.")
        pause()
        return

    # Kategori-kategori umum (contoh berdasarkan typical provider)
    common_categories = [
        "HOT", "PROMO", "INTERNET", "XTRA_COMBO", "AKRAB", "PRIO",
        "BONUS", "REWARD", "ROAMING", "ENTERTAINMENT", "LIFELINE", "UNLIMITED",
        "GIFT", "LOYALTY", "SPECIAL", "TRIAL", "01", "02", "03", "04", "05"
    ]

    print("Apakah Anda ingin menggunakan kategori bawaan, atau ketik custom kategori?")
    print("1. Gunakan kategori bawaan (HOT, PROMO, dll)")
    print("2. Input kategori kustom (pisahkan dengan koma)")
    print("0. Kembali")

    choice = input("Pilih: ")

    categories_to_crawl = []
    if choice == '1':
        categories_to_crawl = common_categories
    elif choice == '2':
        custom = input("Masukkan kategori (contoh: PROMO,SPECIAL,01): ")
        categories_to_crawl = [c.strip() for c in custom.split(",") if c.strip()]
    else:
        return

    found_families = []

    print("\n[+] Memulai proses crawling...")
    for cat in categories_to_crawl:
        print(f"Mencari di kategori: {cat}...")
        try:
            # Panggil fungsi yang ada di engsel.py
            res = get_families(api_key, tokens, package_category_code=cat)

            # get_families me-return list of dict / dictionary
            if res and "package_families" in res:
                families = res["package_families"]
                if len(families) > 0:
                    print(f"  -> Ditemukan {len(families)} package families!")
                    for f in families:
                        # Filter duplicates based on family code
                        existing = [x for x in found_families if x["code"] == f.get("package_family_code")]
                        if not existing:
                            found_families.append({
                                "code": f.get("package_family_code"),
                                "name": f.get("name", "Unknown Name"),
                                "category": cat
                            })
                else:
                    print("  -> Kosong.")
            else:
                print("  -> Kosong atau tidak ada response data.")

        except Exception as e:
            print(f"  -> Error pada kategori {cat}: {e}")

        time.sleep(1) # delay agar tidak rate limited

    print("\n" + "=" * WIDTH)
    print(f"🎉 Crawling selesai! Total unik UUID ditemukan: {len(found_families)}")
    print("=" * WIDTH)

    if len(found_families) > 0:
        save_choice = input("Apakah Anda ingin menyimpan hasilnya ke crawler_result.json? (y/n): ")
        if save_choice.lower() == 'y':
            with open("crawler_result.json", "w", encoding="utf-8") as f:
                json.dump(found_families, f, indent=4)
            print("Hasil disimpan di crawler_result.json")

        print("\nPreview 5 UUID Pertama:")
        for idx, f in enumerate(found_families[:5]):
            print(f"{idx+1}. {f['name']} (Cat: {f['category']})\n   UUID: {f['code']}")

    pause()
