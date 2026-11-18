/** 读取默认问答定义的字段展示描述。 */
export const normalizeAgentConfigurableItems = (items = {}) => Object.fromEntries(
  Object.entries(items).map(([key, item]) => {
    const { x_oap_ui_config: ui, ...schema } = item
    return [key, { ...schema, ...ui }]
  })
)


export const getAgentConfigOptions = (item) => (Array.isArray(item?.options) ? item.options : [])


export const getAgentConfigOptionValue = (option) => {
  if (typeof option !== 'object' || option === null) return option
  return option.key
}

export const getAgentConfigOptionLabel = (option) => {
  if (typeof option !== 'object' || option === null) return option
  return option.name || option.key
}

export const getAgentConfigOptionDescription = (option) =>
  typeof option === 'object' && option !== null ? option.description || '' : ''


/** 全部模式包含后续新增资源，省略字段沿用默认值。 */
export const isAllAgentResourceSelection = (current, item) =>
  current === 'all' || (current === undefined && item?.default === 'all')


/** 将配置意图投影为当前可见选择，空列表始终不选择。 */
export const getVisibleAgentResourceSelection = (current, item, available) => {
  if (current === undefined) current = item?.default
  if (isAllAgentResourceSelection(current, item)) return [...available]
  if (!Array.isArray(current)) return []
  const visible = new Set(available.map(String))
  return current.filter((value) => visible.has(String(value)))
}
