<template>
  <div class="schema-panel">
    <div class="panel-header" @click="expanded = !expanded">
      <div class="title">
        <el-icon><Coin /></el-icon>
        <span>可查询数据表</span>
        <span class="count">{{ tables.length }} 张表</span>
      </div>
      <el-icon class="arrow" :class="{ expanded }">
        <ArrowDown />
      </el-icon>
    </div>

    <transition name="slide">
      <div v-show="expanded" class="panel-body">
        <div class="tables">
          <div
            v-for="t in tables"
            :key="t.name"
            class="table-card"
          >
            <div class="table-name">
              <el-icon><Grid /></el-icon>
              <span>{{ t.name }}</span>
            </div>
            <div class="table-desc">{{ t.desc }}</div>
            <div class="fields">
              <el-tag
                v-for="f in t.fields"
                :key="f.name"
                size="small"
                :type="f.type"
                effect="plain"
              >
                {{ f.name }}
              </el-tag>
            </div>
            <div v-if="t.note" class="table-note">{{ t.note }}</div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Coin, ArrowDown, Grid } from '@element-plus/icons-vue'

const expanded = ref(true)

interface Field {
  name: string
  type: '' | 'success' | 'warning' | 'danger' | 'info'
}

interface TableSchema {
  name: string
  desc: string
  fields: Field[]
  note?: string
}

const tables: TableSchema[] = [
  {
    name: 'servers',
    desc: '服务器信息表',
    fields: [
      { name: 'id', type: 'info' },
      { name: 'hostname', type: '' },
      { name: 'ip', type: '' },
      { name: 'os', type: '' },
      { name: 'status', type: 'success' },
      { name: 'created_at', type: 'info' },
    ],
    note: 'status: running / stopped',
  },
  {
    name: 'metrics',
    desc: '服务器性能指标表',
    fields: [
      { name: 'id', type: 'info' },
      { name: 'server_id', type: 'info' },
      { name: 'cpu', type: 'warning' },
      { name: 'memory', type: 'warning' },
      { name: 'disk', type: 'warning' },
      { name: 'ts', type: 'info' },
    ],
    note: 'cpu / memory / disk 为使用率（0~100）',
  },
  {
    name: 'alerts',
    desc: '告警信息表',
    fields: [
      { name: 'id', type: 'info' },
      { name: 'server_id', type: 'info' },
      { name: 'level', type: 'danger' },
      { name: 'message', type: '' },
      { name: 'ts', type: 'info' },
    ],
    note: 'level: info / warning / critical',
  },
]
</script>

<style scoped lang="scss">
.schema-panel {
  background: #fafbfc;
  border-bottom: 1px solid var(--border-color);
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 20px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;

  &:hover {
    background: #f0f2f5;
  }
  .title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--text-primary);
    font-weight: 500;

    .el-icon {
      color: var(--brand-primary);
    }
    .count {
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: normal;
      background: var(--brand-primary-light);
      padding: 1px 8px;
      border-radius: 10px;
    }
  }
  .arrow {
    color: var(--text-secondary);
    transition: transform 0.2s;
    font-size: 14px;

    &.expanded {
      transform: rotate(180deg);
    }
  }
}
.panel-body {
  padding: 0 20px 12px;
}
.tables {
  display: flex;
  gap: 12px;
  overflow-x: auto;
}
.table-card {
  flex: 1;
  min-width: 200px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 10px 12px;
  transition: border-color 0.2s, box-shadow 0.2s;

  &:hover {
    border-color: var(--brand-primary);
    box-shadow: 0 2px 8px rgba(79, 124, 255, 0.12);
  }
}
.table-name {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: var(--brand-primary);
  margin-bottom: 2px;

  .el-icon {
    font-size: 14px;
  }
}
.table-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.fields {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.table-note {
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-secondary);
  padding-top: 6px;
  border-top: 1px dashed var(--border-color);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  max-height: 300px;
}
</style>
