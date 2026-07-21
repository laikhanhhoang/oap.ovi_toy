# Grid, Table, Treelist Metadata

Grid/table dùng `columns`. Form field dùng `name`, còn grid column dùng `key`.

Tên như `ORDER_LIST`, `ORDER_ITEMS`, `ORD_ID`, `APPS.DEMO_ORDERS` chỉ là ví dụ. Thay bằng page, field, column, bảng/view thật.

## 1. Root datagrid tối thiểu

Root `pageType: "datagrid"` hiện nên giữ schema-safe: `dataSource`, `columns`, `selection`, `pageEvents`.

```json
{
  "metadataVersion": 2,
  "pageCode": "ORDER_LIST",
  "pageType": "datagrid",
  "title": "Danh sách đơn hàng",
  "dataSource": {
    "type": "query",
    "keyField": "ORD_ID",
    "query": "SELECT ORD_ID, ORD_CODE, ORDER_DATE, TOTAL_AMOUNT, STATUS FROM APPS.DEMO_ORDERS"
  },
  "selection": "multiple",
  "columns": [
    { "key": "ORD_CODE", "label": "Mã đơn", "type": "text", "width": 160, "required": true },
    { "key": "ORDER_DATE", "label": "Ngày đơn", "type": "date", "format": "dd/MM/yyyy" },
    { "key": "TOTAL_AMOUNT", "label": "Tổng tiền", "type": "number", "format": "#,##0", "alignment": "right" },
    { "key": "STATUS", "label": "Trạng thái", "type": "select", "lovCode": "ORDER_STATUS" }
  ]
}
```

Không đặt `tableConfig`, `toolbar`, `masterDetail`, `parentIdExpr`, `autoExpandAll` ở root nếu muốn đi qua backend `PageMetadataSchema` hiện tại. Những phần nâng cao bên dưới dùng embedded grid field.

Các ví dụ root datagrid trong file này dùng schema canonical (`dataSource.type: "query"`). Các ví dụ toolbar/buttons/tableConfig là cho embedded grid `fields[].metadata`; backend cho `metadata` passthrough và runtime `FieldRenderer`/`DxDataGrid` đang đọc các key đó.

## 2. Embedded datagrid trong form

Dùng khi cần nhiều config: toolbar, tableConfig, editing, filter/search/export, buttons column.

```json
{
  "id": "lines_region",
  "title": "Dòng đơn hàng",
  "type": "form",
  "fields": [
    {
      "name": "ORDER_ITEMS",
      "type": "datagrid",
      "label": "Dòng hàng",
      "metadata": {
        "dataSource": {
          "type": "query",
          "keyField": "LINE_ID",
          "query": "SELECT LINE_ID, ORD_ID, ITEM_ID, ITEM_NAME, QUANTITY, UNIT_PRICE, STATUS FROM APPS.ORDER_LINES WHERE ORD_ID = :ORD_ID",
          "bindVariables": [
            { "name": "ORD_ID", "sourceField": "ORD_ID" }
          ],
          "foreignKey": "ORD_ID",
          "defaultValues": {
            "ORD_ID": ":ORD_ID",
            "STATUS": "DRAFT"
          }
        },
        "tableConfig": {
          "height": "420px",
          "rowHeight": 34,
          "pageSize": 25,
          "selection": "multiple",
          "editing": {
            "mode": "batch",
            "allowAdding": true,
            "allowUpdating": true,
            "allowDeleting": true
          }
        },
        "filterRow": true,
        "searchPanel": true,
        "headerFilter": true,
        "columnChooser": true,
        "exportEnabled": true,
        "columns": [
          { "key": "ITEM_NAME", "label": "Mặt hàng", "type": "text", "width": 220 },
          { "key": "QUANTITY", "label": "SL", "type": "number", "width": 90 },
          { "key": "UNIT_PRICE", "label": "Đơn giá", "type": "number", "format": "#,##0", "alignment": "right" },
          { "key": "STATUS", "label": "Trạng thái", "type": "select", "lovCode": "ORDER_LINE_STATUS" }
        ]
      }
    }
  ]
}
```

## 3. Feature flags cho embedded grid

Các key này đặt trong `field.metadata`.

```json
{
  "filterRow": true,
  "searchPanel": true,
  "headerFilter": true,
  "columnChooser": true,
  "exportEnabled": true,
  "grouping": true,
  "height": "calc(100vh - 280px)",
  "tableConfig": {
    "height": "420px",
    "rowHeight": 32,
    "pageSize": 50,
    "compact": true,
    "search": true,
    "filterPanel": true,
    "columnFixing": true,
    "stateStoring": true,
    "defaultGrouping": ["STATUS"]
  }
}
```

## 4. Editing batch

Runtime/schema hiện khuyến nghị chỉ dùng `batch`.

```json
{
  "tableConfig": {
    "editing": {
      "mode": "batch",
      "allowAdding": true,
      "allowUpdating": true,
      "allowDeleting": true
    }
  }
}
```

Nếu dùng `inlineEdit`, validator báo deprecated. Nếu dùng mode `row`, `cell`, `popup` trong embedded datagrid, validator báo nên đổi sang `batch`.

## 5. Column cơ bản

```json
[
  { "key": "ORD_CODE", "label": "Mã đơn", "type": "text", "width": 160, "fixed": true, "fixedPosition": "left" },
  { "key": "ORDER_DATE", "label": "Ngày đơn", "type": "date", "format": "dd/MM/yyyy" },
  { "key": "TOTAL_AMOUNT", "label": "Tổng tiền", "type": "number", "format": "#,##0", "alignment": "right" },
  { "key": "STATUS", "label": "Trạng thái", "type": "select", "lovCode": "ORDER_STATUS" }
]
```

## 6. Column readonly/hidden/visible

```json
[
  { "key": "LINE_ID", "label": "ID", "type": "number", "visible": false },
  { "key": "CREATED_BY", "label": "Người tạo", "type": "text", "allowEditing": false },
  { "key": "INTERNAL_NOTE", "label": "Ghi chú nội bộ", "type": "textarea", "hidden": true }
]
```

`visible: false` và `hidden: true` đều dùng để ẩn cột tùy renderer. Với cột audit/computed nên dùng `allowEditing: false`.

## 7. Conditional column

```json
{
  "key": "REJECT_REASON",
  "label": "Lý do từ chối",
  "type": "textarea",
  "conditionalVisible": {
    "mode": "expression",
    "expression": "STATUS == 'REJECTED'",
    "default": false
  },
  "conditionalRequired": {
    "mode": "expression",
    "expression": "STATUS == 'REJECTED'"
  },
  "conditionalReadonly": {
    "mode": "expression",
    "expression": "STATUS == 'APPROVED'"
  }
}
```

## 8. Column computed chain

```json
[
  { "key": "QUANTITY", "label": "SL", "type": "number" },
  { "key": "UNIT_PRICE", "label": "Đơn giá", "type": "number", "format": "#,##0" },
  {
    "key": "LINE_AMOUNT",
    "label": "Thành tiền",
    "type": "number",
    "allowEditing": false,
    "computed": {
      "expression": "(QUANTITY || 0) * (UNIT_PRICE || 0)",
      "dependsOn": ["QUANTITY", "UNIT_PRICE"]
    }
  },
  {
    "key": "VAT_AMOUNT",
    "label": "VAT",
    "type": "number",
    "allowEditing": false,
    "computed": {
      "expression": "(LINE_AMOUNT || 0) * 0.1",
      "dependsOn": ["LINE_AMOUNT"]
    }
  }
]
```

## 9. Grid LOV/lookup

Root/embedded grid column dùng `lovCode` cho LOV đã đăng ký.

```json
{
  "key": "STATUS",
  "label": "Trạng thái",
  "type": "select",
  "lovCode": "ORDER_STATUS"
}
```

Inline lookup:

```json
{
  "key": "PRIORITY",
  "label": "Độ ưu tiên",
  "type": "select",
  "lookup": {
    "dataSource": [
      { "value": "LOW", "label": "Thấp" },
      { "value": "NORMAL", "label": "Thường" },
      { "value": "HIGH", "label": "Cao" }
    ],
    "valueExpr": "value",
    "displayExpr": "label"
  }
}
```

Chi tiết thêm xem [LOV.md](./LOV.md).

## 10. Fill cột khác sau khi chọn LOV

Runtime grid đọc `dependentFields` hoặc `lov.returnFields`.

```json
{
  "key": "ITEM_ID",
  "label": "Mặt hàng",
  "type": "select",
  "lovCode": "LOV_ITEMS",
  "dependentFields": {
    "ITEM_NAME": "ITEM_NAME",
    "UOM": "UOM",
    "UNIT_PRICE": "PRICE"
  }
}
```

Các target `ITEM_NAME`, `UOM`, `UNIT_PRICE` phải là cột có thật trong grid.

## 11. Row action buttons column

Dùng column `type: "buttons"` để có nút theo từng dòng trong embedded grid `field.metadata.columns`.

Không dùng `buttons` trong root `pageType: "datagrid"` `columns[]` nếu đang validate strict `metadataVersion: 2`, vì backend `ColumnSchema.strict()` hiện chưa khai báo key `buttons`.

```json
{
  "key": "ACTIONS",
  "label": "",
  "type": "buttons",
  "width": 120,
  "fixed": true,
  "fixedPosition": "right",
  "buttons": [
    {
      "name": "view",
      "icon": "eye",
      "hint": "Xem chi tiết",
      "type": "normal",
      "stylingMode": "text",
      "actionConfig": {
        "type": "modal",
        "pageCode": "ORDER_DETAIL",
        "title": "Chi tiết đơn hàng",
        "size": "lg",
        "rowKeyField": "ORD_ID",
        "paramMapping": {
          "id": "ORD_ID"
        }
      }
    }
  ]
}
```

## 12. Ẩn/hiện row button theo dòng

`visible` hoặc `visibleExpr` nhận boolean hoặc JS expression. Biến có sẵn: `data`, `row`, `pageItems`, `globalItems`.

```json
{
  "name": "approve",
  "icon": "check",
  "hint": "Duyệt",
  "type": "success",
  "stylingMode": "contained",
  "visible": "data.STATUS === 'SUBMITTED'",
  "actionConfig": {
    "type": "plsql",
    "query": "BEGIN APPS.ORDER_PKG.APPROVE_ORDER(:p_ord_id); END;",
    "bindVariables": [
      { "name": "p_ord_id", "source": "rowData", "sourceField": "ORD_ID" }
    ],
    "confirmMessage": "Duyệt đơn {{ORD_CODE}}?",
    "successMessage": "Đã duyệt đơn",
    "refreshAfter": true
  }
}
```

## 13. Disable row button theo dòng

`disabled` nhận boolean hoặc JS expression. Nếu expression true thì nút bị disable.

```json
{
  "name": "delete",
  "icon": "trash",
  "hint": "Xóa",
  "type": "danger",
  "stylingMode": "text",
  "disabled": "data.STATUS === 'APPROVED' || data.LOCKED_FLAG === 'Y'",
  "actionConfig": {
    "type": "plsql",
    "query": "BEGIN APPS.ORDER_PKG.DELETE_ORDER(:p_ord_id); END;",
    "bindVariables": [
      { "name": "p_ord_id", "source": "rowData", "sourceField": "ORD_ID" }
    ],
    "confirmMessage": "Xóa đơn {{ORD_CODE}}?",
    "successMessage": "Đã xóa",
    "refreshAfter": true
  }
}
```

## 14. Row button: navigate

```json
{
  "name": "open_page",
  "icon": "external-link",
  "hint": "Mở trang",
  "actionConfig": {
    "type": "navigate",
    "url": "/runtime/ORDER_FORM?id={{ORD_ID}}"
  }
}
```

## 15. Row button: API call

```json
{
  "name": "sync",
  "icon": "refresh-cw",
  "hint": "Đồng bộ",
  "visible": "data.STATUS === 'APPROVED'",
  "actionConfig": {
    "type": "api",
    "url": "/api/v1/orders/{{ORD_ID}}/sync",
    "method": "POST",
    "body": {
      "orderId": "{{ORD_ID}}",
      "source": "grid"
    },
    "successMessage": "Đã đồng bộ",
    "refreshAfter": true
  }
}
```

## 16. Row button: refresh

```json
{
  "name": "refresh_row",
  "icon": "rotate-cw",
  "hint": "Refresh grid",
  "actionConfig": {
    "type": "refresh"
  }
}
```

## 17. Toolbar cho embedded grid

Builder/runtime dùng `metadata.toolbar` cho embedded grid field. Các item thường có `type`, `label`, `icon`, `variant`, `stylingMode`, `actionConfig`.

```json
{
  "toolbar": [
    {
      "type": "create",
      "label": "Thêm dòng",
      "icon": "plus",
      "variant": "success",
      "stylingMode": "contained",
      "modalConfig": {
        "pageCode": "ORDER_LINE_FORM",
        "title": "Thêm dòng hàng",
        "size": "lg"
      }
    },
    {
      "type": "navigate",
      "label": "Mở danh mục hàng",
      "icon": "external-link",
      "stylingMode": "outlined",
      "actionConfig": {
        "type": "navigate",
        "url": "/runtime/ITEM_LIST"
      }
    }
  ]
}
```

## 18. Ẩn toolbar button bằng visibleCondition

Grid toolbar dùng `visibleCondition`, không dùng `visible` expression như row buttons. Runtime resolve `{{FIELD}}` từ form values rồi evaluate điều kiện.

```json
{
  "toolbar": [
    {
      "type": "button",
      "label": "Tạo hóa đơn",
      "icon": "file-plus",
      "action": "page-event",
      "visibleCondition": "{{STATUS}} == 'APPROVED' && {{INVOICE_ID}} == null"
    }
  ]
}
```

Nếu parse condition lỗi, runtime fail-open và vẫn show button.

## 19. Disable toolbar button khi chưa chọn dòng

Dùng `enableOnSelection: true`. Runtime sẽ disable một số toolbar action như create/page-popup khi chưa có selected rows. Với `bulkDelete`, runtime ẩn luôn khi chưa chọn dòng.

```json
{
  "tableConfig": {
    "selection": "multiple"
  },
  "toolbar": [
    {
      "type": "create",
      "label": "Tạo phiếu từ dòng chọn",
      "icon": "plus",
      "enableOnSelection": true,
      "modalConfig": {
        "pageCode": "ORDER_CREATE_FROM_LINES",
        "title": "Tạo phiếu",
        "size": "lg",
        "params": {
          "sourceOrderId": "{{ORD_ID}}"
        }
      }
    }
  ]
}
```

## 20. Toolbar addRow

Thêm dòng inline bằng DevExtreme `grid.addRow()`.

```json
{
  "toolbar": [
    {
      "type": "addRow",
      "label": "Thêm dòng",
      "icon": "plus",
      "variant": "success",
      "stylingMode": "contained",
      "location": "before"
    }
  ]
}
```

## 21. Toolbar SQL/PLSQL action

`actionConfig.type` hợp lệ theo validator: `modal`, `sql`, `command`, `plsql`, `procedure`, `api`, `refresh`, `navigate`, `page-popup`, `report`, `openReport`, `import-excel`, `create-tree`.

```json
{
  "toolbar": [
    {
      "type": "plsql",
      "label": "Khóa các dòng đã chọn",
      "icon": "lock",
      "variant": "danger",
      "actionConfig": {
        "type": "plsql",
        "query": "BEGIN APPS.ORDER_PKG.LOCK_SELECTED_LINES(:p_status); END;",
        "bindVariables": [
          { "name": "p_status", "value": "LOCKED" }
        ],
        "confirmMessage": "Khóa các dòng đã chọn?",
        "successMessage": "Đã khóa",
        "refreshAfter": true
      }
    }
  ]
}
```

Với `actionConfig.type: "plsql"`, validator yêu cầu có `query`.

## 22. Toolbar API action

```json
{
  "toolbar": [
    {
      "type": "button",
      "label": "Đồng bộ",
      "icon": "refresh-cw",
      "variant": "primary",
      "visibleCondition": "{{STATUS}} == 'APPROVED'",
      "actionConfig": {
        "type": "api",
        "url": "/api/v1/orders/sync",
        "method": "POST",
        "body": {
          "orderId": ":ORD_ID",
          "source": "grid-toolbar"
        },
        "confirmMessage": "Đồng bộ đơn hàng này?",
        "successMessage": "Đã đồng bộ",
        "refreshAfter": true
      }
    }
  ]
}
```

Trong toolbar API body, runtime resolve dạng `:FIELD_NAME` từ form/global values.

## 23. Toolbar bulk delete

Builder có pattern `bulkDelete` khi selection là `multiple`.

```json
{
  "tableConfig": {
    "selection": "multiple"
  },
  "toolbar": [
    {
      "type": "bulkDelete",
      "label": "Xóa mục đã chọn",
      "icon": "trash",
      "variant": "danger",
      "config": {
        "tableName": "APPS.ORDER_LINES",
        "keyField": "LINE_ID"
      }
    }
  ]
}
```

`bulkDelete` tự ẩn khi chưa chọn dòng. Có thể dùng `config.deleteQuery` nếu không muốn delete theo `tableName/keyField` mặc định.

## 24. Toolbar page-popup

```json
{
  "toolbar": [
    {
      "type": "page-popup",
      "label": "Chọn hàng",
      "icon": "search",
      "action": {
        "type": "page-popup",
        "page": {
          "page": "ITEM_PICKER",
          "title": "Chọn mặt hàng"
        }
      }
    }
  ]
}
```

## 25. Toolbar import Excel

Runtime dispatch event `import-excel-trigger` để mở modal import.

```json
{
  "toolbar": [
    {
      "type": "import-excel",
      "label": "Import Excel",
      "icon": "upload",
      "variant": "default",
      "stylingMode": "contained"
    }
  ]
}
```

## 26. Toolbar dropdown menu

```json
{
  "toolbar": [
    {
      "type": "dropdown",
      "label": "Thao tác",
      "icon": "more-horizontal",
      "items": [
        { "name": "refresh", "label": "Refresh", "icon": "refresh-cw", "action": "refresh" },
        { "name": "add", "label": "Thêm dòng", "icon": "plus", "action": "addRow" },
        { "name": "export", "label": "Export Excel", "icon": "download", "action": "export" },
        {
          "name": "open_picker",
          "label": "Chọn từ popup",
          "icon": "search",
          "action": "modal",
          "modalConfig": {
            "pageCode": "ITEM_PICKER",
            "title": "Chọn mặt hàng",
            "size": "lg"
          }
        }
      ]
    }
  ]
}
```

## 27. Form/page toolbar field visibility

Nếu nút nằm trong field `type: "dx-toolbar"` của form/page, không phải `metadata.toolbar` của grid, runtime dùng `visibility` rules.

```json
{
  "name": "PAGE_TOOLBAR",
  "type": "dx-toolbar",
  "items": [
    {
      "type": "submit",
      "label": "Lưu",
      "icon": "save",
      "visibility": {
        "mode": "expression",
        "expression": "STATUS != 'APPROVED'"
      }
    }
  ]
}
```

Đừng nhầm với row action buttons: row buttons dùng `visible`/`disabled`; grid toolbar dùng `visibleCondition`/`enableOnSelection`; form toolbar field dùng `visibility`.

## 28. Treelist schema-safe

Root treelist hiện chỉ nên dùng `dataSource` và `columns` ở docs chính.

```json
{
  "metadataVersion": 2,
  "pageCode": "ORG_TREE",
  "pageType": "treelist",
  "title": "Cây đơn vị",
  "dataSource": {
    "type": "query",
    "keyField": "ORG_ID",
    "query": "SELECT ORG_ID, PARENT_ORG_ID, ORG_NAME, STATUS FROM APPS.ORG_UNITS"
  },
  "columns": [
    { "key": "ORG_NAME", "label": "Đơn vị", "type": "text" },
    { "key": "STATUS", "label": "Trạng thái", "type": "select", "lovCode": "ORG_STATUS" }
  ]
}
```

Các key như `parentIdExpr`/`autoExpandAll` có type/runtime nhắc tới, nhưng root backend schema hiện chưa khai báo, nên không viết như ví dụ root copy-paste.

## 29. Master-detail

Root `masterDetail` chưa nằm trong `PageMetadataSchema`, nên không dùng ở root metadata chính. Với detail grid, dùng embedded `datagrid` field như mục 2, có `dataSource.foreignKey` và `defaultValues`.

## 30. Checklist grid

- Root datagrid: dùng `dataSource.keyField`, `columns[]`, `selection`.
- Embedded grid: đặt nâng cao trong `field.metadata`.
- Edit grid: dùng `metadata.tableConfig.editing.mode: "batch"`.
- SQL alias phải trùng `columns[].key`.
- LOV grid: dùng `lovCode`, không dùng `lov.code` cho root grid column.
- Row button ẩn/hiện: dùng `visible` hoặc `visibleExpr`.
- Row button disable: dùng `disabled`.
- Row button expression dùng `data.FIELD`, `pageItems.FIELD`, `globalItems.KEY`.
- Grid toolbar ẩn/hiện theo form value: dùng `visibleCondition`.
- Grid toolbar disable khi cần selection: dùng `enableOnSelection`.
- Grid toolbar bulk delete tự ẩn khi chưa chọn dòng.
- Action DB nên có `confirmMessage`, `successMessage`, `refreshAfter`.
- Cột computed/audit nên có `allowEditing: false`.
