import { defineStore } from 'pinia'
import { ref } from 'vue'
import { aiApi } from '@/api/ai'

export interface ChatMessage {
  id?: number
  role: string
  content: string
  task_previews?: any[]
}

export const useAiStore = defineStore('ai', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)

  async function sendMessage(text: string) {
    messages.value.push({ role: 'user', content: text })
    loading.value = true
    try {
      const result = await aiApi.chat(text)
      messages.value.push({
        role: 'assistant',
        content: result.reply,
        task_previews: result.task_previews,
      })
    } finally {
      loading.value = false
    }
  }

  async function loadHistory() {
    messages.value = await aiApi.getHistory()
  }

  async function clearHistory() {
    await aiApi.clearHistory()
    messages.value = []
  }

  return { messages, loading, sendMessage, loadHistory, clearHistory }
})
