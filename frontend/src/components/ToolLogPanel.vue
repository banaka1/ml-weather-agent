<template>
  <div class="tool-log-panel">
    <el-collapse>
      <el-collapse-item name="tools">
        <template #title>
          <span class="tool-title">🔧 工具调用 ({{ tools.length }})</span>
        </template>
        <div v-for="(t, i) in tools" :key="i" class="tool-item">
          <div class="tool-head">
            <el-tag size="small" type="primary">{{ t.name }}</el-tag>
            <span class="latency">{{ t.ms }}ms</span>
          </div>
          <pre class="tool-result">{{ t.result }}</pre>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import type { ToolCallInfo } from '@/types/models'

defineProps<{ tools: ToolCallInfo[] }>()
</script>

<style scoped lang="scss">
.tool-log-panel {
  margin-top: 8px;
}
.tool-title {
  font-size: 13px;
  color: var(--text-secondary);
}
.tool-item {
  margin-bottom: 12px;
}
.tool-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.latency {
  font-size: 12px;
  color: var(--text-secondary);
}
.tool-result {
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 8px;
  margin: 0;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
  color: var(--text-secondary);
}
</style>
