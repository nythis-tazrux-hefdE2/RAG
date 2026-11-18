<template>
  <a-popover v-model:open="open" trigger="click" placement="topLeft" @open-change="load">
    <template #content>
      <div class="knowledge-selection">
        <p>保存后对新提问生效，当前任务使用提交时的选择。</p>
        <a-spin v-if="loading" />
        <template v-else>
          <a-checkbox :checked="draft === 'all'" :disabled="saving" @change="toggleAll">
            全部可访问知识库
          </a-checkbox>
          <a-checkbox-group
            :value="draft === 'all' ? [] : draft"
            :options="options"
            :disabled="draft === 'all' || saving"
            @change="draft = $event"
          />
          <span v-if="!options.length" class="empty">没有可访问的知识库</span>
          <p v-if="error" class="error" role="alert">{{ error }}</p>
          <a-button type="primary" size="small" :loading="saving" :disabled="!ready" @click="save">保存</a-button>
        </template>
      </div>
    </template>
    <a-button type="text" size="small" :disabled="disabled || loading" aria-label="选择知识库范围">
      <LibraryBig :size="14" />
      {{ selection === 'all' ? '全部知识库' : `知识库 ${selection.length}` }}
    </a-button>
  </a-popover>
</template>

<script setup>
import { onScopeDispose, ref, watch } from 'vue'
import { LibraryBig } from '@lucide/vue'
import { agentApi, knowledgeBaseApi } from '@/apis'

const props = defineProps({
  threadId: { type: String, default: '' },
  disabled: Boolean
})
const emit = defineEmits(['change', 'busy'])
const open = ref(false)
const loading = ref(false)
const saving = ref(false)
const ready = ref(false)
const selection = ref('all')
const draft = ref('all')
const options = ref([])
const error = ref('')
let generation = 0

/** 切换会话后只接受本会话的异步结果。 */
watch(() => props.threadId, async (threadId) => {
  const current = ++generation
  selection.value = 'all'
  ready.value = !threadId
  loading.value = !!threadId
  error.value = ''
  open.value = false
  if (!threadId) {
    emit('change', 'all')
    return
  }
  try {
    const response = await agentApi.getSessionKnowledgeSelection(threadId)
    if (current !== generation) return
    selection.value = response.selection
    ready.value = true
    emit('change', response.selection)
  } catch (failure) {
    if (current === generation) error.value = failure.message || '知识库范围读取失败'
  } finally {
    if (current === generation) loading.value = false
  }
}, { immediate: true })

/** 打开选择器时重新读取当前可见目录。 */
async function load(visible) {
  if (!visible) return
  const current = generation
  loading.value = true
  ready.value = false
  error.value = ''
  try {
    const [response, currentSelection] = await Promise.all([
      knowledgeBaseApi.getAccessibleKnowledgeBases(),
      props.threadId
        ? agentApi.getSessionKnowledgeSelection(props.threadId)
        : Promise.resolve({ selection: selection.value })
    ])
    if (current !== generation) return
    selection.value = currentSelection.selection
    emit('change', currentSelection.selection)
    options.value = response.knowledge_bases.map((kb) => ({ value: kb.kb_id, label: kb.name }))
    const visibleIds = new Set(options.value.map((option) => option.value))
    draft.value = selection.value === 'all' ? 'all' : selection.value.filter((id) => visibleIds.has(id))
    ready.value = true
  } catch (failure) {
    if (current === generation) error.value = failure.message || '知识库目录读取失败'
  } finally {
    if (current === generation) loading.value = false
  }
}

/** 全部模式和显式选择使用不同的持久语义。 */
function toggleAll(event) {
  draft.value = event.target.checked ? 'all' : []
}

/** 新会话暂存选择；已有会话先等待服务端提交。 */
async function save() {
  if (!ready.value) return
  const current = generation
  const next = draft.value === 'all' ? 'all' : [...draft.value]
  saving.value = true
  emit('busy', true)
  error.value = ''
  try {
    if (props.threadId) await agentApi.setSessionKnowledgeSelection(props.threadId, next)
    if (current !== generation) return
    selection.value = next
    emit('change', next)
    open.value = false
  } catch (failure) {
    if (current === generation) error.value = failure.message || '知识库范围保存失败'
  } finally {
    saving.value = false
    emit('busy', false)
  }
}

onScopeDispose(() => { generation += 1 })
defineExpose({ getSelection: () => selection.value === 'all' ? 'all' : [...selection.value] })
</script>

<style scoped>
.knowledge-selection { display: flex; flex-direction: column; gap: 12px; width: 280px; max-width: 70vw; }
.knowledge-selection p, .empty { margin: 0; color: var(--color-text-secondary); font-size: 12px; }
.knowledge-selection :deep(.ant-checkbox-group) { display: flex; flex-direction: column; gap: 8px; max-height: 240px; overflow: auto; }
.knowledge-selection .error { color: var(--color-error-500); }
</style>
