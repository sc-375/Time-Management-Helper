<template>
  <el-card
    class="task-card"
    :class="`priority-${task.priority}`"
    shadow="hover"
    @click="$emit('click', task)"
  >
    <div class="card-header">
      <span class="priority-dot" :class="task.priority"></span>
      <span class="title">{{ task.title }}</span>
    </div>
    <div class="card-meta" v-if="task.due_date || task.tags">
      <el-tag v-if="task.due_date" size="small" effect="plain">{{ task.due_date }}</el-tag>
      <el-tag v-for="tag in tagList" :key="tag" size="small" effect="plain" class="tag-item">{{ tag }}</el-tag>
    </div>
    <div class="card-footer" v-if="task.subtasks?.length">
      <span class="subtask-count">{{ task.subtasks.length }} 个子任务</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TaskData } from '@/api/tasks'

const props = defineProps<{ task: TaskData }>()
defineEmits<{ click: [task: TaskData] }>()

const tagList = computed(() => {
  return props.task.tags ? props.task.tags.split(',').filter(Boolean) : []
})
</script>

<style scoped>
.task-card {
  margin-bottom: 8px;
  cursor: pointer;
  border-left: none;
  border-radius: var(--radius-sm);
  transition: all 0.18s ease;
  border: 1px solid var(--border-light) !important;
  background: var(--bg-card);
  box-shadow: var(--shadow-sm);
}
.task-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.priority-high { border-left: 3px solid var(--priority-high); }
.priority-medium { border-left: 3px solid var(--priority-medium); }
.priority-low { border-left: 3px solid var(--priority-low); }

.card-header {
  display: flex; align-items: center; gap: 8px;
}
.priority-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.priority-dot.high { background: var(--priority-high); }
.priority-dot.medium { background: var(--priority-medium); }
.priority-dot.low { background: var(--priority-low); }
.title {
  font-size: 14px; font-weight: 500; color: var(--text-primary);
}
.card-meta {
  margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px;
}
.card-footer { margin-top: 8px; }
.subtask-count {
  font-size: 12px; color: var(--text-secondary);
}
.tag-item { margin-left: 4px; }
</style>
