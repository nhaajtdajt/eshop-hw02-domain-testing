# FR-10: Máy trạng thái đơn hàng — Boundary Value Analysis

Oracle: SRS `README.md` (FR-10 dòng 141–162). Nhập từ `02_domain_testing.md`.
FR-10 không có đại lượng số học nên "biên" ở đây gồm bốn loại: (a) ranh giới giữa trạng thái được và không được hủy trong chuỗi có thứ tự; (b) biên của ID đơn hàng; (c) độ dài/dạng chuỗi `status` sát giá trị hợp lệ; (d) biên của số lần lặp một thao tác. Dùng 3 giá trị tại mỗi biên (biên−1, biên, biên+1) khi có ý nghĩa.

## 1. Chọn đại lượng có thứ tự và biên theo spec

| Đại lượng | Thứ tự / miền theo spec | Biên | Đóng/Mở | Giá trị kiểm thử | Nguồn |
|---|---|---|---|---|---|
| Vị trí trạng thái trong chuỗi `pending(0) < confirmed(1) < shipping(2) < delivered(3)` — **User được hủy** | chỉ vị trí 0–1 | giữa 1 và 2 | đóng ở 1 | pending (min), confirmed (max cho phép), shipping (biên+1), delivered | FR-10 dòng 150–161 |
| Khoảng cách chuyển trạng thái (số bước tiến) | chỉ +1 hợp lệ | +1 | đóng | −2, −1 (ngược), +1, +2, +3 (bỏ bước) | FR-10 sơ đồ |
| ID đơn hàng | các ID có trong DB: 1..N (N = đơn mới nhất) | 1 và N | đóng | 0, −1, **1**, **N**, **N+1**, `abc`, `1.5`, 9223372036854775808 | FR-10 / API 6.2 |
| Chuỗi `status` hợp lệ `confirmed` (9 ký tự) | đúng 1 giá trị | độ dài 9 | đóng | `confirme` (8), `confirmed` (9), `confirmedd` (10), có khoảng trắng đầu/cuối | FR-10 dòng 143–156 |
| Số lần hủy cùng một đơn | tối đa 1 lần (sau đó là trạng thái cuối) | 1 | đóng | lần 1, lần 2 | FR-10 dòng 160 |
| Số bước trong chuỗi tiến tới trạng thái cuối | 3 bước (`pending→confirmed→shipping→delivered`) | 3 | đóng | bước 1–3 thành công, bước thứ 4 bị từ chối | FR-10 dòng 145–160 |

## 2. Test case BVA

Điều kiện chung: trước nhóm này, xóa bảng `orders` và tạo 3 đơn `pending` mới cho `test@eshop.com` để có ID **1, 2, 3** (N = 3, N+1 = 4); các test cần đơn riêng thì tạo thêm đơn mới và dùng ID của nó. Người gọi là Admin (`admin@eshop.com`) trừ khi nói khác.

### 2.1 ID đơn hàng (`PUT /api/admin/orders/:id/status`, body `{"status":"confirmed"}`)
| TC ID | `:id` | Vị trí so với biên | Expected (theo spec) |
|---|---|---|---|
| FR10-BV-01 | `0` | biên−1 (dưới ID nhỏ nhất) | 404 Order not found |
| FR10-BV-02 | `-1` | cực trị thấp | 404 |
| FR10-BV-03 | `1` | **biên** (ID nhỏ nhất, đang `pending`) | Chấp nhận, đơn 1 = confirmed |
| FR10-BV-04 | `3` (= N) | **biên** (ID lớn nhất, đang `pending`) | Chấp nhận, đơn 3 = confirmed |
| FR10-BV-05 | `4` (= N+1) | biên+1 | 404 |
| FR10-BV-06 | `abc` | sai kiểu | 404 (không phải 500), server sống |
| FR10-BV-07 | `1.5` | sai kiểu | 404, không đổi đơn nào |
| FR10-BV-08 | `9223372036854775808` | cực trị cao | 404, không lỗi server |

### 2.2 ID đơn hàng trên API User hủy (`PUT /api/orders/:id/cancel`, token chủ đơn)
| TC ID | `:id` | Vị trí so với biên | Expected (theo spec) |
|---|---|---|---|
| FR10-BV-09 | `0` | biên−1 | 404 |
| FR10-BV-10 | N+1 | biên+1 | 404 |

### 2.3 Chuỗi tiến tới trạng thái cuối và số lần lặp
| TC ID | Kịch bản | Vị trí so với biên | Expected (theo spec) |
|---|---|---|---|
| FR10-BV-11 | Đơn mới: `pending→confirmed→shipping→delivered` (3 bước), rồi thử bước thứ 4 `delivered→canceled` | bước 3 = biên; bước 4 = biên+1 | 3 bước đầu thành công; bước 4 bị từ chối, vẫn `delivered` |
| FR10-BV-12 | User hủy đơn `pending` của mình hai lần liên tiếp | lần 1 = biên; lần 2 = biên+1 | Lần 1 thành công; lần 2 bị từ chối (đã là trạng thái cuối) |

### 2.4 Chuỗi `status` sát giá trị hợp lệ (đơn `pending`)
| TC ID | `status` | Vị trí so với biên | Expected (theo spec) |
|---|---|---|---|
| FR10-BV-13 | `confirme` (8 ký tự) | độ dài−1 | Từ chối, không đổi |
| FR10-BV-14 | `confirmed` (9 ký tự) | **biên** | Chấp nhận, = confirmed |
| FR10-BV-15 | `confirmedd` (10 ký tự) | độ dài+1 | Từ chối, không đổi |
| FR10-BV-16 | ` confirmed` (khoảng trắng đầu) | sát biên | Từ chối, không đổi |
| FR10-BV-17 | `confirmed ` (khoảng trắng cuối) | sát biên | Từ chối, không đổi |

## 3. Tham chiếu chéo với Domain Testing
Các biên còn lại đã có ở `02_domain_testing.md`, không lặp lại:
- **Ranh giới hủy của User** (vị trí 0, 1, 2, 3): DT-26 (pending), DT-27 (confirmed), **DT-28 (shipping = biên+1)**, DT-29 (delivered), DT-30 (canceled); trên UI: DT-49..DT-53.
- **Khoảng cách bước chuyển:** +1 hợp lệ: DT-02, 08, 14; **+2 (bỏ bước):** DT-03 (pending→shipping), DT-09 (confirmed→delivered); **+3:** DT-04 (pending→delivered); **−1 / −2 (ngược):** DT-06, DT-11, DT-12, DT-17, DT-18, DT-21..DT-23.
- **Giá trị `status` sai kiểu/định dạng:** DT-37..DT-41 (rỗng, lạ, sai hoa/thường, null, số).

## 4. Thống kê
- **17** test case BVA (BV-01..BV-17).
- Cùng 54 test Domain Testing → **71** test case thiết kế cho FR-10.

## 5. Giới hạn
- ID `1.5` và `9223372036854775808` kiểm tra khả năng chịu lỗi của truy vấn (tham số SQL); spec không nêu hành vi cụ thể nên expected chỉ ở mức "không lỗi server, không đổi dữ liệu".
- Không có biên thời gian hay số tiền nào liên quan trực tiếp tới FR-10 trong SRS.
