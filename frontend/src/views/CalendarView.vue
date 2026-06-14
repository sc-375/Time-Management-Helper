<template>
  <div class="calendar-page">
    <div class="page-header">
      <h2>日历视图</h2>
      <el-radio-group v-model="viewMode">
        <el-radio-button value="month">月视图</el-radio-button>
        <el-radio-button value="week">周视图</el-radio-button>
      </el-radio-group>
    </div>

    <div class="calendar-content">
      <MonthCalendar
        v-if="viewMode === 'month'"
        :year="currentYear"
        :month="currentMonth"
        :tasks="tasksByDate"
        @prev="changeMonth(-1)"
        @next="changeMonth(1)"
        @day-click="onDayClick"
      />
      <WeekCalendar
        v-else
        :start-date="weekStart"
        :tasks="tasksByDate"
        @prev="changeWeek(-1)"
        @next="changeWeek(1)"
      />
    </div>

    <el-dialog v-model="showDayDialog" :title="selectedDate" width="480px">
      <div v-for="task in selectedTasks" :key="task.id" style="margin-bottom: 8px">
        <el-card>
          <strong>{{ task.title }}</strong>
          <el-tag size="small" :type="priorityType(task.priority)" style="margin-left: 8px">{{ task.priority }}</el-tag>
          <el-tag size="small" style="margin-left: 4px">{{ task.status }}</el-tag>
        </el-card>
      </div>
      <div v-if="!selectedTasks.length">当天无任务</div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MonthCalendar from '@/components/MonthCalendar.vue'
import WeekCalendar from '@/components/WeekCalendar.vue'
import { calendarApi } from '@/api/calendar'

const viewMode = ref<'month' | 'week'>('month')
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const tasksByDate = ref<Record<string, any[]>>({})
const weekStart = ref('')
const showDayDialog = ref(false)
const selectedDate = ref('')
const selectedTasks = ref<any[]>([])

onMounted(async () => {
  await loadMonth()
  setWeekStart()
})

async function loadMonth() {
  tasksByDate.value = await calendarApi.getMonth(currentYear.value, currentMonth.value)
}

async function loadWeek() {
  const end = new Date(weekStart.value + 'T00:00:00')
  end.setDate(end.getDate() + 6)
  const endStr = end.toISOString().slice(0, 10)
  tasksByDate.value = await calendarApi.getWeek(weekStart.value, endStr)
}

function changeMonth(delta: number) {
  currentMonth.value += delta
  if (currentMonth.value > 12) { currentMonth.value = 1; currentYear.value++ }
  if (currentMonth.value < 1) { currentMonth.value = 12; currentYear.value-- }
  loadMonth()
}

function setWeekStart() {
  const today = new Date()
  const day = today.getDay()
  const diff = today.getDate() - day
  weekStart.value = new Date(today.getFullYear(), today.getMonth(), diff).toISOString().slice(0, 10)
}

function changeWeek(delta: number) {
  const d = new Date(weekStart.value + 'T00:00:00')
  d.setDate(d.getDate() + delta * 7)
  weekStart.value = d.toISOString().slice(0, 10)
  loadWeek()
}

function onDayClick(dateStr: string) {
  selectedDate.value = dateStr
  selectedTasks.value = tasksByDate.value[dateStr] || []
  showDayDialog.value = true
}

function priorityType(p: string) {
  return p === 'high' ? 'danger' : p === 'medium' ? 'warning' : 'success'
}
</script>

<style scoped>
.calendar-page { height: 100%; display: flex; flex-direction: column; }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; border-bottom: 1px solid #e4e7ed;
}
.page-header h2 { margin: 0; }
.calendar-content { flex: 1; padding: 24px; overflow-y: auto; }
</style>
