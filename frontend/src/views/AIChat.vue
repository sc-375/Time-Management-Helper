<template>
  <div class="ai-chat-page">
    <div class="chat-header">
      <h2>AI 助手</h2>
      <div class="header-right">
        <el-tag :type="llmConnected ? 'success' : 'danger'" size="small">
          {{ llmConnected ? '已连接' : '未连接' }} — {{ llmModel }}
        </el-tag>
        <el-button @click="store.clearHistory()" size="small">清空对话</el-button>
      </div>
    </div>

    <div class="chat-body" ref="chatBodyRef">
      <ChatMessage
        v-for="msg in store.messages"
        :key="msg.id || Math.random()"
        :role="msg.role"
        :content="msg.content"
        :task-previews="msg.task_previews"
        @add-task="addTask"
      />
      <div v-if="store.loading" class="typing-hint">AI 正在思考...</div>
    </div>

    <div class="chat-input">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入消息，例如：帮我规划明天的任务..."
        @keydown.enter.exact.prevent="send"
      />
      <el-button type="primary" @click="send" :loading="store.loading" style="margin-left: 8px">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import ChatMessage from '@/components/ChatMessage.vue'
import { useAiStore } from '@/stores/ai'
import { useTaskStore } from '@/stores/task'
import { settingsApi } from '@/api/settings'

const store = useAiStore()
const taskStore = useTaskStore()
const inputText = ref('')
const chatBodyRef = ref<HTMLElement>()
const llmConnected = ref(false)
const llmModel = ref('')

onMounted(async () => {
  await store.loadHistory()
  try {
    const config = await settingsApi.getLLMConfig()
    llmModel.value = config.model
    const test = await settingsApi.testLLM()
    llmConnected.value = test.code === 0
  } catch { llmConnected.value = false }
})

async function send() {
  const text = inputText.value.trim()
  if (!text) return
  inputText.value = ''
  await store.sendMessage(text)
  await nextTick()
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}

async function addTask(task: any) {
  try {
    await taskStore.createTask(task)
    ElMessage.success(`任务「${task.title}」已添加到待办列表`)
  } catch { /* handled by interceptor */ }
}
</script>

<style scoped>
.ai-chat-page { height: 100%; display: flex; flex-direction: column; }
.chat-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; border-bottom: 1px solid #e4e7ed;
}
.chat-header h2 { margin: 0; }
.header-right { display: flex; align-items: center; gap: 12px; }
.chat-body { flex: 1; overflow-y: auto; padding: 24px; }
.typing-hint { color: #909399; font-size: 13px; padding: 12px; }
.chat-input {
  display: flex; align-items: flex-end; padding: 16px 24px;
  border-top: 1px solid #e4e7ed; background: #fff;
}
</style>
