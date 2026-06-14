<template>
  <div class="week-calendar">
    <div class="calendar-nav">
      <el-button @click="$emit('prev')" :icon="ArrowLeft" circle size="small" />
      <span class="week-label">{{ weekLabel }}</span>
      <el-button @click="$emit('next')" :icon="ArrowRight" circle size="small" />
    </div>
    <div class="week-grid">
      <div v-for="day in weekDays" :key="day.date" class="week-day-col">
        <div class="day-header">
          <span class="day-name">{{ day.name }}</span>
          <span class="day-date">{{ day.label }}</span>
        </div>
        <div class="day-tasks">
          <div
            v-for="task in day.tasks"
            :key="task.id"
            class="week-task-item"
            :class="task.priority"
            @click="$emit('task-click', task)"
          >
            <span class="task-title">{{ task.title }}</span>
            <span class="task-time" v-if="task.due_time">{{ task.due_time.slice(0, 5) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  startDate: string
  tasks: Record<string, any[]>
}>()
defineEmits<{
  prev: []
  next: []
  'task-click': [task: any]
}>()

const dayNames = ['日', '一', '二', '三', '四', '五', '六']

const weekDays = computed(() => {
  const start = new Date(props.startDate + 'T00:00:00')
  const days = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(start)
    d.setDate(d.getDate() + i)
    const dateStr = d.toISOString().slice(0, 10)
    days.push({
      name: dayNames[d.getDay()],
      label: `${d.getMonth() + 1}/${d.getDate()}`,
      date: dateStr,
      tasks: props.tasks[dateStr] || [],
    })
  }
  return days
})

const weekLabel = computed(() => {
  if (weekDays.value.length) {
    return `${weekDays.value[0].date} ~ ${weekDays.value[6].date}`
  }
  return ''
})
</script>

<style scoped>
.week-calendar { }
.calendar-nav {
  display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 16px;
}
.week-label { font-size: 16px; font-weight: 600; }
.week-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.week-day-col { border: 1px solid #ebeef5; min-height: 400px; }
.day-header {
  text-align: center; padding: 8px; background: #f5f7fa; border-bottom: 1px solid #ebeef5;
}
.day-name { font-size: 12px; color: #909399; }
.day-date { font-size: 16px; font-weight: 600; margin-left: 4px; }
.day-tasks { padding: 4px; }
.week-task-item {
  padding: 6px 8px; margin-bottom: 4px; border-radius: 4px;
  font-size: 12px; cursor: pointer; background: #ecf5ff;
  border-left: 3px solid #409eff;
}
.week-task-item.high { background: #fef0f0; border-left-color: #f56c6c; }
.week-task-item.medium { background: #fdf6ec; border-left-color: #e6a23c; }
.week-task-item.low { background: #f0f9eb; border-left-color: #67c23a; }
.task-title { display: block; }
.task-time { color: #909399; font-size: 11px; }
</style>
