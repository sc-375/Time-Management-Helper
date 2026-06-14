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
      <el-tag v-if="task.due_date" size="small" type="info">{{ task.due_date }}</el-tag>
      <el-tag v-for="tag in tagList" :key="tag" size="small" class="tag-item">{{ tag }}</el-tag>
    </div>
    <div class="card-footer" v-if="task.subtasks?.length">
      <span class="subtask-count">子任务: {{ task.subtasks.length }}</span>
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
  border-left: 3px solid #ddd;
  transition: transform 0.2s;
}
.task-card:hover { transform: translateY(-1px); }
.priority-high { border-left-color: #f56c6c; }
.priority-medium { border-left-color: #e6a23c; }
.priority-low { border-left-color: #67c23a; }
.card-header { display: flex; align-items: center; gap: 8px; }
.priority-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.priority-dot.high { background: #f56c6c; }
.priority-dot.medium { background: #e6a23c; }
.priority-dot.low { background: #67c23a; }
.title { font-size: 14px; font-weight: 500; }
.card-meta { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
.card-footer { margin-top: 8px; }
.subtask-count { font-size: 12px; color: #909399; }
.tag-item { margin-left: 4px; }
</style>
