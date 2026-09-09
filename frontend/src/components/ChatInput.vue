<template>
  <div class="chat-input">
    <el-input
      v-model="text"
      type="textarea"
      :rows="3"
      placeholder="输入消息，Enter 发送，Shift+Enter 换行"
      :disabled="loading"
      @keydown="onKeydown"
    />
    <el-button
      type="primary"
      class="send-btn"
      :loading="loading"
      @click="send"
    >
      发送
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ loading: boolean }>()
const emit = defineEmits<{ (e: 'send', text: string): void }>()

const text = ref('')

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

function send() {
  if (!text.value.trim() || props.loading) return
  emit('send', text.value.trim())
  text.value = ''
}
</script>

<style scoped lang="scss">
.chat-input {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  background: #fff;
}
.send-btn {
  margin-top: 8px;
  width: 100%;
}
</style>
