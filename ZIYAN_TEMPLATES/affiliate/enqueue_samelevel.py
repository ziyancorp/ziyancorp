import sys, os
sys.path.insert(0, r'C:\Users\arija\ziyan_intake')
import scheduler as S

LINK = "https://s.shopee.co.id/4LIPRqMDM8"
DESC = "SAMELEVEL Autumn Ribbon Halter Dress / Casual Summer Maxi Dress / Korean Dress Wanita - Rp169.426"
CAP = f"{LINK}\n{DESC}\n#KoreanDress #MaxiDress #HalterDress #OOTD #ShopeeAffiliate"

VID1 = r'C:\Users\arija\AppData\Local\hermes\cache\videos\video_deb16b60c4fb.mp4'
VID2 = r'C:\Users\arija\AppData\Local\hermes\cache\videos\video_5e07cae89e60.mp4'
IMG1 = r'C:\Users\arija\AppData\Local\hermes\cache\images\img_20ef19f9f619.jpg'  # olive
IMG2 = r'C:\Users\arija\AppData\Local\hermes\cache\images\img_57bf56c2e075.jpg'  # pastel blue

items = [
    {"file_path": VID1, "deskripsi": DESC, "caption": CAP, "link_aff": LINK, "tipe": "video"},
    {"file_path": VID2, "deskripsi": DESC, "caption": CAP, "link_aff": LINK, "tipe": "video"},
    {"file_path": IMG1, "deskripsi": DESC+" (Olive)", "caption": CAP, "link_aff": LINK, "tipe": "foto"},
    {"file_path": IMG2, "deskripsi": DESC+" (Pastel Blue)", "caption": CAP, "link_aff": LINK, "tipe": "foto"},
]
for it in items:
    S.enqueue(it)
print("ENQUEUED:", len(items), "item -> schedule 1 per 6 jam")
