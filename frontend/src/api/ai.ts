import client from './client'

export const aiApi = {
  chat(message: string) {
    return client.post('/ai/chat', { message }).then(r => r.data.data)
  },
  getHistory() {
    return client.get('/ai/history').then(r => r.data.data)
  },
  clearHistory() {
    return client.delete('/ai/history').then(r => r.data)
  },
  createTaskFromNL(text: string) {
    return client.post('/ai/create-task', { text }).then(r => r.data.data)
  },
}
