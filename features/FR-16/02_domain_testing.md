# FR-16: Import sản phẩm từ CSV — Domain Testing

Oracle: SRS `README.md` (FR-16 dòng 200–211; FR-12 dòng 176–179; FR-15 dòng 191–198; SEC-03 dòng 280). Chi tiết ở `01_analysis.md`.

Quy ước:
- Mã lớp: `EC-<nhóm>-V<n>` (hợp lệ), `EC-<nhóm>-I<n>` (không hợp lệ).
- Mỗi test không hợp lệ chỉ chứa **một** lỗi; phần còn lại của file hợp lệ (dòng dữ liệu chuẩn bên dưới).
- Tiêu chí "không import" = **số sản phẩm trong DB không đổi** (đếm `GET /api/products` trước/sau), không chỉ dựa vào thông báo.
- Cột **Lớp chạy**: `UI` = chọn file `.csv` thật trên Web Admin (tab Sản phẩm), parse ở client; `API` = gọi `POST /api/admin/import-products` với mảng JSON.
- Dữ liệu chuẩn: header `name,price,description,imageUrl,category_id`; dòng hợp lệ `SP Test 1,100000,Mô tả 1,https://placehold.co/300,1`. Tên sản phẩm test dùng tiền tố `FR16-` để dễ đếm và dọn dẹp sau mỗi test.
- Tài khoản: Admin `admin@eshop.com` / `Admin123!` (token), User `test@eshop.com` / `Test1234!`.

## 1. Lớp tương đương

### 1.1 File
| Mã lớp | Loại | Mô tả | Ví dụ |
|---|---|---|---|
| EC-file-V1 | Hợp lệ | File `.csv` có header và ≥ 1 dòng dữ liệu | `products.csv` |
| EC-file-I1 | Không hợp lệ | Sai đuôi `.txt` (nội dung vẫn là CSV đúng) | `products.txt` |
| EC-file-I2 | Không hợp lệ | Sai đuôi `.xlsx` (nội dung CSV) | `products.xlsx` |
| EC-file-I3 | Không hợp lệ | File `.csv` rỗng (0 byte) | |
| EC-file-I4 | Không hợp lệ | Chỉ có header, không có dòng dữ liệu | |
| EC-file-I5 | Không hợp lệ | Chỉ có khoảng trắng/xuống dòng | |

### 1.2 Header
| Mã lớp | Loại | Mô tả | Ví dụ |
|---|---|---|---|
| EC-hdr-V1 | Hợp lệ | Đúng 5 cột, đúng thứ tự, đúng tên | `name,price,description,imageUrl,category_id` |
| EC-hdr-I1 | Không hợp lệ | Sai thứ tự | `price,name,description,imageUrl,category_id` |
| EC-hdr-I2 | Không hợp lệ | Thiếu cột `price` | `name,description,imageUrl,category_id` |
| EC-hdr-I3 | Không hợp lệ | Thừa cột | `name,price,description,imageUrl,category_id,sku` |
| EC-hdr-I4 | Không hợp lệ | Sai tên (hoa/thường) | `Name,Price,Description,ImageUrl,Category_id` |
| EC-hdr-I5 | Không hợp lệ | Không có header (dòng đầu là dữ liệu) | |

### 1.3 Định dạng trường (RFC 4180)
| Mã lớp | Loại | Mô tả | Ví dụ |
|---|---|---|---|
| EC-fmt-V1 | Hợp lệ | Trường thường không có ký tự đặc biệt | |
| EC-fmt-V2 | Hợp lệ | Trường có dấu phẩy bọc trong nháy kép | `"Áo, size M"` |
| EC-fmt-V3 | Hợp lệ | Nháy kép được escape bằng `""` | `"Màn hình 27"" IPS"` |
| EC-fmt-V4 | Hợp lệ | Xuống dòng kiểu CRLF | |
| EC-fmt-V5 | Hợp lệ | Ký tự tiếng Việt UTF-8 | `Điện thoại Samsung` |
| EC-fmt-I1 | Không hợp lệ | Nháy kép mở nhưng không đóng | `"Áo, size M,100000,...` |

### 1.4 `name`
| Mã lớp | Loại | Mô tả | Ví dụ |
|---|---|---|---|
| EC-name-V1 | Hợp lệ | Chuỗi không rỗng | `FR16-A` |
| EC-name-I1 | Không hợp lệ | Rỗng | `` |
| EC-name-I2 | Không hợp lệ | Chỉ khoảng trắng | `   ` |

### 1.5 `price`
| Mã lớp | Loại | Mô tả | Ví dụ |
|---|---|---|---|
| EC-price-V1 | Hợp lệ | Số nguyên dương | `100000` |
| EC-price-V2 | Hợp lệ | Số thập phân dương | `0.5` |
| EC-price-I1 | Không hợp lệ | Số âm | `-1` |
| EC-price-I2 | Không hợp lệ | Bằng 0 | `0` |
| EC-price-I3 | Không hợp lệ | Không phải số | `abc` |
| EC-price-I4 | Không hợp lệ | Rỗng | `` |

### 1.6 `category_id` (diễn giải theo FR-15: danh mục phải có trong danh sách)
| Mã lớp | Loại | Mô tả | Ví dụ |
|---|---|---|---|
| EC-cat-V1 | Hợp lệ | Id danh mục tồn tại | `1` |
| EC-cat-I1 | Không hợp lệ (diễn giải) | Id không tồn tại | `999` |
| EC-cat-I2 | Không hợp lệ (diễn giải) | Rỗng | `` |

### 1.7 Tính nguyên tử (vị trí và số dòng lỗi, mỗi dòng lỗi dùng lỗi `price = -1`)
| Mã lớp | Mô tả |
|---|---|
| EC-atom-V1 | Mọi dòng hợp lệ (đối chứng) |
| EC-atom-I1 | 1 dòng lỗi ở **đầu** file (3 dòng) |
| EC-atom-I2 | 1 dòng lỗi ở **giữa** (3 dòng) |
| EC-atom-I3 | 1 dòng lỗi ở **cuối** (3 dòng) |
| EC-atom-I4 | **Nhiều** dòng lỗi (2 trong 5 dòng) |
| EC-atom-I5 | **Tất cả** dòng lỗi (3 dòng) |

### 1.8 Quyền và hình dạng request (API)
| Mã lớp | Loại | Mô tả |
|---|---|---|
| EC-auth-V1 | Hợp lệ | Token Admin |
| EC-auth-I1 | Không hợp lệ | Không token |
| EC-auth-I2 | Không hợp lệ | Token User thường |
| EC-body-I1 | Không hợp lệ | Thiếu `products` |
| EC-body-I2 | Không hợp lệ | `products` là mảng rỗng |
| EC-body-I3 | Không hợp lệ | `products` không phải mảng (chuỗi) |
| EC-body-I4 | Không hợp lệ | Mảng chứa phần tử không phải object (`null`) |

### 1.9 Báo cáo và giao diện
| Mã lớp | Mô tả |
|---|---|
| EC-rep-1 | Báo cáo khi thành công: số dòng thành công |
| EC-rep-2 | Báo cáo khi thất bại: lý do theo dòng, số dòng lỗi, nói rõ **không có sản phẩm nào được thêm** |
| EC-rep-3 | Mã phản hồi API khi có lỗi cho thấy thất bại |
| EC-ui-1 | Nút Import bị vô hiệu khi chưa có dữ liệu |
| EC-ui-2 | Bảng xem trước đúng số dòng và tên cột |
| EC-ui-3 | File mẫu tải về đúng header và import được |

## 2. Test case

### 2.1 Hợp lệ và định dạng (UI, file thật)
| TC ID | Lớp phủ | Dữ liệu vào | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-DT-01 | EC-file-V1, EC-hdr-V1, EC-fmt-V1, EC-name-V1, EC-price-V1, EC-cat-V1 | 3 dòng hợp lệ | Import 3/3; DB tăng 3 | UI |
| FR16-DT-02 | EC-fmt-V2 | tên `"FR16-Áo, size M"` | Tạo 1 SP có tên đúng `FR16-Áo, size M` (không bị cắt tại dấu phẩy) | UI |
| FR16-DT-03 | EC-fmt-V3 | tên `"FR16-Màn hình 27"" IPS"` | Tạo 1 SP tên `FR16-Màn hình 27" IPS` | UI |
| FR16-DT-04 | EC-fmt-V4 | file dùng CRLF, 3 dòng | Import 3 SP, tên/giá không chứa ký tự `\r` | UI |
| FR16-DT-05 | EC-fmt-V5 | tên tiếng Việt có dấu | Lưu đúng, không lỗi mã hóa | UI |
| FR16-DT-06 | EC-price-V2 | price `0.5` | Chấp nhận (số dương) | UI+API |
| FR16-DT-43 | EC-fmt-I1 | tên mở nháy kép không đóng | Từ chối file không hợp lệ, DB không đổi | UI |

### 2.2 File
| TC ID | Lớp phủ | Dữ liệu vào | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-DT-07 | EC-file-I1 | `products.txt` nội dung CSV đúng | Từ chối (đuôi phải `.csv`), DB không đổi | UI |
| FR16-DT-08 | EC-file-I2 | `products.xlsx` nội dung CSV đúng | Từ chối, DB không đổi | UI |
| FR16-DT-09 | EC-file-I3 | `.csv` 0 byte | Không import được, có thông báo/ nút vô hiệu, DB không đổi | UI |
| FR16-DT-10 | EC-file-I4 | chỉ header | Không import, DB không đổi | UI |
| FR16-DT-11 | EC-file-I5 | chỉ khoảng trắng/xuống dòng | Không import, DB không đổi | UI |

### 2.3 Header
| TC ID | Lớp phủ | Dữ liệu vào | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-DT-12 | EC-hdr-I1 | header sai thứ tự (+ dữ liệu theo thứ tự đó) | Từ chối, DB không đổi | UI |
| FR16-DT-13 | EC-hdr-I2 | thiếu cột `price` | Từ chối, DB không đổi | UI |
| FR16-DT-14 | EC-hdr-I3 | thừa cột `sku` | Từ chối, DB không đổi | UI |
| FR16-DT-15 | EC-hdr-I4 | header `Name,Price,...` | Từ chối, DB không đổi | UI |
| FR16-DT-16 | EC-hdr-I5 | không có header | Từ chối, DB không đổi | UI |

### 2.4 Nội dung dòng (mỗi test chỉ một lỗi; 1 dòng dữ liệu)
| TC ID | Lớp phủ | Dữ liệu vào | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-DT-17 | EC-name-I1 | name rỗng | Từ chối, DB không đổi | UI+API |
| FR16-DT-18 | EC-name-I2 | name `"   "` | Từ chối, DB không đổi | UI+API |
| FR16-DT-19 | EC-price-I1 | price `-1` | Từ chối, DB không đổi | UI+API |
| FR16-DT-20 | EC-price-I2 | price `0` | Từ chối, DB không đổi | UI+API |
| FR16-DT-21 | EC-price-I3 | price `abc` | Từ chối, DB không đổi | UI+API |
| FR16-DT-22 | EC-price-I4 | price rỗng | Từ chối, DB không đổi | UI+API |
| FR16-DT-23 | EC-cat-I1 | category_id `999` | Từ chối (danh mục không tồn tại; diễn giải FR-15), DB không đổi | UI+API |
| FR16-DT-24 | EC-cat-I2 | category_id rỗng | Từ chối (danh mục bắt buộc; diễn giải FR-15), DB không đổi | UI+API |

### 2.5 Tính nguyên tử
| TC ID | Lớp phủ | Dữ liệu vào | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-DT-25 | EC-atom-I1 | 3 dòng, dòng 1 lỗi | **Không** dòng nào được thêm (rollback) | UI+API |
| FR16-DT-26 | EC-atom-I2 | 3 dòng, dòng 2 lỗi | Không dòng nào được thêm | UI+API |
| FR16-DT-27 | EC-atom-I3 | 3 dòng, dòng 3 lỗi | Không dòng nào được thêm | UI+API |
| FR16-DT-28 | EC-atom-I4 | 5 dòng, dòng 2 và 4 lỗi | Không dòng nào được thêm | UI+API |
| FR16-DT-29 | EC-atom-I5 | 3 dòng, cả 3 lỗi | Không dòng nào được thêm | UI+API |
| FR16-DT-30 | EC-atom-V1 | 5 dòng hợp lệ | Thêm cả 5 | UI+API |

### 2.6 Báo cáo
| TC ID | Lớp phủ | Kịch bản | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-DT-31 | EC-rep-1 | Import thành công 3 dòng | Báo cáo nêu số dòng thành công (3) | UI |
| FR16-DT-32 | EC-rep-2 | Import file có 1 dòng lỗi (dòng 2 của 3) | Báo cáo nêu rõ lỗi ở dòng nào và lý do, **số dòng lỗi**, và việc import đã bị hủy (0 sản phẩm được thêm) | UI |
| FR16-DT-33 | EC-rep-3 | API với 1 dòng lỗi | Phản hồi cho thấy thất bại (HTTP 4xx hoặc `inserted = 0` kèm lỗi), không phải "hoàn tất" thành công | API |

### 2.7 Quyền và hình dạng request (API)
| TC ID | Lớp phủ | Dữ liệu vào | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-DT-34 | EC-auth-I1 | không token | 401, DB không đổi | API |
| FR16-DT-35 | EC-auth-I2 | token User thường, 1 dòng hợp lệ | Từ chối (403), DB không đổi (FR-12, SEC-03) | API |
| FR16-DT-36 | EC-body-I1 | body không có `products` | 400, server vẫn sống | API |
| FR16-DT-37 | EC-body-I2 | `products: []` | 400 | API |
| FR16-DT-38 | EC-body-I3 | `products: "abc"` | 400 | API |
| FR16-DT-39 | EC-body-I4 | `products: [null]` | 400, server không crash | API |

### 2.8 Giao diện
| TC ID | Lớp phủ | Kịch bản | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-DT-40 | EC-ui-1 | Mở tab Sản phẩm, chưa chọn file | Nút Import bị vô hiệu | UI |
| FR16-DT-41 | EC-ui-2 | Chọn file 3 dòng hợp lệ | Bảng xem trước hiển thị 3 dòng và đủ 5 tên cột | UI |
| FR16-DT-42 | EC-ui-3 | Nội dung link "Tải file mẫu" | Header đúng chuẩn; import được file mẫu | UI |

## 3. Truy vết lớp → test
| Nhóm lớp | Test phủ |
|---|---|
| EC-file-V1, EC-hdr-V1, EC-fmt-V1, EC-name-V1, EC-price-V1, EC-cat-V1 | DT-01 (và mọi test hợp lệ khác) |
| EC-file-I1..I5 | DT-07..DT-11 |
| EC-hdr-I1..I5 | DT-12..DT-16 |
| EC-fmt-V2..V5 | DT-02..DT-05 |
| EC-fmt-I1 | DT-43 |
| EC-name-I1, I2 | DT-17, DT-18 |
| EC-price-V2 | DT-06 |
| EC-price-I1..I4 | DT-19..DT-22 |
| EC-cat-I1, I2 | DT-23, DT-24 |
| EC-atom-V1, I1..I5 | DT-30, DT-25..DT-29 |
| EC-rep-1..3 | DT-31..DT-33 |
| EC-auth-I1, I2 | DT-34, DT-35 |
| EC-body-I1..I4 | DT-36..DT-39 |
| EC-ui-1..3 | DT-40..DT-42 |

Tổng: **43** test case Domain Testing; mọi lớp đều có ít nhất một test.

## 4. Giới hạn và giả định
- DT-23, DT-24 (danh mục) dựa trên FR-15 ("danh mục phải chọn từ danh sách có sẵn"); FR-16 không nêu rõ nên nếu lệch thì ghi "theo diễn giải", không coi chắc chắn là bug.
- DT-06: số thập phân dương được coi là số dương; cột `price` trong DB là `INTEGER` nên chỉ kiểm tra hệ thống có chấp nhận hay không, không đánh giá việc làm tròn.
- Parse CSV được làm ở client nên các test về định dạng (nháy kép, header, CRLF) chỉ chạy được trên UI; validate `name`/`price`, quyền và hình dạng request chạy trên API.
- Đuôi file `.csv` chỉ có thể kiểm tra khi chọn file qua UI (`<input type="file">` không có `accept`).
