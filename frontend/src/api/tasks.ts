import client from './client'

export interface TaskData {
  id?: number
  title: string
  description?: string
  priority: string
  status: string
  due_date?: string | null
  due_time?: string | null
  estimated_minutes?: number | null
  actual_minutes?: number | null
  parent_id?: number | null
  tags: string
  created_at?: string
  updated_at?: string
  subtasks?: TaskData[]
}

export const taskApi = {
  list(params?: Record<string, string>) {
    return client.get('/tasks', { params }).then(r => r.data.data)
  },
  create(data: Partial<TaskData>) {
    return client.post('/tasks', data).then(r => r.data.data)
  },
  get(id: number) {
    return client.get(`/tasks/${id}`).then(r => r.data.data)
  },
  update(id: number, data: Partial<TaskData>) {
    return client.put(`/tasks/${id}`, data).then(r => r.data.data)
  },
  delete(id: number) {
    return client.delete(`/tasks/${id}`).then(r => r.data)
  },
  updateStatus(id: number, status: string) {
    return client.patch(`/tasks/${id}/status`, { status }).then(r => r.data.data)
  },
}
