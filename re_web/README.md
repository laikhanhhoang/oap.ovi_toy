# Cấu trúc page metadata (OAP)

Phân cấp: `layout` → `pane` → `region` → `field`

## layout
Quy định cách chia bố cục tổng thể của trang.
- `type: "grid"` — lưới đơn giản, không chia pane/sidebar/tab.
- `type: "splitter"` — chia trang thành nhiều pane có thể kéo giãn/thu gọn. Có `orientation: "horizontal"` (trái-phải) hoặc `"vertical"` (trên-dưới).

## pane
Chỉ tồn tại khi `layout.type: "splitter"`. Mỗi pane là một khung con của trang.
- `id`: định danh pane
- `size`: độ rộng/cao (`"260px"` cố định hoặc `"1fr"` chiếm phần còn lại)
- `collapsible`, `resizable`: cho phép thu gọn / kéo giãn
- `regionIds`: danh sách region hiển thị bên trong pane đó (có thể nhiều region xếp chồng dọc)

## region
Khung chứa nội dung, nằm bên trong 1 pane (hoặc trực tiếp trong `regions[]` nếu dùng `layout.type: "grid"`).
- `id`: phải khớp với `regionIds` khai ở pane
- `type: "card"` (khung có viền/tiêu đề) hoặc `"plain"` (không viền)
- `fields[]`: danh sách field bên trong region

## field
Đơn vị nhỏ nhất — 1 ô input, nút, bảng, biểu đồ... nằm trong `region.fields[]`.
- `name`: tên field (dùng làm key dữ liệu)
- `type`: loại field — input (text, number, date...), selection (select, combobox, radio...), layout (datagrid, dx-toolbar, container...), advanced (chart, widget, dashboard, kanban...)
- `label`: nhãn hiển thị
- `layout.col` / `colSpan`: vị trí trên hệ lưới 12 cột bên trong region

## Ví dụ minh họa

```json
{
  "layout": {
    "type": "splitter",
    "orientation": "horizontal",
    "panes": [
      { "id": "filters_pane", "size": "260px", "collapsible": true, "regionIds": ["filter_region"] },
      { "id": "center", "size": "1fr", "regionIds": ["kpi_region", "list_region"] }
    ]
  },
  "regions": [
    { "id": "filter_region", "type": "card", "fields": [ /* field lọc f_* */ ] },
    { "id": "kpi_region", "type": "plain", "fields": [ /* field widget KPI */ ] },
    { "id": "list_region", "type": "plain", "fields": [ /* field datagrid */ ] }
  ]
}
```

# Database

Schema: `ERP` (quyền: SELECT, INSERT, UPDATE, DELETE)

## RE_PRODUCTS
Sản phẩm bất động sản. PK: `RPR_ID`

| Cột | Kiểu | Bắt buộc | Default | Mô tả |
|---|---|---|---|---|
| RPR_ID | NUMBER | có | — | Khóa chính, định danh duy nhất sản phẩm |
| OUN_ID | NUMBER | có | — | Đơn vị tổ chức sở hữu/quản lý sản phẩm |
| LEN_ID | NUMBER | có | — | Pháp nhân quản lý sản phẩm |
| PROJ_ID | NUMBER | có | — | Dự án mà sản phẩm thuộc về |
| ZONE_NAME | VARCHAR2(400) | có | — | Tên khu vực/phân khu trong dự án |
| RPR_CODE | VARCHAR2(200) | có | — | Mã sản phẩm (vd số căn hộ, mã lô đất) |
| RPR_CATEGORY | VARCHAR2(80) | không | — | Loại sản phẩm (căn hộ, biệt thự, đất nền...) — có thể là LOV |
| RPG_ID | NUMBER | có | — | Nhóm sản phẩm chứa sản phẩm này — FK → RE_PRODUCT_GROUPS.RPG_ID |
| HOT | VARCHAR2(80) | có | 'N' | Đánh dấu sản phẩm nổi bật ("hot") |
| MAIN_DIRECTION | VARCHAR2(80) | không | — | Hướng chính của căn hộ/nhà |
| AREA_PRIMARY | NUMBER | không | — | Diện tích chính (thông thủy/sử dụng) |
| AREA_SECONDARY | NUMBER | không | — | Diện tích phụ (tim tường hoặc phần phụ) |
| FLOOR_NO | VARCHAR2(80) | không | — | Tầng số mấy |
| BEDROOM_COUNT | NUMBER | không | — | Số phòng ngủ |
| BALCONY_DIRECTION | VARCHAR2(80) | không | — | Hướng ban công |
| RESIDENT | VARCHAR2(80) | không | — | Tình trạng cư dân/đang ở |
| FLOOR_COUNT | NUMBER | không | — | Tổng số tầng của tòa nhà |
| LAND_OR_BUILD | NUMBER | không | — | Phân loại đất hay công trình xây dựng |
| AMOUNT | NUMBER | có | NULL | Giá trị/số tiền của sản phẩm |
| TAX_ID | NUMBER | không | — | Mã thuế áp dụng |
| MAINTENANCE_FEE | NUMBER | không | 0 | Phí bảo trì |
| TOTAL_AMOUNT | NUMBER | có | NULL | Tổng giá trị (đã gồm phụ phí) |
| ACC_ID | VARCHAR2(160) | không | — | Tài khoản kế toán liên kết |
| REVENUE_ACC_ID | VARCHAR2(160) | không | — | Tài khoản hạch toán doanh thu |
| COST_ACC_ID | VARCHAR2(160) | không | — | Tài khoản hạch toán giá vốn |
| LOCK_VERSION | NUMBER | có | 0 | Số phiên bản khóa lạc quan (optimistic lock), tránh ghi đè dữ liệu |
| LOCKED_BY | NUMBER | không | — | Người đang giữ khóa bản ghi |
| LOCKED_AT | TIMESTAMP(6) | không | — | Thời điểm khóa bản ghi |
| LOCK_EXPIRE_AT | TIMESTAMP(6) | không | — | Thời điểm hết hạn khóa |
| STATUS | VARCHAR2(80) | có | 'AVAILABLE' | Trạng thái sản phẩm (còn hàng, đã bán...) — có thể là LOV |
| CREATED_BY | VARCHAR2(200) | không | — | Người tạo bản ghi |
| CREATED_AT | TIMESTAMP(6) | không | CURRENT_TIMESTAMP | Thời điểm tạo bản ghi |
| MODIFIED_BY | VARCHAR2(200) | không | — | Người sửa gần nhất |
| MODIFIED_AT | TIMESTAMP(6) | không | — | Thời điểm sửa gần nhất |
| UNIT_PRICE | NUMBER | không | — | Đơn giá |
| POSITION_TYPE | VARCHAR2(80) | không | — | Loại vị trí (căn góc, căn giữa...) — có thể là LOV |
| AXIS_CODE | VARCHAR2(160) | không | — | Mã trục căn hộ |
| BLOCK_NAME | VARCHAR2(400) | không | — | Tên tòa/block |
| ROAD_FACE | VARCHAR2(800) | không | — | Mặt tiền đường |
| LAND_AREA | NUMBER | không | — | Diện tích đất |
| BUILD_AREA | NUMBER | không | — | Diện tích xây dựng |
| LAND_UNIT_PRICE | NUMBER | không | — | Đơn giá đất |
| LAND_AMOUNT | NUMBER | không | — | Thành tiền phần đất |
| BUILD_UNIT_PRICE | NUMBER | không | — | Đơn giá xây dựng |
| BUILD_AMOUNT | NUMBER | không | — | Thành tiền phần xây dựng |
| ORIGINAL_PRICE | NUMBER | không | 0 | Giá gốc trước chiết khấu |
| DISCOUNT_PERCENT | NUMBER | không | 0 | Phần trăm chiết khấu |
| TREND_DATA | VARCHAR2(2000) | không | — | Dữ liệu xu hướng giá (lưu lịch sử biến động) |
| DESCRIPTION | VARCHAR2(4000) | không | — | Mô tả chi tiết bổ sung về sản phẩm (textarea) |

## RE_PRODUCT_GROUPS
Nhóm sản phẩm bất động sản (cây phân cấp). PK: `RPG_ID`

| Cột | Kiểu | Bắt buộc | Default | Mô tả |
|---|---|---|---|---|
| RPG_ID | NUMBER | có | — | Khóa chính, định danh duy nhất nhóm sản phẩm |
| OUN_ID | NUMBER | có | — | Đơn vị tổ chức sở hữu/quản lý nhóm |
| LEN_ID | NUMBER | có | — | Pháp nhân quản lý nhóm |
| RPR_CATEGORY | VARCHAR2(80) | có | — | Loại sản phẩm áp dụng cho nhóm (căn hộ, đất nền...) — có thể là LOV |
| PGR_CLASS | VARCHAR2(80) | có | — | Phân loại nhóm (class) — có thể là LOV |
| RPG_CODE | VARCHAR2(400) | có | — | Mã nhóm sản phẩm |
| RPG_NAME | VARCHAR2(2000) | có | — | Tên nhóm sản phẩm |
| DESCRIPTION | VARCHAR2(4000) | không | — | Mô tả chi tiết về nhóm (textarea) |
| IS_PARENT | VARCHAR2(4) | có | 'N' | Đánh dấu đây có phải nhóm cha (có nhóm con) hay không |
| WBS_LEVEL | NUMBER | không | — | Cấp bậc trong cây phân cấp |
| PARENT_RPG_ID | NUMBER | không | — | Nhóm cha trực tiếp — FK tự trỏ về chính bảng này, dùng dựng cây phân cấp |
| STATUS | VARCHAR2(4) | có | 'Y' | Trạng thái hoạt động của nhóm — có thể là LOV |
| CREATED_BY | VARCHAR2(200) | không | — | Người tạo bản ghi |
| CREATED_AT | TIMESTAMP(6) | không | CURRENT_TIMESTAMP | Thời điểm tạo bản ghi |
| MODIFIED_BY | VARCHAR2(200) | không | — | Người sửa gần nhất |
| MODIFIED_AT | TIMESTAMP(6) | không | — | Thời điểm sửa gần nhất |

```
Nhóm sản phẩm BĐS (RE_PRODUCT_GROUPS)
│
├── [37] KCN — Khu công nghiệp (INDUSTRIAL, class I)
│   ├── [50] LDT — Lô đất công nghiệp
│   ├── [51] NX  — Nhà xưởng
│   └── [52] KB  — Kho bãi
│
├── [38] CT — Cao tầng (RESIDENTIAL, class H)
│   ├── [53] CH — Căn hộ
│   └── [56] PH — Penthouse
│
└── [39] TT — Thấp tầng (RESIDENTIAL, class L)
    ├── [57] BT — Biệt thự
    ├── [58] NP — Nhà phố
    ├── [59] SH — Shophouse
    └── [60] DN — Đất nền
```

3 nhóm gốc (`PARENT_RPG_ID = null`, `IS_PARENT = 'Y'`) ở `WBS_LEVEL` 1; 9 nhóm con (`IS_PARENT = 'N'`) ở `WBS_LEVEL` 2. Không có nhóm nào ở cấp 3.