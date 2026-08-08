import sys, os, json
sys.path.insert(0, r'C:\Users\arija\ziyan_intake')
import scheduler as S

LINK = "https://s.shopee.co.id/6Ak3g4iefN"
DESC = "SAMELEVEL Madeline Dress Korean Midi Dress Wanita - Rp179.550"
CAP = f"{LINK}\n{DESC}\n#KoreanMidiDress #MadelineDress #OOTD #ShopeeAffiliate"

VID1 = r'C:\Users\arija\AppData\Local\hermes\cache\videos\video_ab2913295810.mp4'
VID2 = r'C:\Users\arija\AppData\Local\hermes\cache\videos\video_ae446f5fab30.mp4'
IMG1 = r'C:\Users\arija\AppData\Local\hermes\cache\images\img_e3063ad18082.jpg'  # maroon
IMG2 = r'C:\Users\arija\AppData\Local\hermes\cache\images\img_af36e6ed2d83.jpg'  # sage/olive

# baca queue, buang item teks Madeline lama (deskripsi sama, tipe teks)
Q = S.QUEUE
q = json.load(open(Q)) if os.path.exists(Q) else []
q = [i for i in q if not (i.get("tipe")=="teks" and "Madeline" in i.get("deskripsi",""))]
json.dump(q, open(Q,"w"), indent=2, ensure_ascii=False)

items = [
    {"file_path": VID1, "deskripsi": DESC, "caption": CAP, "link_aff": LINK, "tipe": "video"},
    {"file_path": VID2, "deskripsi": DESC, "caption": CAP, "link_aff": LINK, "tipe": "video"},
    {"file_path": IMG1, "deskripsi": DESC+" (Maroon)", "caption": CAP, "link_aff": LINK, "tipe": "foto"},
    {"file_path": IMG2, "deskripsi": DESC+" (Sage/Olive)", "caption": CAP, "link_aff": LINK, "tipe": "foto"},
]
for it in items:
    S.enqueue(it)
print("QUEUE total sekarang:", len(json.load(open(Q))))
