<template>
  <div class="month-calendar">
    <div class="calendar-nav">
      <el-button @click="$emit('prev')" :icon="ArrowLeft" circle size="small" />
      <span class="month-label">{{ year }}年 {{ month }}月</span>
      <el-button @click="$emit('next')" :icon="ArrowRight" circle size="small" />
    </div>
    <div class="weekday-header">
      <span v-for="d in weekdays" :key="d" class="weekday">{{ d }}</span>
    </div>
    <div class="days-grid">
      <div
        v-for="(day, idx) in calendarDays"
        :key="idx"
        class="day-cell"
        :class="{ 'other-month': !day.currentMonth, 'has-tasks': day.tasks?.length }"
        @click="day.currentMonth && $emit('day-click', day.date)"
      >
        <span class="day-num">{{ day.day }}</span>
        <div class="day-dots" v-if="day.tasks?.length">
          <span
            v-for="t in day.tasks.slice(0, 3)"
            :key="t.id"
            class="dot"
            :class="t.priority"
          ></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  year: number
  month: number
  tasks: Record<string, any[]>
}>()
defineEmits<{
  prev: []
  next: []
  'day-click': [date: string]
}>()

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const calendarDays = computed(() => {
  const firstDay = new Date(props.year, props.month - 1, 1)
  const lastDay = new Date(props.year, props.month, 0)
  const startDayOfWeek = firstDay.getDay()
  const days: any[] = []

  const prevLastDay = new Date(props.year, props.month - 1, 0).getDate()
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const d = prevLastDay - i
    const prevMonth = props.month - 1 || 12
    const prevYear = props.month === 1 ? props.year - 1 : props.year
    const dateStr = `${prevYear}-${String(prevMonth).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({ day: d, currentMonth: false, date: dateStr, tasks: [] })
  }

  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${props.year}-${String(props.month).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({
      day: d,
      currentMonth: true,
      date: dateStr,
      tasks: props.tasks[dateStr] || [],
    })
  }

  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    days.push({ day: d, currentMonth: false, date: '', tasks: [] })
  }

  return days
})
</script>

<style scoped>
.month-calendar { user-select: none; }
.calendar-nav {
  display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 16px;
}
.month-label { font-size: 16px; font-weight: 600; }
.weekday-header { display: grid; grid-template-columns: repeat(7, 1fr); margin-bottom: 4px; }
.weekday { text-align: center; font-size: 13px; color: #909399; padding: 8px 0; }
.days-grid { display: grid; grid-template-columns: repeat(7, 1fr); }
.day-cell {
  aspect-ratio: 1; border: 1px solid #ebeef5; padding: 4px;
  display: flex; flex-direction: column; cursor: pointer;
}
.day-cell.other-month { background: #fafafa; cursor: default; }
.day-cell.has-tasks { background: #ecf5ff; }
.day-num { font-size: 14px; color: #303133; }
.day-dots { display: flex; gap: 2px; margin-top: 4px; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot.high { background: #f56c6c; }
.dot.medium { background: #e6a23c; }
.dot.low { background: #67c23a; }
</style>
