<template>
  <div class="kanban-column">
    <div class="column-header">
      <span class="column-title">{{ title }}</span>
      <span class="column-count">{{ tasks.length }}</span>
    </div>
    <div class="column-body" @dragover.prevent @drop="onDrop">
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @click="$emit('task-click', task)"
        @delete="$emit('delete-task', task)"
        @complete="$emit('complete-task', task)"
        draggable="true"
        @dragstart="onDragStart($event, task)"
      />
      <div v-if="tasks.length === 0" class="empty-hint">—</div>
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
  'delete-task': [task: TaskData]
  'complete-task': [task: TaskData]
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
  background: var(--bg-kanban-col);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex; flex-direction: column;
}
.column-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.column-title {
  font-size: 14px; font-weight: 600; color: var(--text-primary);
  letter-spacing: 0.3px;
}
.column-count {
  font-size: 11px; font-weight: 600; color: var(--text-muted);
  background: var(--bg-card); padding: 2px 8px; border-radius: 10px;
}
.column-body {
  flex: 1; overflow-y: auto; min-height: 200px; padding: 2px;
}
.empty-hint {
  text-align: center; color: var(--text-muted); padding: 40px 0;
  font-size: 18px; font-weight: 300;
}
</style>
