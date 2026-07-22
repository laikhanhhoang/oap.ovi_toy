# Project Rules & Guidance for OAP / OVI Development

## Learned Reference Patterns (`docs/reference/AN_CAP_CHAN`)

- **Page Architecture**: Follow the standard OAP 3-file pattern (`metadata.json`, `events.json`, `translations.json`).
- **Skill Usage**: Refer to the `oap-page-patterns` skill in `.agents/skills/oap-page-patterns/SKILL.md` for exact JSON structure templates and event handlers.
- **Checkbox Datagrid Actions**: Use `selection: "multiple"` in `tableConfig` and pass `{{<grid_name>_SELECTED}}` in action bindings for batch processing/ActionBar commands.
- **Filter-Grid Linkage**: Ensure `filterRegionId` is set on datagrids and filter `onChange` events call `refreshRegion`.
- **Layout Splitters**: Utilize `splitter` layouts with collapsible/resizable panes for Sidebar Grids, Master-Detail Forms, and Filterable Lists.
