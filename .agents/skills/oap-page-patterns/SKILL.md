---
name: oap-page-patterns
description: Reference patterns and configuration best practices for OAP/OVI UI pages (AN_CAP_CHAN reference standards), including standard forms, checkbox datagrids, actionbar integrations, grid input forms, master-detail layouts, and sidebar splitters.
---

# OAP UI Page Design Patterns & Reference Architecture (AN_CAP_CHAN)

This skill documents the 9 standard UI page patterns and metadata conventions used in OAP (OVI Application Platform), based on `@docs/reference/AN_CAP_CHAN`.

---

## 1. Metadata & Page Structure Overview

Every OAP page consists of three primary JSON configurations:
- `metadata.json`: Defines layout, splitters, tab groups, regions, components (fields, datagrids, toolbars, buttons), data sources, and modal popup configs.
- `events.json`: Defines interactive triggers (`onLoad`, `onChange`, `onCustomAction`), conditions, and action lists (`refreshRegion`, `apiCall`, `setValue`, `command`, `showMessage`).
- `translations.json`: Defines localized labels and messages.

---

## 2. Key OAP Page Patterns

### Pattern A: Standard Form & List (`form list thuong` / `listhuong`)
- **Layout**: `splitter` with header action toolbar and tab groups (`tab_main`, `tab_details`, `tab_accounting`, `tab_history`).
- **Toolbar Action Popup**:
  ```json
  {
    "type": "button",
    "label": "Cấn trừ công nợ",
    "action": "page-popup",
    "variant": "secondary",
    "modalConfig": {
      "pageCode": "FCM_CASH_R_OFFSET_NETTING_FORM",
      "workspace": "OVI_SUITE",
      "size": "full",
      "params": { "CTR_ID": "CTR_ID", "OBJ_ID": "OBJ_ID" },
      "refreshOnClose": true
    },
    "visibility": {
      "rules": [{ "field": "RECEIPT_STATUS", "operator": "in", "value": ["C", "P"] }]
    }
  }
  ```

---

### Pattern B: Checkbox Datagrid Pass to ActionBar (`check box grid truyen len acctionbar`)
- **Use Case**: Multi-selecting grid rows and sending selected keys to an actionbar command (e.g., bulk assignment, batch status updates).
- **Datagrid Metadata**: Set `"selection": "multiple"` in `tableConfig`.
  ```json
  "tableConfig": {
    "keyField": "RRE_ID",
    "selection": "multiple",
    "pageSize": 25,
    "search": true
  }
  ```
- **Event Binding**: Target selected items using `{{<grid_field_name>_SELECTED}}`:
  ```json
  {
    "name": "assign_task",
    "trigger": "onCustomAction",
    "sourceComponent": "assign_task",
    "actions": [
      { "type": "confirm", "message": "Bạn có chắc chắn muốn giao việc?" },
      {
        "type": "command",
        "commandMode": "plsql",
        "body": {
          "bindVariables": [
            { "name": "p_emp_id", "sourceField": "lov_assigned_emp" },
            { "name": "p_ids", "value": "{{main_grid_SELECTED}}" },
            { "name": "p_username", "value": "{{G_USER_ID}}" }
          ]
        },
        "onResult": [
          { "type": "showMessage", "messageType": "success", "message": "{{result.data.p_result_out}}" },
          { "type": "refreshRegion", "target": "grid_reg" }
        ]
      }
    ]
  }
  ```

---

### Pattern C: Multi-Action Checkbox Grid (`check box grid truyen len acctionbar nhieu chuc nang`)
- **Use Case**: Datagrids with multiple toolbar operations (e.g. Generate posting, Batch export).
- **Conditional Action Execution**:
  ```json
  {
    "type": "apiCall",
    "endpoint": "/api/v1/sql/execute-query",
    "method": "POST",
    "body": {
      "params": {
        "ids": "{{main_grid_SELECTED}}",
        "fallback_id": "{{RRE_ID}}"
      }
    },
    "onResult": [
      {
        "condition": "!result || !result.data || !result.data.items || result.data.items.length === 0",
        "type": "showMessage",
        "messageType": "warning",
        "message": "Không tìm thấy dữ liệu."
      },
      {
        "condition": "result && result.data && result.data.items && result.data.items.length > 0",
        "type": "setValue",
        "target": "txt_downloader",
        "value": "{{result.data.items[0].POSTING_TEXT}}"
      }
    ]
  }
  ```

---

### Pattern D: Grid Input in Form (`cacchuc nag co ban cua grid input trong form`)
- **Layout**: Vertical Splitter (Top 60% Form Tabs, Bottom 40% Grid Input Detail Tabs).
- **Calculated Actions**: SQL button calculation triggers (e.g., `btn_calculate_tax` recalculating totals and tax lines).
- **Auto-Fill Triggers**:
  - `onLoad`: Execute queries to auto-populate default periods (`APE_ID`, `FISCAL_YEAR`) and customer default info (`BUYER_CODE`, `BUYER_EMAIL`).
  - `onChange`: Trigger currency exchange rate lookup (`EXCHANGE_RATE`) on `CUR_CODE` change.

---

### Pattern E: Master-Detail & Sidebar Layouts (`form grid chua detail`, `grid chua detail`, `siderbar grid`)
- **Sidebar Splitter**: Left pane (20%–35% width, collapsible filter or hierarchy tree) + Right center pane (Header, widgets, tabs, grids).
- **Badge Styling**: Use `badgeMapping` on datagrid status columns:
  ```json
  "badgeMapping": {
    "ASSIGNED": { "cssClass": "lov-status-success", "label": "Đã giao" },
    "UNASSIGNED": { "cssClass": "lov-status-warning", "label": "Chưa giao" }
  }
  ```
- **Filter Region Linkage**: Reference `filterRegionId` inside `datagrid` metadata to automatically react to changes in filter fields.

---

## 3. Core Principles & Conventions

1. **Selection Reference**: Always use `{{<grid_id>_SELECTED}}` to pass selected rows to actions.
2. **Filter Integration**: Link datagrids to filter regions via `filterRegionId` and define `onChange` triggers with `refreshRegion`.
3. **Modal Navigation**: Configure column links with `modalConfig` (`pageCode`, `size`, `paramMapping`).
4. **Conditional Formatting**: Use `coloredBadge: true` and `badgeMapping` for LOV status columns.
