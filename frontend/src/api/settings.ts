import client from './client'

export const settingsApi = {
  getLLMConfig() {
    return client.get('/settings/llm').then(r => r.data.data)
  },
  updateLLMConfig(data: any) {
    return client.put('/settings/llm', data).then(r => r.data)
  },
  testLLM() {
    return client.post('/settings/llm/test').then(r => r.data)
  },
}
