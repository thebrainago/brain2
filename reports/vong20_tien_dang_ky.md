# Vong 20 - loc trang thai -> chon nhom - DANG KY TRUOC (2026-10-12 ~16:05 UTC+7, truoc khi chay). MO PHONG.
Trang thai tai dong nen i (chi dung du lieu <= i; lenh vao o mo i+1):
 C1 (quy tac): XU_HUONG neu ER20 (efficiency ratio) > 0,30 HOAC ADX14 > 25, nguoc lai DI_NGANG; BIEN_DONG_CAO neu ATR14 > trung vi ATR14 500 nen truoc.
    => 4 trang thai.
 C2 (thong ke): GaussianMixture 3 thanh phan tren (log ATR14/gia, ER20, |loi nhuan 24 nen|), fit CHI tren nua phat hien tung cap.
    (HMM that: khong co thu vien hmmlearn tren box -> GMM thay the, khong co ma tran chuyen.)
Hurst: khong dung (ER20 + ADX da do xu huong) - ghi ro.
Chien luoc: 21 lenh vao cua vong 19 (8 cu + 13 moi) x 3 thoat (TR2, GIO6, TP) - dung nguyen ma v19/v19b.
Chon anh xa (CHI tren nua phat hien bo 1, gop 7 cap): moi trang thai -> to hop (vao, thoat) co loi trung binh/lenh cao nhat (>= 30 lenh);
neu tot nhat <= 0 -> khong giao dich trong trang thai do.
He chuyen trang thai = moi cap chi lay lenh cua to hop duoc chon cho trang thai luc vao.
Kiem: nua kiem bo 1 (7 cap) va TOAN bo 2 (6 chuoi) voi anh xa co dinh => (7 + 6) x 2 bo phan loai = 26 o; t mot phia loi/lenh > 0.
Holm cong don 6.295 + 26. Song: Holm < 0,05, lai, spread x1,5 lai, maxDD < 80 %. So sanh: tung to hop chay rieng khong loc (nua kiem).
Do: tan suat doi trang thai (do dai trung binh moi doan, nen), do tre: do lech (nen) cho tuong quan cheo lon nhat giua ER20 thoi gian thuc
va ER20 "that" tinh tren cua so tam [i-10, i+10] (chi de do, khong dung de giao dich).
Bang nhom x trang thai: loi trung binh/lenh (bps) nua kiem bo 1 va bo 2.
