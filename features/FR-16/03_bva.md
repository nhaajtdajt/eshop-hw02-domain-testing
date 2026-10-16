# FR-16: Import sản phẩm từ CSV — Boundary Value Analysis

Oracle: SRS `README.md` (FR-16 dòng 200–211, FR-15 dòng 195–197 để tham chiếu độ dài tên). Nhập từ `02_domain_testing.md`.
Kỹ thuật: 3 giá trị tại mỗi biên (biên−1, biên, biên+1), kèm cực trị khi SRS không nêu giới hạn.

## 1. Chọn đại lượng có thứ tự và biên theo spec

| Đại lượng | Miền theo spec | Biên | Đóng/Mở | Giá trị kiểm thử | Nguồn |
|---|---|---|---|---|---|
| Số dòng dữ liệu của file | ≥ 1 (file phải có dữ liệu để import) | 1 | đóng | 0 (header-only, DT-10), **1**, **2**, 100, 1000 (không nêu tối đa) | FR-16 dòng 202 |
| Số trường mỗi dòng | đúng 5 (khớp header) | 5 | đóng | **4** (n−1), 5, **6** (n+1) | FR-16 dòng 205 |
| Giá `price` | số dương (> 0) | 0 | **mở** (`> 0`) | −1 (DT-19), 0 (DT-20), **1**, **0.01**, cực trị 2147483647, 2147483648, 9223372036854775808 | FR-16 dòng 209 |
| Độ dài `name` | không rỗng (≥ 1); tối đa 255 theo FR-15 (diễn giải) | 1 và 255 | đóng | 0 (DT-17), **1**, **255**, **256** | FR-16 dòng 208; FR-15 dòng 195 |
| Vị trí dòng lỗi trong file | bất kỳ dòng nào lỗi → hủy toàn bộ | dòng 1 và dòng N | đóng | N=1 (dòng đầu = dòng cuối), N=2 dòng 2 lỗi, N=100 dòng 100 lỗi, N=1000 dòng 1000 lỗi | FR-16 dòng 210 |
| Số thứ tự dòng trong báo cáo lỗi | dòng 1 là header, dòng dữ liệu đầu là dòng 2 | 2 và N+1 | đóng | lỗi ở dòng dữ liệu đầu, ở dòng dữ liệu cuối | FR-16 dòng 211 |
| Kích thước request | spec không nêu giới hạn | — | — | ~100 dòng (nhỏ), ~1000 dòng (lớn; có thể vượt giới hạn body mặc định 100 KB của `body-parser`) | FR-16 dòng 202 ("nhiều sản phẩm") |

Ghi chú: các biên 0 dòng, giá −1/0, tên rỗng, 1 dòng lỗi đầu/giữa/cuối đã có ở Domain Testing (tham chiếu bên dưới), BVA chỉ thêm các giá trị mới.

## 2. Test case BVA

Điều kiện chung: Admin đã đăng nhập; mỗi test đếm số sản phẩm trước/sau; tên SP test có tiền tố `FR16-`; dọn dẹp sau mỗi test. Dòng "hợp lệ" mặc định: `FR16-<n>,100000,Mô tả sản phẩm test dòng <n>,https://placehold.co/300,1`.

### 2.1 Số dòng dữ liệu
| TC ID | Số dòng hợp lệ | Vị trí so với biên | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-BV-01 | 1 | **biên** (min) | Import 1/1, DB +1 | UI+API |
| FR16-BV-02 | 2 | biên+1 | Import 2/2, DB +2 | UI+API |
| FR16-BV-03 | 100 | giá trị lớn vừa | Import 100/100, DB +100 | UI+API |
| FR16-BV-04 | 1000 | cực trị cao | Import 1000/1000, DB +1000 (SRS không nêu giới hạn); nếu bị từ chối thì phải có thông báo rõ ràng, DB không đổi | API |

### 2.2 Số trường mỗi dòng (UI, một dòng dữ liệu)
| TC ID | Dữ liệu dòng | Vị trí so với biên | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-BV-05 | `FR16-X,100000,Mô tả,https://placehold.co/300` (4 trường, thiếu `category_id`) | n−1 | File không hợp lệ (RFC 4180: mỗi dòng cùng số trường), từ chối, DB không đổi | UI |
| FR16-BV-06 | `FR16-X,100000,Mô tả,https://placehold.co/300,1,thua` (6 trường) | n+1 | Từ chối, DB không đổi | UI |

### 2.3 Giá
| TC ID | `price` | Vị trí so với biên | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-BV-07 | `1` | biên+1 (số nguyên dương nhỏ nhất) | Chấp nhận | UI+API |
| FR16-BV-08 | `0.01` | sát biên mở 0 | Chấp nhận (số dương) | UI+API |
| FR16-BV-09 | `2147483647` | cực trị (2³¹−1) | Chấp nhận, lưu đúng giá trị | API |
| FR16-BV-10 | `2147483648` | cực trị (2³¹) | Chấp nhận (SRS không nêu tối đa), lưu đúng giá trị | API |
| FR16-BV-11 | `9223372036854775808` (2⁶³) | cực trị | Không lỗi server; hoặc từ chối rõ ràng, hoặc lưu đúng; không được lưu giá trị sai | API |

### 2.4 Độ dài `name` (diễn giải FR-15 cho 256)
| TC ID | Độ dài | Vị trí so với biên | Expected | Lớp chạy |
|---|---|---|---|---|
| FR16-BV-12 | 1 ký tự | **biên** (min) | Chấp nhận | UI+API |
| FR16-BV-13 | 255 ký tự | **biên** (max theo FR-15) | Chấp nhận | UI+API |
| FR16-BV-14 | 256 ký tự | biên+1 | Từ chối (diễn giải FR-15), DB không đổi | UI+API |

### 2.5 Vị trí dòng lỗi (lỗi `price = -1`) và số dòng trong báo cáo
| TC ID | Cấu hình | Vị trí so với biên | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR16-BV-15 | 1 dòng dữ liệu và dòng đó lỗi | dòng đầu = dòng cuối | Không thêm gì; báo lỗi dòng 2 | UI+API |
| FR16-BV-16 | 2 dòng dữ liệu, dòng thứ 2 lỗi | biên (dòng cuối của N=2) | Không thêm gì (dòng 1 hợp lệ cũng không được lưu); báo lỗi dòng 3 | UI+API |
| FR16-BV-17 | 100 dòng, chỉ dòng 100 lỗi | dòng cuối | Không thêm dòng nào (99 dòng hợp lệ cũng bị hủy); báo lỗi dòng 101 | UI+API |
| FR16-BV-18 | 1000 dòng, chỉ dòng 1000 lỗi | cực trị | Không thêm dòng nào; báo lỗi dòng 1001 (hoặc từ chối toàn bộ rõ ràng) | API |
| FR16-BV-19 | 3 dòng, dòng dữ liệu **đầu tiên** lỗi | dòng đầu | Báo lỗi **dòng 2** (dòng 1 là header) | UI+API |

## 3. Tham chiếu chéo với Domain Testing
Các biên còn lại đã có ở `02_domain_testing.md`, không lặp lại: 0 dòng dữ liệu (DT-10, DT-09, DT-11), `price` −1 (DT-19) và 0 (DT-20), `name` rỗng (DT-17), 1 dòng lỗi ở đầu/giữa/cuối của file 3 dòng (DT-25..27), nhiều dòng lỗi (DT-28), tất cả dòng lỗi (DT-29).

## 4. Thống kê
- **19** test case BVA (BV-01..BV-19).
- Cùng 43 test Domain Testing → **62** test case thiết kế cho FR-16.

## 5. Giới hạn
- BV-04, BV-18 (1000 dòng) kiểm tra khả năng xử lý dữ liệu lớn và giới hạn kích thước body; SRS không nêu số dòng tối đa nên expected chỉ ở mức "import đủ hoặc từ chối rõ ràng, không mất/hỏng dữ liệu".
- BV-09..BV-11 không có biên theo spec (không nêu giá tối đa); mục đích là phát hiện lỗi tràn/lưu sai giá trị.
- BV-14 (256 ký tự) là diễn giải từ FR-15; nếu lệch ghi "theo diễn giải".
