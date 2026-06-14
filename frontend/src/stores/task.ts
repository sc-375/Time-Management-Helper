import { defineStore } from 'pinia'
import { ref } from 'vue'
import { taskApi, type TaskData } from '@/api/tasks'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<TaskData[]>([])
  const loading = ref(false)

  async function fetchTasks(params?: Record<string, string>) {
    loading.value = true
    try {
      tasks.value = await taskApi.list(params)
    } finally {
      loading.value = false
    }
  }

  async function createTask(data: Partial<TaskData>) {
    const task = await taskApi.create(data)
    await fetchTasks()
    return task
  }

  async function updateTask(id: number, data: Partial<TaskData>) {
    const task = await taskApi.update(id, data)
    await fetchTasks()
    return task
  }

  async function deleteTask(id: number) {
    await taskApi.delete(id)
    await fetchTasks()
  }

  async function updateStatus(id: number, status: string) {
    await taskApi.updateStatus(id, status)
    await fetchTasks()
  }

  return { tasks, loading, fetchTasks, createTask, updateTask, deleteTask, updateStatus }
})
