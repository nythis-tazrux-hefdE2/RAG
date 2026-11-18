<template>
  <component
    :is="currentRenderer"
    v-if="currentRenderer"
    :tool-call="toolCall"

    :appearance="appearance"
    :default-expanded="defaultExpanded"
    ref="toolRendererRef"
  />
  <BaseToolCall
    v-else-if="!isHidden"
    :tool-call="toolCall"
    :appearance="appearance"
    :default-expanded="defaultExpanded"
  />
</template>

<script setup>
import { computed, defineAsyncComponent, ref } from 'vue'
import BaseToolCall from './BaseToolCall.vue'
import ToolRendererUnavailable from './ToolRendererUnavailable.vue'

import { getToolCallId, isHiddenToolCall } from './toolRegistry'

const createRenderer = (loader) => defineAsyncComponent({
  loader,
  loadingComponent: BaseToolCall,
  errorComponent: ToolRendererUnavailable,
  delay: 0,
  timeout: 10000,
  suspensible: false
})




const ListKbsTool = createRenderer(() => import('./renderers/ListKbsTool.vue'))
const QueryKbTool = createRenderer(() => import('./renderers/QueryKbTool.vue'))
const FindKbDocumentTool = createRenderer(() => import('./renderers/FindKbDocumentTool.vue'))
const OpenKbDocumentTool = createRenderer(() => import('./renderers/OpenKbDocumentTool.vue'))
const CalculatorTool = createRenderer(() => import('./renderers/CalculatorTool.vue'))

const WriteFileTool = createRenderer(() => import('./renderers/WriteFileTool.vue'))
const ReadFileTool = createRenderer(() => import('./renderers/ReadFileTool.vue'))
const ListDirectoryTool = createRenderer(() => import('./renderers/ListDirectoryTool.vue'))
const SearchFileContentTool = createRenderer(() => import('./renderers/SearchFileContentTool.vue'))
const SearchFileTool = createRenderer(() => import('./renderers/SearchFileTool.vue'))
const GrepTool = createRenderer(() => import('./renderers/GrepTool.vue'))
const GlobTool = createRenderer(() => import('./renderers/GlobTool.vue'))
const EditFileTool = createRenderer(() => import('./renderers/EditFileTool.vue'))



const AskUserQuestionTool = createRenderer(() => import('./renderers/AskUserQuestionTool.vue'))
const ExecuteTool = createRenderer(() => import('./renderers/ExecuteTool.vue'))
const OcrParseFileTool = createRenderer(() => import('./renderers/OcrParseFileTool.vue'))


const props = defineProps({

  toolCall: {
    type: Object,
    required: true
  },
  appearance: {
    type: String,
    default: 'card'
  },
  defaultExpanded: {
    type: Boolean,
    default: false
  }
})

const toolId = computed(() => getToolCallId(props.toolCall))

const TOOL_RENDERERS = {
  ask_user_question: AskUserQuestionTool,
  bash: ExecuteTool,
  calculator: CalculatorTool,
  cmd: ExecuteTool,
  edit_file: EditFileTool,
  execute: ExecuteTool,
  find_kb_document: FindKbDocumentTool,
  glob: GlobTool,
  grep: GrepTool,
  list_directory: ListDirectoryTool,
  list_kbs: ListKbsTool,
  ls: ListDirectoryTool,



  ocr_parse_file: OcrParseFileTool,
  open_kb_document: OpenKbDocumentTool,
  query_kb: QueryKbTool,
  read_file: ReadFileTool,

  replace: EditFileTool,
  run_shell_command: ExecuteTool,
  search_file: SearchFileTool,
  search_file_content: SearchFileContentTool,





  write_file: WriteFileTool
}

const currentRenderer = computed(() =>
  TOOL_RENDERERS[toolId.value] || null
)
const isHidden = computed(() => isHiddenToolCall(props.toolCall))

const toolRendererRef = ref(null)
const refreshGraph = () => {
  if (toolRendererRef.value && typeof toolRendererRef.value.refreshGraph === 'function') {
    toolRendererRef.value.refreshGraph()
  }
}

defineExpose({ refreshGraph })
</script>

<style lang="less" scoped></style>
