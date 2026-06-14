<template>
  <div class="task-board-page">
    <div class="board-header">
      <h2>任务看板</h2>
      <div class="header-actions">
        <el-input
          v-model="searchText"
          placeholder="搜索任务..."
          :prefix-icon="Search"
          clearable
          style="width: 240px"
          @input="onSearch"
        />
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon> 创建任务
        </el-button>
        <el-button @click="showAICreateDialog = true">
          <el-icon><MagicStick /></el-icon> AI 快速创建
        </el-button>
      </div>
    </div>

    <div class="kanban-container">
      <KanbanColumn
        title="待办"
        :tasks="todoTasks"
        @task-click="openDetail"
        @drop-task="onDrop"
      />
      <KanbanColumn
        title="进行中"
        :tasks="inProgressTasks"
        @task-click="openDetail"
        @drop-task="onDrop"
      />
      <KanbanColumn
        title="已完成"
        :tasks="doneTasks"
        @task-click="openDetail"
        @drop-task="onDrop"
      />
    </div>

    <TaskForm
      v-model:visible="showCreateDialog"
      @saved="onTaskSaved"
    />
    <TaskForm
      v-if="editingTask"
      v-model:visible="showEditDialog"
      :task="editingTask"
      @saved="onTaskSaved"
    />

    <el-dialog v-model="showAICreateDialog" title="AI 快速创建任务" width="500px">
      <el-input
        v-model="aiText"
        type="textarea"
        :rows="3"
        placeholder="描述你想创建的任务，例如：明天下午3点和王经理开会讨论Q3预算"
      />
      <div v-if="aiPreviews.length" style="margin-top: 16px">
        <el-card v-for="(p, i) in aiPreviews" :key="i" style="margin-bottom: 8px">
          <div>{{ p.title }} — {{ p.priority }} — {{ p.estimated_minutes }}分钟</div>
          <el-button size="small" type="primary" @click="confirmAITask(p)">添加</el-button>
        </el-card>
      </div>
      <template #footer>
        <el-button @click="showAICreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="aiLoading" @click="doAIParse">解析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Plus, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import KanbanColumn from '@/components/KanbanColumn.vue'
import TaskForm from '@/components/TaskForm.vue'
import { useTaskStore } from '@/stores/task'
import { aiApi } from '@/api/ai'
import type { TaskData } from '@/api/tasks'

const store = useTaskStore()
const searchText = ref('')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showAICreateDialog = ref(false)
const editingTask = ref<TaskData | null>(null)
const aiText = ref('')
const aiPreviews = ref<any[]>([])
const aiLoading = ref(false)

const todoTasks = computed(() => store.tasks.filter(t => t.status === 'todo'))
const inProgressTasks = computed(() => store.tasks.filter(t => t.status === 'in_progress'))
const doneTasks = computed(() => store.tasks.filter(t => t.status === 'done'))

onMounted(() => store.fetchTasks())

function onSearch() {
  store.fetchTasks(searchText.value ? { search: searchText.value } : undefined)
}

function onDrop(taskId: number, newStatus: string) {
  store.updateStatus(taskId, newStatus)
}

function openDetail(task: TaskData) {
  editingTask.value = task
  showEditDialog.value = true
}

function onTaskSaved() {
  showCreateDialog.value = false
  showEditDialog.value = false
  editingTask.value = null
  store.fetchTasks()
}

async function doAIParse() {
  if (!aiText.value.trim()) return
  aiLoading.value = true
  try {
    aiPreviews.value = await aiApi.createTaskFromNL(aiText.value)
  } finally {
    aiLoading.value = false
  }
}

async function confirmAITask(preview: any) {
  await store.createTask(preview)
  ElMessage.success('任务已添加')
  aiPreviews.value = aiPreviews.value.filter(p => p !== preview)
}
</script>

<style scoped>
.task-board-page { height: 100%; display: flex; flex-direction: column; }
.board-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; border-bottom: 1px solid #e4e7ed;
}
.board-header h2 { margin: 0; font-size: 20px; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.kanban-container {
  flex: 1; display: flex; gap: 16px; padding: 24px; overflow-x: auto;
}
</style>
