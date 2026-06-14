import client from './client'

export const emailApi = {
  getConfig() {
    return client.get('/email/config').then(r => r.data.data)
  },
  updateConfig(data: any) {
    return client.put('/email/config', data).then(r => r.data)
  },
  test() {
    return client.post('/email/test').then(r => r.data)
  },
  listReminders(taskId: number) {
    return client.get('/reminders', { params: { task_id: taskId } }).then(r => r.data.data)
  },
  createReminder(data: { task_id: number; remind_at: string; method: string }) {
    return client.post('/reminders', data).then(r => r.data.data)
  },
  deleteReminder(id: number) {
    return client.delete(`/reminders/${id}`).then(r => r.data)
  },
}
