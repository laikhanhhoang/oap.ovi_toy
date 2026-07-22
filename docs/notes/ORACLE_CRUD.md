# Oracle CRUD Metadata

File này tập trung vào câu hỏi người mới hay vướng nhất:

- `loadQuery` chạy khi nào?
- `:id`, `:p_ord_id`, `:VIEW_MONTH` lấy từ đâu?
- `params[]` với `bindVariables[]` khác nhau chỗ nào?
- `saveQuery` có tự map field -> bind được không?
- OUT param trả về có được đẩy lại vào form không?

Các ví dụ dưới đây dùng canonical metadata mới: `dataSource.type: "query"`.

## 1. Muốn load được dữ liệu thì tối thiểu cần gì?

Muốn form edit load được 1 record từ Oracle, tối thiểu cần:

- `pageType: "form"`
- `dataSource.keyField`
- `dataSource.loadQuery`
- bind trong `loadQuery` phải có nguồn giá trị thật

Ví dụ tối thiểu:

```json
{
  "metadataVersion": 2,
  "pageCode": "ORDER_FORM",
  "pageType": "form",
  "title": "Đơn hàng",
  "dataSource": {
    "type": "query",
    "keyField": "ORD_ID",
    "loadQuery": "SELECT ORD_ID, ORD_CODE, ORDER_DATE, CUSTOMER_ID, STATUS FROM APPS.DEMO_ORDERS WHERE ORD_ID = :id",
    "params": [
      { "name": "id", "sourceType": "url", "sourceField": "id" }
    ]
  },
  "layout": { "type": "default" },
  "regions": [
    {
      "id": "main",
      "type": "form",
      "fields": [
        { "name": "ORD_ID", "type": "number", "label": "ID", "readOnly": true },
        { "name": "ORD_CODE", "type": "text", "label": "Mã đơn" },
        { "name": "ORDER_DATE", "type": "date", "label": "Ngày đơn" },
        { "name": "CUSTOMER_ID", "type": "select", "label": "Khách hàng", "lov": { "code": "LOV_CUSTOMERS" } },
        { "name": "STATUS", "type": "select", "label": "Trạng thái", "lov": { "code": "LOV_STATUS" } }
      ]
    }
  ]
}
```

Nếu URL là `/runtime/ORDER_FORM?id=101`, runtime sẽ lấy `id=101` và bind vào `:id`.

## 2. `:id` đến từ đâu?

Trong runtime hiện tại, form load có 3 nhóm nguồn bind chính:

1. `id` hiện tại của page.
   Runtime tự thêm bind `{ name: "id", value: currentId }` khi page đang mở record edit.

2. `dataSource.params[]`.
   Đây là config chính thống trong schema để map URL/page/global item vào bind.

3. `dataSource.bindVariables[]`.
   Dùng khi bind lấy từ field đang có trên form, hoặc từ giá trị tĩnh/default.

Nói ngắn gọn:

- bind kiểu `:id` thường lấy từ URL/search param record hiện tại
- bind kiểu `:p_month`, `:p_status`, `:p_company_id` thường nên map bằng `params[]` hoặc `bindVariables[]`

## 3. `dataSource.params[]` truyền được những gì?

Schema hiện nhận:

```json
{
  "name": "bind_name",
  "sourceType": "url | pageItem | globalItem",
  "sourceField": "ten_nguon"
}
```

### 3.1. Lấy từ URL

```json
{
  "dataSource": {
    "type": "query",
    "keyField": "ORD_ID",
    "loadQuery": "SELECT * FROM APPS.DEMO_ORDERS WHERE ORD_ID = :id",
    "params": [
      { "name": "id", "sourceType": "url", "sourceField": "id" }
    ]
  }
}
```

URL `/runtime/ORDER_FORM?id=101` -> bind `:id = 101`.

### 3.2. Lấy từ page item

```json
{
  "dataSource": {
    "type": "query",
    "loadQuery": "SELECT * FROM APPS.DEMO_ORDERS WHERE STATUS = :p_status",
    "params": [
      { "name": "p_status", "sourceType": "pageItem", "sourceField": "STATUS_FILTER" }
    ]
  }
}
```

Ý nghĩa: bind `:p_status` lấy từ field `STATUS_FILTER` trên page hiện tại.

### 3.3. Lấy từ global item

```json
{
  "dataSource": {
    "type": "query",
    "loadQuery": "SELECT * FROM APPS.DEMO_ORDERS WHERE COMPANY_ID = :p_company_id",
    "params": [
      { "name": "p_company_id", "sourceType": "globalItem", "sourceField": "G_COMPANY_ID" }
    ]
  }
}
```

Ý nghĩa: bind `:p_company_id` lấy từ global item `G_COMPANY_ID`.

## 4. `dataSource.bindVariables[]` dùng khi nào?

`params[]` hợp với URL/page/global item. `bindVariables[]` hợp với bind lấy từ field/form value hoặc gán tĩnh.

Ví dụ load detail grid theo parent form:

```json
{
  "name": "ORDER_ITEMS",
  "type": "datagrid",
  "metadata": {
    "dataSource": {
      "type": "query",
      "keyField": "LINE_ID",
      "query": "SELECT LINE_ID, ORD_ID, ITEM_NAME, QUANTITY FROM APPS.ORDER_LINES WHERE ORD_ID = :ORD_ID",
      "bindVariables": [
        { "name": "ORD_ID", "sourceField": "ORD_ID" }
      ]
    }
  }
}
```

Ý nghĩa: lấy `ORD_ID` hiện có trên form cha rồi bind vào query detail grid.

## 5. Có cần viết cả `params[]` lẫn `bindVariables[]` không?

Không phải lúc nào cũng cần.

- Record form bình thường: thường chỉ cần `params[]` để lấy `id` từ URL.
- Embedded grid/detail grid: thường cần `bindVariables[]` để lấy khóa cha từ form.
- Filter form / dashboard / page không có `id`: thường dùng `params[]` hoặc `bindVariables[]` tùy nguồn dữ liệu.

## 6. Nếu không khai báo `params[]` thì có load được không?

Có thể có, nhưng không nên trông chờ vào may mắn.

Runtime hiện có fallback:

- tự inject bind `id`
- nếu trong SQL có `:PARAM_NAME` và URL cũng có `?PARAM_NAME=...`, runtime có thể tự nhặt lên

Nhưng cách an toàn cho người mới là luôn khai báo rõ `params[]`.

Ví dụ an toàn hơn fallback:

```json
{
  "dataSource": {
    "type": "query",
    "loadQuery": "SELECT * FROM APPS.DEMO_ORDERS WHERE ORD_ID = :id AND COMPANY_ID = :companyId",
    "params": [
      { "name": "id", "sourceType": "url", "sourceField": "id" },
      { "name": "companyId", "sourceType": "url", "sourceField": "companyId" }
    ]
  }
}
```

## 7. Query load trả dữ liệu về map vào field thế nào?

Runtime lấy row đầu tiên trả về rồi map theo tên cột.

Ví dụ field trong form:

```json
[
  { "name": "ORD_ID", "type": "number" },
  { "name": "ORD_CODE", "type": "text" },
  { "name": "STATUS", "type": "text" }
]
```

Thì SQL nên alias khớp:

```sql
SELECT
  ORD_ID,
  ORD_CODE,
  STATUS
FROM APPS.DEMO_ORDERS
WHERE ORD_ID = :id
```

Nếu alias khác tên field, người mới rất dễ tưởng là query không load được dù thực ra query vẫn chạy.

## 8. Dấu hiệu để biết `loadQuery` có khả năng chạy được thật

Checklist thực dụng:

- Có `dataSource.loadQuery`
- Có `dataSource.keyField`
- Mọi bind trong SQL đều có nguồn giá trị thật
- SQL alias khớp `fields[].name`
- `loadQuery` trả đúng 1 row cho trường hợp edit
- Không hardcode endpoint nội bộ nếu chỉ dùng internal query runtime

Ví dụ có thể load được:

```json
{
  "dataSource": {
    "type": "query",
    "keyField": "EMP_ID",
    "loadQuery": "SELECT EMP_ID, EMP_CODE, FULL_NAME, DEPT_ID FROM APPS.EMPLOYEES WHERE EMP_ID = :id",
    "params": [
      { "name": "id", "sourceType": "url", "sourceField": "id" }
    ]
  }
}
```

Ví dụ dễ lỗi:

```json
{
  "dataSource": {
    "type": "query",
    "loadQuery": "SELECT EMP_ID, EMP_CODE FROM APPS.EMPLOYEES WHERE EMP_ID = :empId"
  }
}
```

Lý do dễ lỗi:

- thiếu `keyField`
- không map `:empId`
- field form có thể tên khác alias SQL

## 9. Save có những mode nào?

Theo runtime/schema hiện tại, phần hay gặp nhất là:

- `saveMode: "auto"` với `tableName`
- `saveQuery` / `saveQueryId` để chạy PL/SQL custom
- `saveMode: "procedure"` với `procedureName`

File này đào sâu vào `saveQuery` vì đây là chỗ người mới hay rối nhất.

## 10. `saveQuery` truyền bind như thế nào?

Runtime hiện làm như sau:

1. Lấy danh sách bind từ:
   `saveBindNames`, `saveOutBindNames`, hoặc regex quét trực tiếp từ `saveQuery`.

2. Với mỗi bind:
   - nếu tên là `id` -> lấy id hiện tại của record
   - nếu tên kết thúc `_out` -> set `null` để chờ OUT param
   - còn lại -> runtime cố map từ form values theo tên bind

3. Gọi internal command `/api/v2/sql/command` với `commandMode: 'plsql'`.

## 11. Runtime auto-map bind từ field như thế nào?

Với bind save, runtime đang map khá thực dụng:

- `:p_ord_code` -> tìm field `ORD_CODE`
- `:p_order_date` -> tìm field `ORDER_DATE`
- `:status` -> tìm field `STATUS`
- so sánh không phân biệt hoa thường, có thử bỏ `_`

Nghĩa là nếu field tên `ORDER_DATE`, bind tên `p_order_date` thường map được.

## 12. Ví dụ saveQuery create/update dễ hiểu

```json
{
  "dataSource": {
    "type": "query",
    "keyField": "ORD_ID",
    "loadQuery": "SELECT ORD_ID, ORD_CODE, ORDER_DATE, TOTAL_AMOUNT, STATUS FROM APPS.DEMO_ORDERS WHERE ORD_ID = :id",
    "params": [
      { "name": "id", "sourceType": "url", "sourceField": "id" }
    ],
    "saveQuery": "DECLARE\n  v_ord_id NUMBER := :p_ord_id;\nBEGIN\n  IF v_ord_id IS NULL THEN\n    SELECT APPS.DEMO_ORDERS_SEQ.NEXTVAL INTO v_ord_id FROM DUAL;\n    INSERT INTO APPS.DEMO_ORDERS (ORD_ID, ORD_CODE, ORDER_DATE, TOTAL_AMOUNT, STATUS)\n    VALUES (v_ord_id, :p_ord_code, TO_DATE(SUBSTR(:p_order_date, 1, 19), 'YYYY-MM-DD\"T\"HH24' || CHR(58) || 'MI' || CHR(58) || 'SS'), :p_total_amount, :p_status);\n  ELSE\n    UPDATE APPS.DEMO_ORDERS\n       SET ORD_CODE = :p_ord_code,\n           ORDER_DATE = TO_DATE(SUBSTR(:p_order_date, 1, 19), 'YYYY-MM-DD\"T\"HH24' || CHR(58) || 'MI' || CHR(58) || 'SS'),\n           TOTAL_AMOUNT = :p_total_amount,\n           STATUS = :p_status\n     WHERE ORD_ID = v_ord_id;\n  END IF;\n  :p_ord_id_out := v_ord_id;\nEND;",
    "outParams": ["p_ord_id_out"]
  }
}
```

Ở ví dụ này:

- `:p_ord_id` lấy từ field `ORD_ID`
- `:p_ord_code` lấy từ `ORD_CODE`
- `:p_order_date` lấy từ `ORDER_DATE`
- `:p_total_amount` lấy từ `TOTAL_AMOUNT`
- `:p_status` lấy từ `STATUS`
- `:p_ord_id_out` là OUT param trả về id mới sau insert

## 13. Sau save, OUT param được dùng thế nào?

Runtime sẽ cố tìm OUT key theo pattern:

- nếu `keyField = "ORD_ID"` -> tìm `p_ord_id_out`

Nếu có giá trị trả về:

- set lại field `ORD_ID` trên form
- update URL `?id=...` khi đang create normal page
- tiếp tục save detail grids theo id mới

Nói ngắn gọn: nếu create thành công và OUT param trả về đúng, form sẽ chuyển từ trạng thái “new” sang “edit record vừa tạo”.

## 14. Khi nào nên khai báo `outParams` rõ ràng?

Nên khai báo khi:

- PL/SQL có OUT bind
- procedure trả nhiều biến OUT
- muốn runtime/backend bind type ổn định hơn

Ví dụ:

```json
{
  "dataSource": {
    "saveQuery": "BEGIN APPS.PKG_ORDER.SAVE_ORDER(:p_ord_id, :p_ord_code, :p_status, :p_ord_id_out, :p_message_out); END;",
    "outParams": [
      { "name": "p_ord_id_out", "type": "number" },
      { "name": "p_message_out", "type": "varchar2" }
    ]
  }
}
```

## 15. `saveBindNames` và `saveOutBindNames` có dùng được không?

Frontend runtime hiện có đọc `saveBindNames` và `saveOutBindNames` khi build bind cho `saveQuery`.

Nhưng backend `DataSourceSchema` hiện chưa khai báo 2 key này trong schema strict. Vì vậy:

- runtime có hỗ trợ
- nhưng docs metadata chính không khuyên dùng như config chuẩn nếu bạn cần strict validation sạch lỗi

Muốn an toàn nhất thì để runtime tự regex bind từ `saveQuery`, và khai báo `outParams` cho OUT bind.

## 16. Truyền được những kiểu biến gì vào save?

Thực tế hiện tại:

- text / textarea / select: truyền được
- number / currency: runtime normalize trước khi gửi
- date / datetime / time: runtime cố normalize về chuỗi phù hợp trước khi bind
- hidden field: truyền được nếu có value trong form
- LOV field: value lưu trong field vẫn bind được như field thường

Điều quyết định không phải loại field fancy hay không, mà là field đó có mặt trong `formValues` lúc save không.

## 17. Những thứ người mới hay hiểu nhầm

### 17.1. Có `loadQuery` là chắc chắn load được

Không đúng. Có `loadQuery` mới chỉ là điều kiện cần. Còn phải có bind đúng và alias khớp field.

### 17.2. Có `saveQuery` là tự insert/update được

Không đúng. `saveQuery` chỉ là đoạn PL/SQL chạy được. Việc insert/update đúng còn phụ thuộc:

- bind có map đúng field không
- date/number có đúng format không
- có trả OUT id đúng không

### 17.3. Muốn bind gì cũng viết `fieldMapping`

Không nên trong metadata chính, vì backend schema strict hiện chưa khai báo `dataSource.fieldMapping`.

## 18. Mẫu thực tế dễ copy cho người mới

```json
{
  "metadataVersion": 2,
  "pageCode": "CUSTOMER_FORM",
  "pageType": "form",
  "title": "Khách hàng",
  "dataSource": {
    "type": "query",
    "keyField": "CUSTOMER_ID",
    "loadQuery": "SELECT CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, STATUS FROM APPS.CUSTOMERS WHERE CUSTOMER_ID = :id",
    "params": [
      { "name": "id", "sourceType": "url", "sourceField": "id" }
    ],
    "saveQuery": "DECLARE\n  v_customer_id NUMBER := :p_customer_id;\nBEGIN\n  IF v_customer_id IS NULL THEN\n    SELECT APPS.CUSTOMERS_SEQ.NEXTVAL INTO v_customer_id FROM DUAL;\n    INSERT INTO APPS.CUSTOMERS (CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, STATUS)\n    VALUES (v_customer_id, :p_customer_code, :p_customer_name, :p_status);\n  ELSE\n    UPDATE APPS.CUSTOMERS\n       SET CUSTOMER_CODE = :p_customer_code,\n           CUSTOMER_NAME = :p_customer_name,\n           STATUS = :p_status\n     WHERE CUSTOMER_ID = v_customer_id;\n  END IF;\n  :p_customer_id_out := v_customer_id;\nEND;",
    "outParams": ["p_customer_id_out"]
  },
  "layout": { "type": "default" },
  "regions": [
    {
      "id": "main",
      "type": "form",
      "fields": [
        { "name": "CUSTOMER_ID", "type": "number", "label": "ID", "readOnly": true },
        { "name": "CUSTOMER_CODE", "type": "text", "label": "Mã KH", "required": true },
        { "name": "CUSTOMER_NAME", "type": "text", "label": "Tên KH", "required": true },
        { "name": "STATUS", "type": "select", "label": "Trạng thái", "lov": { "code": "LOV_STATUS" } }
      ]
    }
  ]
}
```

## 19. Checklist trước khi nói “query này load được”

- `dataSource.type = "query"`
- có `keyField`
- có `loadQuery`
- mọi bind trong `loadQuery` có nguồn giá trị rõ ràng
- SQL alias khớp field name
- nếu edit page bằng URL thì có `params[]` map `id`
- nếu create/update bằng PL/SQL thì OUT id trả về khớp `p_<keyField>_out`

## 20. Checklist trước khi nói “save này chạy được”

- `saveQuery` có đủ bind input
- tên bind gần với tên field để runtime auto-map được
- OUT bind có trong `outParams`
- key field trên form tồn tại thật
- số/ngày được normalize đúng trước khi save
- procedure/PLSQL thực sự chạy được trong DB schema hiện tại

## 21. Lỗi thường gặp

- Query không load: thiếu bind `:id`, hoặc alias SQL không khớp field.
- Form mở create mode nhưng tưởng edit mode: URL không có `?id=...`.
- Save không ra ID mới: quên `:p_<key>_out` hoặc OUT param tên khác pattern runtime đang tìm.
- Save ra null: bind tên quá xa tên field, runtime auto-map không khớp.
- ORA-06502: sai type OUT param, date thiếu time, bind duplicate.
- Sequence not found: sai sequence/schema hoặc thiếu grant.
