<template>
  <div class="task-preview">
    <div class="preview-content">
      <strong>{{ task.title }}</strong>
      <el-tag size="small" :type="priorityType(task.priority)" style="margin-left: 8px">{{ task.priority }}</el-tag>
      <span style="margin-left: 8px; color: #909399; font-size: 13px">{{ task.estimated_minutes }}分钟</span>
      <span v-if="task.due_date" style="margin-left: 8px; color: #909399; font-size: 13px">{{ task.due_date }}</span>
    </div>
    <el-button type="primary" size="small" @click="$emit('add', task)">添加到待办</el-button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ task: { title: string; priority: string; estimated_minutes: number; due_date?: string } }>()
defineEmits<{ add: [task: any] }>()

function priorityType(p: string) {
  return p === 'high' ? 'danger' : p === 'medium' ? 'warning' : 'success'
}
</script>

<style scoped>
.task-preview {
  margin: 8px 0; padding: 12px; border: 1px solid #e4e7ed; border-radius: 8px;
  display: flex; justify-content: space-between; align-items: center;
}
.preview-content { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
</style>
