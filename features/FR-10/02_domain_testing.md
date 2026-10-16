# FR-10: Máy trạng thái đơn hàng — Domain Testing

Oracle: SRS `README.md` (FR-10 dòng 141–162; FR-12 dòng 176–179; FR-21 dòng 244; SEC-03 dòng 280). Chi tiết và điểm mơ hồ ở `01_analysis.md`.

Quy ước:
- Miền đầu vào chính của feature là **cặp (trạng thái hiện tại × trạng thái đích)**, hữu hạn 5 × 5 nên mỗi ô là một lớp tương đương và được test đủ.
- Mỗi test không hợp lệ chỉ vi phạm **một** điều kiện; các điều kiện còn lại hợp lệ (đúng chủ đơn/đúng vai trò, id tồn tại).
- Sau mỗi test không hợp lệ, kiểm tra **trạng thái đơn trong DB không đổi**.
- Cột **Lớp chạy**: `API` = HTTP trực tiếp `localhost:3000`; `UI-Admin` = Web Admin `:5174`; `UI-Web` = Web user `:5173/profile`.
- Dữ liệu: mỗi test tạo đơn `pending` mới bằng `POST /api/checkout` (user `test@eshop.com`), rồi đưa tới trạng thái nguồn bằng các chuyển hợp lệ qua API Admin (`admin@eshop.com` / `Admin123!`).

## 1. Lớp tương đương

### 1.1 (trạng thái hiện tại × trạng thái đích) — gọi bởi Admin
Chiều hợp lệ theo sơ đồ SRS: ✔ = được phép, ✘ = phải bị từ chối (400, trạng thái không đổi).

| Hiện tại \ Đích | pending | confirmed | shipping | delivered | canceled |
|---|---|---|---|---|---|
| **pending** | ✘ | ✔ | ✘ | ✘ | ✔ |
| **confirmed** | ✘ | ✘ | ✔ | ✘ | ✔ |
| **shipping** | ✘ | ✘ | ✘ | ✔ | ✘ (*) |
| **delivered** (cuối) | ✘ | ✘ | ✘ | ✘ | ✘ |
| **canceled** (cuối) | ✘ | ✘ | ✘ | ✘ | ✘ |

(*) Diễn giải chặt: sơ đồ SRS không có `shipping → canceled`; xem điểm mơ hồ ở `01_analysis.md`.
Tổng: 5 ô hợp lệ + 20 ô không hợp lệ. Mã lớp: `EC-M-<hiện tại>-<đích>`.

### 1.2 Người thực hiện (actor) và quyền
| Mã lớp | Mô tả |
|---|---|
| EC-act-V1 | Admin (token `role=admin`) gọi API Admin |
| EC-act-V2 | User đã đăng nhập, **chủ đơn**, gọi hủy đơn |
| EC-act-I1 | Không có token |
| EC-act-I2 | User thường (`role=user`) gọi API Admin |
| EC-act-I3 | User hủy đơn của **người khác** |

### 1.3 Đơn hàng được chỉ định
| Mã lớp | Mô tả |
|---|---|
| EC-ord-V1 | `id` của đơn tồn tại |
| EC-ord-I1 | `id` không tồn tại |

### 1.4 Giá trị `status` trong body
| Mã lớp | Mô tả | Ví dụ |
|---|---|---|
| EC-sv-V1 | Một trong 5 giá trị hợp lệ (viết thường) | `confirmed` |
| EC-sv-I1 | Chuỗi rỗng | `""` |
| EC-sv-I2 | Chuỗi lạ | `refunded` |
| EC-sv-I3 | Sai chữ hoa/thường | `CONFIRMED` |
| EC-sv-I4 | `null` | `null` |
| EC-sv-I5 | Sai kiểu (số) | `123` |

### 1.5 Giao diện
| Mã lớp | Mô tả |
|---|---|
| EC-gui-A-<trạng thái> | Web Admin: tập nút hành động hiển thị cho đơn ở trạng thái đó chỉ gồm chuyển hợp lệ |
| EC-gui-W-<trạng thái> | Web user (Profile): nút "Hủy đơn" chỉ hiển thị khi `pending`/`confirmed` |
| EC-gui-err | Thông báo lỗi khi chuyển không hợp lệ rõ ràng, tiếng Việt (FR-21) |

## 2. Test case

### 2.1 Ma trận chuyển trạng thái (API Admin) — Expected theo SRS
| TC ID | Lớp | Hiện tại → Đích | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR10-DT-01 | EC-M-pending-pending | pending → pending | Từ chối (400), không đổi | API |
| FR10-DT-02 | EC-M-pending-confirmed | pending → confirmed | Chấp nhận (200), trạng thái = confirmed | API |
| FR10-DT-03 | EC-M-pending-shipping | pending → shipping | Từ chối (bỏ qua `confirmed`) | API |
| FR10-DT-04 | EC-M-pending-delivered | pending → delivered | Từ chối | API |
| FR10-DT-05 | EC-M-pending-canceled | pending → canceled | Chấp nhận, trạng thái = canceled | API |
| FR10-DT-06 | EC-M-confirmed-pending | confirmed → pending | Từ chối (không chuyển ngược) | API |
| FR10-DT-07 | EC-M-confirmed-confirmed | confirmed → confirmed | Từ chối | API |
| FR10-DT-08 | EC-M-confirmed-shipping | confirmed → shipping | Chấp nhận, = shipping | API |
| FR10-DT-09 | EC-M-confirmed-delivered | confirmed → delivered | Từ chối (bỏ qua `shipping`) | API |
| FR10-DT-10 | EC-M-confirmed-canceled | confirmed → canceled | Chấp nhận, = canceled | API |
| FR10-DT-11 | EC-M-shipping-pending | shipping → pending | Từ chối | API |
| FR10-DT-12 | EC-M-shipping-confirmed | shipping → confirmed | Từ chối | API |
| FR10-DT-13 | EC-M-shipping-shipping | shipping → shipping | Từ chối | API |
| FR10-DT-14 | EC-M-shipping-delivered | shipping → delivered | Chấp nhận, = delivered | API |
| FR10-DT-15 | EC-M-shipping-canceled | shipping → canceled | Từ chối (diễn giải chặt) | API |
| FR10-DT-16 | EC-M-delivered-pending | delivered → pending | Từ chối (trạng thái cuối) | API |
| FR10-DT-17 | EC-M-delivered-confirmed | delivered → confirmed | Từ chối | API |
| FR10-DT-18 | EC-M-delivered-shipping | delivered → shipping | Từ chối | API |
| FR10-DT-19 | EC-M-delivered-delivered | delivered → delivered | Từ chối | API |
| FR10-DT-20 | EC-M-delivered-canceled | delivered → canceled | Từ chối | API |
| FR10-DT-21 | EC-M-canceled-pending | canceled → pending | Từ chối (trạng thái cuối) | API |
| FR10-DT-22 | EC-M-canceled-confirmed | canceled → confirmed | Từ chối | API |
| FR10-DT-23 | EC-M-canceled-shipping | canceled → shipping | Từ chối | API |
| FR10-DT-24 | EC-M-canceled-delivered | canceled → delivered | Từ chối (`canceled` là trạng thái cuối) | API |
| FR10-DT-25 | EC-M-canceled-canceled | canceled → canceled | Từ chối | API |

### 2.2 User hủy đơn của chính mình (`PUT /api/orders/:id/cancel`)
| TC ID | Lớp | Trạng thái đơn | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR10-DT-26 | EC-act-V2 | pending | Chấp nhận, = canceled | API |
| FR10-DT-27 | EC-act-V2 | confirmed | Chấp nhận, = canceled | API |
| FR10-DT-28 | EC-act-V2 | shipping | **Từ chối** (User không được hủy khi shipping), không đổi | API |
| FR10-DT-29 | EC-act-V2 | delivered | Từ chối, không đổi | API |
| FR10-DT-30 | EC-act-V2 | canceled | Từ chối, không đổi | API |

### 2.3 Quyền và đối tượng
| TC ID | Lớp | Dữ liệu vào | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR10-DT-31 | EC-act-I1 | Admin API, không token, pending → confirmed | 401, không đổi | API |
| FR10-DT-32 | EC-act-I1 | Hủy đơn, không token | 401, không đổi | API |
| FR10-DT-33 | EC-act-I2 | Token User thường gọi Admin API pending → confirmed | Từ chối (403), không đổi (FR-12, SEC-03) | API |
| FR10-DT-34 | EC-act-I3 | User B hủy đơn pending của User A | Từ chối, đơn A không đổi | API |
| FR10-DT-35 | EC-ord-I1 | Admin API, id không tồn tại | 404 | API |
| FR10-DT-36 | EC-ord-I1 | User hủy, id không tồn tại | 404 | API |

### 2.4 Giá trị `status` không hợp lệ (đơn đang `pending`, Admin)
| TC ID | Lớp | `status` | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR10-DT-37 | EC-sv-I1 | `""` | Từ chối (400), không đổi | API |
| FR10-DT-38 | EC-sv-I2 | `refunded` | Từ chối, không đổi | API |
| FR10-DT-39 | EC-sv-I3 | `CONFIRMED` | Từ chối, không đổi | API |
| FR10-DT-40 | EC-sv-I4 | `null` | Từ chối, không đổi | API |
| FR10-DT-41 | EC-sv-I5 | `123` | Từ chối, không đổi | API |

### 2.5 Luồng nghiệp vụ
| TC ID | Lớp | Kịch bản | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR10-DT-42 | EC-M (chuỗi hợp lệ) | pending → confirmed → shipping → delivered | Mỗi bước thành công; sau `delivered` mọi chuyển tiếp bị từ chối | API |
| FR10-DT-43 | EC-M, EC-act-V2 | pending → confirmed → User hủy → thử `canceled → delivered` | Hủy thành công; chuyển tiếp từ `canceled` bị từ chối | API |

### 2.6 Giao diện
| TC ID | Lớp | Trạng thái đơn | Expected (theo spec) | Lớp chạy |
|---|---|---|---|---|
| FR10-DT-44 | EC-gui-A-pending | pending | Chỉ nút "Xác nhận", "Hủy" | UI-Admin |
| FR10-DT-45 | EC-gui-A-confirmed | confirmed | Chỉ nút "Giao hàng", "Hủy" | UI-Admin |
| FR10-DT-46 | EC-gui-A-shipping | shipping | Chỉ nút "Hoàn thành" | UI-Admin |
| FR10-DT-47 | EC-gui-A-delivered | delivered | Không có nút hành động | UI-Admin |
| FR10-DT-48 | EC-gui-A-canceled | canceled | Không có nút hành động (trạng thái cuối) | UI-Admin |
| FR10-DT-49 | EC-gui-W-pending | pending | Có nút "Hủy đơn" | UI-Web |
| FR10-DT-50 | EC-gui-W-confirmed | confirmed | Có nút "Hủy đơn" | UI-Web |
| FR10-DT-51 | EC-gui-W-shipping | shipping | **Không** có nút "Hủy đơn" | UI-Web |
| FR10-DT-52 | EC-gui-W-delivered | delivered | Không có nút "Hủy đơn" | UI-Web |
| FR10-DT-53 | EC-gui-W-canceled | canceled | Không có nút "Hủy đơn" | UI-Web |
| FR10-DT-54 | EC-gui-err | Màn hình Admin đang hiển thị đơn `pending` (cũ), trong lúc đó đơn đã chuyển `confirmed` bằng API; bấm "Xác nhận" | Thông báo lỗi rõ ràng, **tiếng Việt**, không lộ chi tiết kỹ thuật | UI-Admin |

## 3. Truy vết lớp → test
| Nhóm lớp | Test phủ |
|---|---|
| EC-M (25 ô) | DT-01..DT-25 (mỗi ô một test), DT-42, DT-43 (chuỗi) |
| EC-act-V1 / V2 | DT-02, 05, 08, 10, 14 (Admin); DT-26, 27 (chủ đơn) |
| EC-act-I1 | DT-31, DT-32 |
| EC-act-I2 | DT-33 |
| EC-act-I3 | DT-34 |
| EC-ord-V1 / I1 | mọi test khác / DT-35, DT-36 |
| EC-sv-V1 | DT-02, 08, 10 (và các ô hợp lệ khác) |
| EC-sv-I1..I5 | DT-37..DT-41 |
| EC-gui-A-* | DT-44..DT-48 |
| EC-gui-W-* | DT-49..DT-53 |
| EC-gui-err | DT-54 |

Tổng: **54** test case Domain Testing; mọi lớp đều có ít nhất một test.

## 4. Giới hạn và giả định
- Hủy đơn trên Mobile không thuộc phạm vi (feature của thành viên khác); logic backend dùng chung đã được test qua API.
- `shipping → canceled` do Admin (DT-15) phụ thuộc diễn giải "chỉ Admin mới có thể thao tác" (xem `01_analysis.md`); nếu kết quả khác diễn giải, ghi "theo diễn giải chặt", không coi chắc chắn là bug.
- DT-54 cần tạo tình huống dữ liệu cũ (stale) trên Web Admin vì giao diện không cho bấm hành động không hợp lệ ở trạng thái mới nhất.
