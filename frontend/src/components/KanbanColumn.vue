<template>
  <div class="kanban-column">
    <div class="column-header">
      <span class="column-title">{{ title }}</span>
      <el-tag size="small" type="info">{{ tasks.length }}</el-tag>
    </div>
    <div class="column-body" @dragover.prevent @drop="onDrop">
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @click="$emit('task-click', task)"
        draggable="true"
        @dragstart="onDragStart($event, task)"
      />
      <div v-if="tasks.length === 0" class="empty-hint">暂无任务</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import TaskCard from './TaskCard.vue'
import type { TaskData } from '@/api/tasks'

defineProps<{ title: string; tasks: TaskData[] }>()
const emit = defineEmits<{
  'task-click': [task: TaskData]
  'drop-task': [taskId: number, newStatus: string]
}>()

function onDragStart(e: DragEvent, task: TaskData) {
  e.dataTransfer!.setData('taskId', String(task.id))
}

function onDrop(e: DragEvent) {
  const taskId = Number(e.dataTransfer!.getData('taskId'))
  const statusMap: Record<string, string> = {
    '待办': 'todo',
    '进行中': 'in_progress',
    '已完成': 'done',
  }
  const colTitle = (e.currentTarget as HTMLElement).closest('.kanban-column')?.querySelector('.column-title')?.textContent
  const newStatus = statusMap[colTitle || ''] || 'todo'
  if (taskId) emit('drop-task', taskId, newStatus)
}
</script>

<style scoped>
.kanban-column {
  flex: 1; min-width: 280px; max-width: 400px;
  background: #f5f7fa; border-radius: 8px; padding: 12px;
  display: flex; flex-direction: column;
}
.column-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #e4e7ed;
}
.column-title { font-size: 15px; font-weight: 600; }
.column-body { flex: 1; overflow-y: auto; min-height: 200px; }
.empty-hint { text-align: center; color: #c0c4cc; padding: 40px 0; font-size: 14px; }
</style>
