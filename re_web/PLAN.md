# Kế hoạch xây dựng `index.json` + `search.json` (app `rem`)

## 1. Mục tiêu

- **`index.json`** — trang chủ giới thiệu các loại BĐS: tiêu đề căn giữa, 3 widget nhóm cha, nút mở rộng để lộ thêm 9 widget nhóm con (tổng 12), bấm vào 1 widget sẽ điều hướng sang trang search kèm loại BĐS đã chọn.
- **`search.json`** — trang tìm kiếm sản phẩm BĐS: layout 2 cột co giãn (splitter kéo được), trái là form lọc, phải là kết quả (datagrid).

Cả 2 trang dùng chung dữ liệu `ERP.RE_PRODUCTS` / `ERP.RE_PRODUCT_GROUPS` (xem `interface/README.md`).

## 2. Đã tra cứu qua mcp `oap-devkit` (không đoán mò)

| Câu hỏi | Kết luận | Nguồn |
|---|---|---|
| Field nào hiển thị tên + mô tả, bấm được để điều hướng? | `type: "card-region"` (props: `displayAs`, `config.{titleField,subtitleField,badgeField,imageField,iconField,colSpan,actions}`, `data`). Đây là loại **duy nhất** hỗ trợ trigger `onCardClick`. Field `widget` chỉ hiển thị 1 con số KPI, **không** hỗ trợ click/navigate — không dùng được cho yêu cầu này. | `get_registry(fields)`, compatibility-matrix Section D/F |
| Nút "mở rộng" | `type: "action-button"` (props: `label, icon, variant, stylingMode, actionConfig, disabledWhen, visibleWhen`). Kết hợp `pageEvents` (`onClick` → action `toggle`, target = id của region chứa 9 widget con) để ẩn/hiện. | `get_registry(fields, layout)`, `get_registry(events)` |
| Ẩn 9 widget con lúc mới vào trang | Không có prop "collapsed" sẵn trên field/region — dùng `pageEvents onLoad` → action `hide` target region con, rồi `onClick` nút mở rộng → action `toggle` cùng target. | `get_registry(events)` (actions `show/hide/toggle` nhận target là field **hoặc region**) |
| Tiêu đề căn giữa | `type: "heading"`, prop `textAlign: "center"` (enum `left/center/right`, áp dụng mọi field type). | `get_registry(fields, layout)`, compatibility-matrix Section C.3 |
| Splitter 2 cột kéo giãn | `layout.type: "splitter"`, `orientation: "horizontal"`, pane có `size`, `collapsible: true`, `resizable: true`. Không có prop min/max size (không cần cho yêu cầu này). | `layout-patterns` resource, README.md |
| LOV cho `RPG_ID` | 3 LOV liên quan: `LOV_RE_PRODUCT_GROUP` (tất cả nhóm, gắn với `RE_PRODUCTS.RPG_ID`), `LOV_REM_PRODUCT_GROUP_PARENT` (chỉ nhóm cha), `LOV_RE_PRODUCT`. Dùng `LOV_RE_PRODUCT_GROUP` cho filter search vì cần chọn được cả cấp cha lẫn cấp con. | `find_lov(columnName: "RPG_ID")` |
| `RE_PRODUCTS.RPG_ID` trỏ vào cấp nào của cây nhóm? | Đã `execute_sql` kiểm tra thực tế: **toàn bộ sản phẩm chỉ gắn `RPG_ID` ở cấp con** (`IS_PARENT='N'`), không sản phẩm nào gắn thẳng vào 1 trong 3 nhóm cha. ⇒ Khi filter/điều hướng bằng `RPG_ID` của nhóm **cha**, SQL phải match luôn `rpg.PARENT_RPG_ID = :p_rpg_id` (không chỉ `rpg.RPG_ID = :p_rpg_id`), giống cách trang có sẵn `rem_price_list` đang làm. | `execute_sql` trực tiếp trên `ERP.RE_PRODUCTS` |
| Có trang mẫu tương tự chưa? | Có — `rem_price_list` (`inspect_page`) dùng đúng pattern splitter + widget + datagrid + bindVariables theo filter, và câu WHERE `(:p_rpg_id IS NULL OR rpg.PARENT_RPG_ID = :p_rpg_id OR rpg.RPG_ID = :p_rpg_id)` y hệt nhu cầu search.json → tái dùng logic này. | `list_pages(searchTableName: RE_PRODUCTS)`, `inspect_page(rem_price_list)` |
| Điều hướng kèm giá trị điền sẵn (index → search) | Cơ chế **đã xác nhận chắc chắn**: mở page B dạng **modal/popup** (`modalConfig.params`) → page B `onLoad` → `setValue target: "..." value: "{{PARAMS.xxx}}"`. Cơ chế **navigate URL kèm query string tới 1 trang độc lập (không phải modal)** chỉ có `{type:"navigate", url}` được tài liệu hoá — phần binding query string → `{{PARAMS.xxx}}` cho *trang độc lập* (không phải modal) **không có ví dụ xác nhận** trong `page-events`/`frontend-runtime-contracts`. ⇒ Đây là điểm rủi ro duy nhất, xử lý ở mục 5. | `page-events`, `frontend-runtime-contracts`, `layout-patterns` resources |

## 3. Trang `index.json`

```json
{
  "pageCode": "REM_HOME_INDEX",
  "pageType": "form",
  "title": "Trang chủ",
  "dataSource": { "type": "none" },
  "layout": { "type": "default" },
  "regions": [
    {
      "id": "hero_region",
      "type": "plain",
      "fields": [
        { "name": "hero_title", "type": "heading", "level": 1, "textAlign": "center",
          "text": "Tự do lựa chọn loại bất động sản phù hợp nhu cầu của bạn",
          "layout": { "colSpan": 12 } }
      ]
    },
    {
      "id": "parent_groups_region",
      "type": "plain",
      "fields": [
        { "name": "btn_expand", "type": "action-button", "icon": "chevron-down",
          "label": "", "variant": "default", "stylingMode": "outlined",
          "layout": { "col": 1, "colSpan": 1 } },
        { "name": "card_parent_groups", "type": "card-region", "displayAs": "card-grid",
          "layout": { "col": 2, "colSpan": 11 },
          "config": { "titleField": "RPG_NAME", "subtitleField": "DESCRIPTION", "colSpan": 4 },
          "dataSource": {
            "type": "query",
            "query": "SELECT RPG_ID, RPG_NAME, DESCRIPTION FROM ERP.RE_PRODUCT_GROUPS WHERE PARENT_RPG_ID IS NULL AND STATUS = 'Y' ORDER BY RPG_ID"
          } }
      ]
    },
    {
      "id": "child_groups_region",
      "type": "plain",
      "fields": [
        { "name": "card_child_groups", "type": "card-region", "displayAs": "card-grid",
          "layout": { "colSpan": 12 },
          "config": { "titleField": "RPG_NAME", "subtitleField": "DESCRIPTION", "colSpan": 3 },
          "dataSource": {
            "type": "query",
            "query": "SELECT RPG_ID, RPG_NAME, DESCRIPTION, PARENT_RPG_ID FROM ERP.RE_PRODUCT_GROUPS WHERE PARENT_RPG_ID IS NOT NULL AND STATUS = 'Y' ORDER BY PARENT_RPG_ID, RPG_ID"
          } }
      ]
    }
  ],
  "pageEvents": [
    { "name": "init_hide_child_groups", "trigger": "onLoad",
      "actions": [ { "type": "hide", "target": "child_groups_region" } ] },
    { "name": "toggle_child_groups", "trigger": "onClick", "sourceField": "btn_expand",
      "actions": [ { "type": "toggle", "target": "child_groups_region" } ] },
    { "name": "goto_search_from_parent", "trigger": "onCardClick", "sourceField": "card_parent_groups",
      "actions": [ { "type": "navigate", "url": "/rem/search?rpg_id={{ROW.RPG_ID}}" } ] },
    { "name": "goto_search_from_child", "trigger": "onCardClick", "sourceField": "card_child_groups",
      "actions": [ { "type": "navigate", "url": "/rem/search?rpg_id={{ROW.RPG_ID}}" } ] }
  ]
}
```

Ghi chú:
- 3 card cha dùng `colSpan: 4` (3×4=12/hàng), 9 card con dùng `colSpan: 3` (4/hàng × ~2.25 hàng — có thể chỉnh lại 3 hoặc 4 tùy thẩm mỹ thực tế sau khi xem preview).
- Icon nút mở rộng nên đổi `chevron-down` ↔ `chevron-up` khi toggle — cần thêm 1 action `setValue` cho `icon` nếu muốn (để sau, không chặn MVP).

## 4. Trang `search.json`

```json
{
  "pageCode": "REM_PRODUCT_SEARCH",
  "pageType": "form",
  "title": "Tìm kiếm sản phẩm BĐS",
  "dataSource": { "type": "none" },
  "layout": {
    "type": "splitter", "orientation": "horizontal",
    "panes": [
      { "id": "search_pane", "size": "320px", "collapsible": true, "regionIds": ["search_form_region"] },
      { "id": "result_pane", "size": "1fr", "regionIds": ["result_region"] }
    ]
  },
  "regions": [
    {
      "id": "search_form_region", "type": "card", "title": "Tìm kiếm",
      "fields": [
        { "name": "f_rpg_id", "type": "select", "label": "Loại bất động sản",
          "showClearButton": true, "lov": { "code": "LOV_RE_PRODUCT_GROUP" } },
        { "name": "f_min_price", "type": "number", "label": "Giá từ" },
        { "name": "f_max_price", "type": "number", "label": "Giá đến" },
        { "name": "f_min_area", "type": "number", "label": "Tổng diện tích tối thiểu (m²)" }
      ]
    },
    {
      "id": "result_region", "type": "plain",
      "fields": [
        { "name": "grid_products", "type": "datagrid", "layout": { "colSpan": 12 },
          "metadata": {
            "pageType": "table",
            "columns": [
              { "key": "RPR_CODE", "label": "Mã sản phẩm", "width": 140 },
              { "key": "RPG_NAME", "label": "Loại BĐS", "width": 160 },
              { "key": "UNIT_PRICE", "label": "Đơn giá", "dataType": "number", "alignment": "right", "width": 140 },
              { "key": "TOTAL_AREA", "label": "Tổng diện tích", "dataType": "number", "alignment": "right", "width": 130 },
              { "key": "STATUS", "label": "Trạng thái", "coloredBadge": true, "width": 120 }
            ],
            "dataSource": {
              "type": "query",
              "keyField": "RPR_ID",
              "bindVariables": [
                { "name": "p_rpg_id", "sourceField": "f_rpg_id" },
                { "name": "p_min_price", "sourceField": "f_min_price" },
                { "name": "p_max_price", "sourceField": "f_max_price" },
                { "name": "p_min_area", "sourceField": "f_min_area" }
              ],
              "query": "SELECT p.RPR_ID, p.RPR_CODE, rpg.RPG_NAME, p.UNIT_PRICE, p.STATUS, (NVL(p.AREA_PRIMARY,0) + NVL(p.AREA_SECONDARY,0)) AS TOTAL_AREA FROM ERP.RE_PRODUCTS p LEFT JOIN ERP.RE_PRODUCT_GROUPS rpg ON p.RPG_ID = rpg.RPG_ID WHERE (:p_rpg_id IS NULL OR rpg.RPG_ID = :p_rpg_id OR rpg.PARENT_RPG_ID = :p_rpg_id) AND (:p_min_price IS NULL OR p.UNIT_PRICE >= :p_min_price) AND (:p_max_price IS NULL OR p.UNIT_PRICE <= :p_max_price) AND (:p_min_area IS NULL OR (NVL(p.AREA_PRIMARY,0) + NVL(p.AREA_SECONDARY,0)) >= :p_min_area) ORDER BY p.RPR_CODE"
            },
            "tableConfig": { "height": "calc(100vh - 180px)", "pageSize": 25, "columnChooser": true }
          } }
      ]
    }
  ],
  "pageEvents": [
    { "name": "init_rpg_from_params", "trigger": "onLoad",
      "actions": [ { "type": "setValue", "target": "f_rpg_id", "value": "{{PARAMS.rpg_id}}" } ] }
  ]
}
```

Ghi chú:
- `f_min_price`/`f_max_price` so với `UNIT_PRICE` (đơn giá), đúng yêu cầu "min price, max price để so sánh với UNIT_PRICE".
- `f_min_area` so với `AREA_PRIMARY + AREA_SECONDARY`, đúng yêu cầu ">= tổng diện tích tối thiểu".
- Không cần nút "Tìm kiếm" riêng — `bindVariables` khiến grid tự refresh khi field filter đổi giá trị (theo đúng pattern `rem_price_list` đang chạy thật).

## 5. Điều hướng index → search (rủi ro cần xác minh)

Đã tra cứu kỹ (mục 2) nhưng **không tìm thấy ví dụ chính thức** cho case "navigate sang 1 trang độc lập (không phải modal) kèm query string, rồi trang đó tự đọc `{{PARAMS.xxx}}`". Pattern `{{PARAMS.xxx}}` chỉ được xác nhận rõ ràng cho **modal/popup** (`modalConfig.params` → `onLoad` → `setValue`).

⇒ Kế hoạch xử lý:
1. Cài đặt theo thiết kế ở mục 3-4 (`navigate` + query string + `onLoad` đọc `PARAMS`) như phương án chính.
2. Dùng `test_page()` / `get_page_preview()` ngay sau khi tạo để xác minh thực tế query string có tới được `PARAMS` hay không.
3. Nếu không hoạt động, phương án dự phòng (đã có tài liệu xác nhận 100%): đổi `card-region` action trên index thành mở `search.json` dưới dạng **modal** (`action: "page-popup"`, `modalConfig: { pageCode: "REM_PRODUCT_SEARCH", params: { rpg_id: "{{ROW.RPG_ID}}" } }`) thay vì `navigate` thẳng URL.

## 6. Checklist công việc

- [x] Xác nhận `appCode` (`rem`) và `workspaceCode` (`OVI_SUITE`) — dùng theo giả định (khớp các trang `rem_*` có sẵn), chưa có phản hồi khác từ người phụ trách.
- [x] `find_lov` xác nhận lại `LOV_RE_PRODUCT_GROUP` trả đủ 12 nhóm (cả cha lẫn con) trước khi gắn vào `f_rpg_id`.
- [x] Viết `re_web/index.json` theo khung mục 3.
- [x] Viết `re_web/search.json` theo khung mục 4.
- [x] `validate_metadata()` cho cả 2 file trước khi tạo trang — phát hiện & sửa 2 lỗi so với bản kế hoạch gốc (xem mục 7).
- [x] `create_page()` cho `REM_HOME_INDEX` (pageId `10665`, appCode `rem`, layout `default`).
- [x] `create_page()` cho `REM_PRODUCT_SEARCH` (pageId `10666`, appCode `rem`, layout `splitter`).
- [x] Thêm `pageEvents` (`onLoad` hide, `onClick` toggle, `onCardClick` navigate ×2) cho index qua `update_page()`.
- [x] Thêm `pageEvent` `onLoad` set `f_rpg_id` cho search qua `update_page()`.
- [x] `test_page()` cả 2 trang — `REM_HOME_INDEX`: preflight passed, 2 surface (card cha rowCount=3, card con rowCount=9, tổng đúng 12). `REM_PRODUCT_SEARCH`: runtime-verified, LOV 12 dòng, grid query chạy được.
- [x] `build_translations()` + `update_page(translations)` cho cả 2 trang — `test_page` xác nhận `translations: ✅ vi/en complete`.
- [ ] `get_page_preview()` xác minh bằng browser thật cơ chế điều hướng kèm `rpg_id` (mục 5) — **chưa làm được**, môi trường hiện tại không có browser tool. Cần người dùng tự mở `previewUrl` (xem mục 7) để xác nhận.
- [ ] Kiểm tra bằng mắt trên browser: canh giữa tiêu đề, bố cục 3+9 card, thanh kéo splitter hoạt động đúng trên `search.json` — cần browser, chưa tự làm được.
- [ ] Kiểm tra SQL search trả đúng kết quả khi lọc theo nhóm cha (VD `RPG_ID=38` phải ra sản phẩm của cả `CH` và `PH`) — đã gián tiếp xác nhận qua `test_page(sampleContext)` chạy được câu query, nhưng chưa test riêng case `f_rpg_id=38` để đối chiếu số dòng kỳ vọng.

## 7. Phát hiện thực tế khi triển khai (khác với bản kế hoạch gốc)

`validate_metadata()`/`test_page()` bắt lỗi 3 chỗ mà tài liệu registry/README mô tả sai hoặc thiếu — đã sửa trực tiếp trên DB (qua `create_page`/`update_page`) và trên file local:

1. **`layout.type: "grid"` không tồn tại.** `interface/README.md` mô tả layout có 2 loại `"grid"`/`"splitter"`, nhưng validator thực tế chỉ chấp nhận `default | sidebar | split | wide | boxed | full | splitter`. Đã đổi `index.json` sang `"default"`. **Nên cập nhật lại `interface/README.md` mục `layout`** vì tài liệu đang sai so với backend — chưa làm vì ngoài phạm vi 2 trang này, cần xác nhận thêm.
2. **`region.icon` (VD `"filter"` trên `type: "card"`) làm validate_metadata fail** dù compatibility-matrix Section C.4 liệt kê `icon` là prop hợp lệ của region. Đã bỏ `icon` khỏi `search_form_region` (chỉ mất icon trang trí, không ảnh hưởng chức năng).
3. **Quan trọng nhất: `card-region` phải dùng prop `dataSource`, không phải `data`.** Registry (`get_registry(fields)`) khai prop tên `data`, và `validate_metadata()` chấp nhận `data` mà không báo lỗi — nhưng `test_page()` cho thấy `surface_inventory: 0` (SQL không được nhận diện/thực thi). Đổi sang `dataSource` (giống convention của `widget`/`datagrid`) thì `test_page()` mới nhận diện đúng 2 surface và trả về đúng rowCount 3 (nhóm cha) + 9 (nhóm con). Nếu không phát hiện qua `test_page()`, 2 khối card trên `index.json` sẽ **hiển thị rỗng khi chạy thật** dù metadata "valid". Đã sửa cả trên DB và file `re_web/index.json`.

Rủi ro còn lại (đã nêu ở mục 5) chưa xác minh được do môi trường không có browser tool: cơ chế `navigate` + query string (`?rpg_id=...`) → trang `search.json` tự đọc `{{PARAMS.rpg_id}}` khi **không** mở qua modal. `test_page(sampleContext)` chỉ verify được câu SQL của grid chạy đúng với `pageItems` cho sẵn, **không** verify được chuỗi sự kiện `onLoad → setValue từ PARAMS` khi điều hướng bằng URL thật. Cần người dùng tự mở `get_page_preview` trong browser để xác nhận, theo phương án dự phòng đã nêu (đổi sang `page-popup` nếu không hoạt động).
