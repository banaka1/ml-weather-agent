<template>
  <div class="session-list">
    <el-button type="primary" class="new-btn" @click="$emit('new')">
      <el-icon><Plus /></el-icon> 新对话
    </el-button>
    <ul class="list">
      <li
        v-for="s in sessions"
        :key="s.id"
        :class="{ active: s.id === currentId }"
        @click="$emit('select', s.id)"
      >
        <div class="meta">
          <span class="title" :title="s.title">{{ s.title }}</span>
          <span class="time">{{ formatTime(s.updated_at) }}</span>
        </div>
        <button
          class="del-btn"
          type="button"
          title="删除对话"
          @click.stop="handleDelete(s)"
        >
          <el-icon><Delete /></el-icon>
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import type { SessionItem } from '@/types/models'

defineProps<{
  sessions: SessionItem[]
  currentId: string
}>()

const emit = defineEmits<{
  (e: 'new'): void
  (e: 'select', id: string): void
  (e: 'delete', id: string): void
}>()

function formatTime(s: string) {
  if (!s) return ''
  return s.slice(5, 16) // MM-DD HH:mm
}

async function handleDelete(s: SessionItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除对话「${s.title}」吗？删除后不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
    emit('delete', s.id)
  } catch {
    // 用户取消，不做处理
  }
}
</script>

<style scoped lang="scss">
.session-list {
  padding: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.new-btn {
  width: 100%;
  margin-bottom: 12px;
}
.list {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
}
li {
  padding: 10px 12px;
  border-radius: var(--radius);
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    background: #ebedf0;

    .del-btn {
      opacity: 1;
    }
  }
  &.active {
    background: var(--brand-primary-light);
  }
  .meta {
    flex: 1;
    min-width: 0;
  }
  .title {
    display: block;
    font-size: 14px;
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .time {
    font-size: 12px;
    color: var(--text-secondary);
  }
  .del-btn {
    flex-shrink: 0;
    width: 26px;
    height: 26px;
    border: none;
    background: transparent;
    border-radius: 6px;
    cursor: pointer;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.2s, background 0.2s, color 0.2s;

    &:hover {
      background: #fff;
      color: #f56c6c;
    }
  }
}
</style>
