<template>
  <span class="resource-avatar" :style="{ '--resource-color': color }" aria-hidden="true">
    <component :is="icon" :size="15" />
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { getExtensionIconColor } from '@/shared/lib/extensionIconColor'
import { getKbTypeIcon } from '@/modules/knowledge'

const props = defineProps({ item: { type: Object, required: true } })
const color = computed(() => getExtensionIconColor(props.item.resourceId || props.item.value))
const icon = computed(() => getKbTypeIcon(props.item.kbType || 'milvus'))
</script>

<style lang="less" scoped>
.resource-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 24px;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  color: var(--resource-color);
  background: color-mix(in srgb, var(--resource-color) 7%, var(--gray-0));
}
</style>
