import { formatMentionToken } from './mention_token.js'

const toResourceItem = (type, { value, label, extra = {} } = {}) => {
  if (!value && !label) return null
  const resolvedValue = value || label
  return {
    value: resolvedValue,
    label: label || resolvedValue,
    type,
    tokenLabel: formatMentionToken(type, label || resolvedValue),
    ...extra
  }
}

export const buildMentionResourceItems = (mention = {}) => {
  const { knowledgeBases = [] } = mention
  return {
    knowledgeBases: knowledgeBases.map((kb) => toResourceItem('knowledge', {
      value: kb.name, label: kb.name,
      extra: { description: kb.description || '', resourceId: kb.kb_id, kbType: kb.kb_type }
    })).filter(Boolean)
  }
}
