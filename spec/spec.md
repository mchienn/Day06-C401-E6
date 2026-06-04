# SPEC san pham: AI Food Recommendation

## 1. Bang chung

### Track, app that va user

- **Track:** Food & Local Delivery
- **App tham chieu:** ShopeeFood / GrabFood
- **User chinh:** nhan vien van phong va sinh vien can dat bua trua nhanh, thuong chi co cam giac them mo ho thay vi biet chinh xac ten mon.
- **Nhom co phai user that khong:** co. Nhom cung gap tinh huong phai luot app lau de chon mon, dac biet khi chi nghi duoc cac mo ta nhu "do nuoc", "thanh dam", "gan day".

### Evidence summary

| Evidence | Nguon | User/pain noi len dieu gi? | SPEC phai doi gi? |
|---|---|---|---|
| Khi go mo ta ngu canh nhu "toi muon an do nuoc, thanh dam, loanh quanh Quan 1" tren GrabFood/ShopeeFood, ket qua thuong rong hoac bi keo ve keyword cung. | Self-use tren app giao do an | App hien tai bat user phai biet ten mon cu the, trong khi user chi biet cam giac them hoac trang thai an uong. | AI phai hieu intent roi map sang tag mon an, khong chi search keyword. |
| Khi hoi ChatGPT "Trua nay an gi do nuoc, thanh dam o Quan 1", AI hieu dung nhu cau nhung de goi y quan sai vi tri hoac quan khong kiem chung duoc. | Self-use voi ChatGPT | LLM hieu ngon ngu tu nhien tot, nhung thieu du lieu khoang cach va du lieu mon that nen de hallucinate. | Prototype chi dung dataset nho 10-20 mon da gan tag, co hard filter ban kinh duoi 3km. |
| "Trua nao toi va dong nghiep cung mat 20-30 phut chi de chon mon, luot app mot hoi cuoi cung lai goi lai mon cu vi met." | Phong van nhanh nhan vien van phong | Pain chinh khong chi la tim mon, ma la decision fatigue trong gio nghi trua ngan. | Output phai gioi han dung 3 goi y tot nhat, kem ly do ngan de ra quyet dinh nhanh. |
| User thuong chi nghi ra cam giac nhu "muon do nuoc" nhung app bat tu suy ra pho, bun, mien hoac ten quan. | Gia dinh tu evidence pack, can kiem them voi 3-5 user | Nhu cau ban dau cua user nam o mo ta tu nhien, khong phai danh muc cung. | Form nhap phai nhan cau tu nhien; UI khong ep user chon nhieu filter truoc. |

### Pain statement

User **nhan vien van phong va sinh vien** gap kho o buoc **chon mon an trua**, vi ho thuong chi nghi ra cam giac them nhu "do nuoc", "thanh dam", "an gan cong ty" nhung cac app hien tai lai yeu cau ho go dung keyword hoac tu biet ten mon. Ket qua la ho mat **20-30 phut** luot app, met vi qua nhieu lua chon, roi thuong quay lai mon cu.

Insight cua nhom: bai toan khong chi la search mon an. User can **decision support**: mot he thong giup chuyen mo ta mo ho thanh vai lua chon du tot, dang tin, va de kiem tra.

## 2. Lat cat de build

Cho **mot nhan vien van phong hoac sinh vien** dang **can dat do an trua nhung chi co mo ta tu nhien/mo ho**, prototype dung AI de **phan tich intent thanh cac tag cu the nhu loai mon, vi, khu vuc, ngan sach, dieu kien di ung**, sau do **khop voi dataset noi bo 10-20 mon** va tra ve **dung 3 mon phu hop nhat kem ly do ngan**, dong thoi chan loi nguy hiem bang **hard filter khoang cach duoi 3km va filter di ung bat buoc**.

Khong build toan bo app giao do an. Prototype chi chung minh mot flow: nhap nhu cau tu nhien -> AI hieu intent -> loc dataset -> hien thi 3 goi y -> user chon hoac sua dieu kien.

## 3. AI Product Canvas

| O | Noi dung |
|---|---|
| **Value - Gia tri** | San pham danh cho nguoi ban ron can chon mon nhanh. AI giai quyet khoang trong ma search keyword chua lam tot: hieu mo ta mo ho, giam so lua chon xuong 3 mon co ly do ro rang, giup user ra quyet dinh trong vai phut thay vi luot app 20-30 phut. |
| **Trust - Niem tin** | AI khong duoc tu bia quan hoac mon ngoai dataset. Moi goi y phai hien thi tag khop, khoang cach, canh bao di ung neu co, va ly do ngan. Khi AI khong chac, UI hoi lai hoac cho user sua prompt/filter. User luon la nguoi chon mon cuoi cung. |
| **Feasibility - Tinh kha thi** | Trong hackathon, dataset nho 10-20 mon la du de demo. Moi luot goi AI chi can extract intent va cham diem phu hop, do tre chap nhan duoc duoi 5 giay. Rui ro lon nhat la goi y mon sai di ung hoac sai vi tri; nguong dung la khi prototype khong loc duoc di ung/khoang cach mot cach on dinh. |
| **Tin hieu hoc** | Khi user sua prompt, bo mon, doi filter hoac chon mot mon trong 3 goi y, he thong luu lai thanh log test: input ban dau, tag AI extract, mon bi loai, mon duoc chon, ly do sua. Trong prototype, du lieu nay dung de cai thien rule/tag va tao test case; chua dung de train model tu dong. |

## 4. Tang nang luc hay tu dong hoa

Nhom chon **Augmentation**.

AI ho tro user bang cach phan tich nhu cau va rut gon lua chon, nhung **khong tu dat mon, khong tu quyet dinh user se an gi**. Quyen quyet dinh cuoi nam o user tai buoc chon mot trong 3 mon hoac sua lai dieu kien.

Ly do: chon mon an co yeu to khau vi, suc khoe va di ung. Neu AI sai, hau qua co the tu kho chiu den rui ro an toan. Vi vay muc phu hop la AI lam phan nang ve suy luan va loc lua chon, con con nguoi giu vai tro decider.

## 5. Bon duong di cua trai nghiem

| Duong di | Prototype phai the hien gi? | Cach xu ly trong demo |
|---|---|---|
| **Duong thuan** | User nhap "toi muon an do nuoc, thanh dam, loanh quanh Quan 1". AI extract tag: do nuoc, thanh dam, Quan 1/gan day, khong di ung. | Hien thi dung 3 mon tu dataset, moi mon co ten, tag khop, khoang cach duoi 3km va ly do 1-2 cau. |
| **Khi AI khong chac** | User nhap mo ta mau thuan hoac qua rong nhu "an gi cung duoc, vua cay vua khong cay, no nhung nhe bung". | AI hien thi trang thai khong chac, dua 2-3 lua chon lam ro nhu "uu tien nhe bung", "uu tien cay", "uu tien no" thay vi tu tin tra loi bua. |
| **Khi AI sai / khong co ket qua** | Dataset khong co mon nao thoa dong thoi khoang cach duoi 3km va dieu kien di ung. | Khong sinh mon ngoai dataset. UI bao khong tim thay lua chon an toan va de nghi noi khoang cach, doi loai mon hoac bo bot dieu kien khong quan trong. |
| **Khi user sua** | User bo mot mon vi khong thich, chinh di ung, hoac sua prompt tu "thanh dam" thanh "it dau, khong cay". | He thong chay lai filter, luu correction vao log, cap nhat tag/rule kiem thu de lan sau xu ly mo ta tuong tu tot hon. |

## 6. Nhung kieu loi dang lo nhat

### Loi 1: Goi y mon chua thanh phan di ung

- **Khi nao xay ra:** user co di ung dau phong, hai san hoac sua nhung prompt khong noi ro; hoac AI bo sot tag nguyen lieu trong dataset.
- **Ai chiu thiet:** user chiu rui ro suc khoe. Day la loi nang nhat.
- **Prototype xu ly:** form co truong/checkbox di ung bat buoc truoc khi goi y. Filter di ung chay truoc khi AI xep hang. Mon co ingredient trung di ung bi loai hoan toan, khong chi giam diem.

### Loi 2: Goi y quan/mon qua xa

- **Khi nao xay ra:** AI hieu dung mon nhung thieu hoac hieu sai vi tri, giong loi LLM tu goi y quan khong kiem chung duoc.
- **Ai chiu thiet:** user mat thoi gian, phi giao hang cao, trai nghiem giam trust.
- **Prototype xu ly:** chi dung mon trong dataset co truong khoang cach/khu vuc. Hard filter loai mon ngoai ban kinh 3km truoc khi hien thi.

### Loi 3: AI tu tin voi intent mo ho

- **Khi nao xay ra:** prompt qua ngan nhu "an gi do on on" hoac chua yeu cau mau thuan.
- **Ai chiu thiet:** user nhan goi y khong lien quan va quay lai luot app thu cong.
- **Prototype xu ly:** neu confidence thap hoac so tag quan trong thieu, AI hoi lai bang chip/option thay vi tra ra 3 mon nhu chac chan.

## 7. Ke hoach kiem thu va bang chung demo

### Input demo duong thuan

- **Prompt:** "Toi muon an do nuoc, thanh dam, loanh quanh Quan 1, khong dau phong."
- **Ky vong:** AI extract dung tag `do_nuoc`, `thanh_dam`, `quan_1`, `no_peanut`; tra ve 3 mon trong ban kinh duoi 3km, khong chua dau phong, co ly do ngan.

### Input demo kho / gay nhieu

- **Prompt:** "An gi cung duoc, vua cay vua khong cay, no nhung nhe bung, gan day cang tot, toi di ung hai san."
- **Ky vong:** AI khong tu tin tuyet doi; hoi user uu tien cay hay nhe bung/no; van giu filter di ung hai san va khoang cach.

### Test cases can luu trong repo

| Case | Input | Ky vong pass |
|---|---|---|
| Happy path | Do nuoc, thanh dam, Quan 1, khong di ung | 3 mon hop tag, duoi 3km |
| Allergy filter | Co di ung dau phong | Khong mon nao chua dau phong duoc hien thi |
| Distance filter | User yeu cau gan Quan 1 | Khong mon ngoai 3km duoc hien thi |
| Low-confidence | Prompt mau thuan | AI hoi lai hoac hien thi canh bao khong chac |
| Empty result | Dieu kien qua chat | Bao khong co ket qua an toan, khong bia mon |

Bang chung demo can co: anh chup man hinh flow happy path, anh chup man hinh low-confidence/error path, prompt log, dataset mau, va ghi chu cac lan chinh rule/tag.

## 8. Phan cong

| Thanh vien | Phan phu trach | Bang chung can co trong repo |
|---|---|---|
| NguyenThaiHoc | Research / evidence | Cap nhat quote phong van 3-5 user hoac ghi ro gia dinh nao chua kiem chung. |
| NguyenQuangMinh | SPEC | Hoan thien `spec/spec.md`, dam bao co canvas, failure mode va test plan. |
| PhamDucLiem | Prototype / dataset | Tao dataset nho 10-20 mon co tag, khoang cach, gia, nguyen lieu di ung. |
| NguyenTuanDung | Prototype / prompt flow | Xay prompt hoac logic extract intent, map tag va xep hang 3 mon. |
| NguyenDinhTienManh | Test / failure path | Kiem thu hard filter duoi 3km, filter di ung, low-confidence va empty result. |
| NguyenMinhChien | Demo script / repo | Chuan hoa repo, viet kich ban demo 5 phut, chuan bi screenshot hoac backup demo. |

## 9. Kich ban demo ngan

1. Mo bang pain: user mat 20-30 phut chon mon vi app search theo keyword, khong hieu "do nuoc/thanh dam/gan day".
2. Show input happy path va 3 goi y co ly do.
3. Giai thich AI chi augment: extract intent va loc dataset, user van quyet dinh.
4. Show failure/low-confidence: di ung hoac prompt mau thuan lam he thong hoi lai hoac khong tra mon khong an toan.
5. Ket bang bai hoc: LLM manh o hieu ngon ngu tu nhien, nhung phai bi rang buoc boi dataset, khoang cach va guardrail di ung de dang tin trong san pham that.
