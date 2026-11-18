import { DatabaseZap } from '@lucide/vue'

/** 本地知识库唯一使用 Milvus。 */
export const getKbTypeLabel = (type) =>
  String(type || '').toLowerCase() === 'milvus' ? 'Milvus' : type

export const getKbTypeIcon = () => DatabaseZap
export const getKbTypeColor = () => 'blue'

/** 只开放当前应用支持的知识库详情。 */
export const supportsKnowledgeBaseDetail = (knowledgeBase) => knowledgeBase?.kb_type === 'milvus'

export const kbUtils = { getKbTypeLabel, getKbTypeIcon, getKbTypeColor, supportsKnowledgeBaseDetail }
