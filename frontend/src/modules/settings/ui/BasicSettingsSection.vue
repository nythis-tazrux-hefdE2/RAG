<template>
  <div class="basic-settings-section settings-page">
    <template v-if="userStore.isSuperAdmin">
      <section class="settings-section-block">
        <h3 class="settings-section-title">默认项配置</h3>
        <section class="settings-form-panel" aria-label="默认模型配置">
          <div class="settings-form-row">
            <div class="settings-form-copy">
              <div class="settings-form-label">
                {{ items?.default_model?.des || '默认对话模型' }}
              </div>
              <p class="settings-form-description">未单独指定模型时，用于对话与内容生成。</p>
            </div>
            <div class="settings-form-control">
              <ModelSelectorComponent
                display-name="mini"
                @select-model="handleChatModelSelect"
                :model_spec="configStore.config?.default_model"
                placeholder="请选择默认模型"
              />
            </div>
          </div>
          <div class="settings-form-row">
            <div class="settings-form-copy">
              <div class="settings-form-label">{{ items?.fast_model?.des || '快速响应模型' }}</div>
              <p class="settings-form-description">用于会话标题等需要快速响应的轻量任务。</p>
            </div>
            <div class="settings-form-control">
              <ModelSelectorComponent
                display-name="mini"
                @select-model="handleFastModelSelect"
                :model_spec="configStore.config?.fast_model"
                placeholder="请选择模型"
              />
            </div>
          </div>
          <div class="settings-form-row">
            <div class="settings-form-copy">
              <div class="settings-form-label">
                {{ items?.reference_model?.des || '来源标注模型' }}
              </div>
              <p class="settings-form-description">
                建议选择非思考模型，或在模型配置中关闭思考、降低思考强度。
              </p>
            </div>
            <div class="settings-form-control">
              <ModelSelectorComponent
                display-name="mini"
                :model_spec="configStore.config?.reference_model || ''"
                clearable
                placeholder="沿用快速响应模型"
                @select-model="handleChange('reference_model', $event || '')"
              />
            </div>
          </div>
          <div class="settings-form-row">
            <div class="settings-form-copy">
              <div class="settings-form-label">
                {{ items?.embed_model?.des || '默认 Embedding 模型' }}
              </div>
              <p class="settings-form-description">将文本转为向量，用于知识库索引与检索。</p>
            </div>
            <div class="settings-form-control is-compact">
              <EmbeddingModelSelector
                display-name="mini"
                :value="configStore.config?.embed_model"
                @change="handleChange('embed_model', $event)"
              />
            </div>
          </div>
          <div class="settings-form-row">
            <div class="settings-form-copy">
              <div class="settings-form-label">
                {{ items?.reranker?.des || '默认 Re-Ranker 模型' }}
              </div>
              <p class="settings-form-description">对检索结果重排序，优先呈现更相关的内容。</p>
            </div>
            <div class="settings-form-control is-compact">
              <RerankModelSelector
                display-name="mini"
                :value="configStore.config?.reranker"
                @change="handleChange('reranker', $event)"
              />
            </div>
          </div>
        </section>
      </section>




    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useConfigStore } from '@/modules/settings/model/config'

import { useUserStore } from '@/modules/identity'
import ModelSelectorComponent from '@/modules/agents/ui/ModelSelectorComponent.vue'
import EmbeddingModelSelector from '@/modules/settings/ui/EmbeddingModelSelector.vue'
import RerankModelSelector from '@/modules/settings/ui/RerankModelSelector.vue'


const configStore = useConfigStore()
const userStore = useUserStore()
const items = computed(() => configStore.config?._config_items || {})
const handleChange = (key, e) => {
  configStore.setConfigValue(key, e)
}

/** 只提交完整的非负整数，清空输入不会修改已保存的限制。 */


/** 只提交不小于 1 的整数，清空输入不会修改已保存的上限。 */


const handleChatModelSelect = (spec) => {
  if (typeof spec === 'string' && spec) {
    configStore.setConfigValue('default_model', spec)
  }
}

const handleFastModelSelect = (spec) => {
  if (typeof spec === 'string' && spec) {
    configStore.setConfigValue('fast_model', spec)
  }
}
</script>
