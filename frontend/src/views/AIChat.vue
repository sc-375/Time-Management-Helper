<template>
  <div class="ai-chat-page">
    <header class="chat-header">
      <h2>AI 助手</h2>
      <div class="header-right">
        <span class="conn-dot" :class="{ connected: llmConnected }"></span>
        <span class="conn-label" :class="{ connected: llmConnected }">
          {{ llmConnected ? '已连接' : '未连接' }}
        </span>
        <span class="model-name">{{ llmModel }}</span>
        <el-button @click="store.clearHistory()" size="small" class="btn-clear">清空对话</el-button>
      </div>
    </header>

    <div class="chat-body" ref="chatBodyRef">
      <div v-if="store.messages.length === 0" class="chat-empty">
        <div class="empty-icon">—</div>
        <p>输入消息开始与 AI 对话</p>
      </div>
      <ChatMessage
        v-for="msg in store.messages"
        :key="msg.id || Math.random()"
        :role="msg.role"
        :content="msg.content"
        :task-previews="msg.task_previews"
        @add-task="addTask"
      />
      <div v-if="store.loading" class="typing-hint">
        <span class="typing-dots"><span>•</span><span>•</span><span>•</span></span>
      </div>
    </div>

    <div class="chat-input">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入消息..."
        @keydown.enter.exact.prevent="send"
        class="input-area"
      />
      <el-button type="primary" @click="send" :loading="store.loading" class="btn-send">
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
    ElMessage.success(`「${task.title}」已添加到待办列表`)
  } catch { /* handled by interceptor */ }
}
</script>

<style scoped>
.ai-chat-page { height: 100%; display: flex; flex-direction: column; }

.chat-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 28px; border-bottom: 1px solid var(--border);
}
.chat-header h2 { margin: 0; font-size: 18px; font-weight: 600; color: var(--text-primary); }

.header-right { display: flex; align-items: center; gap: 8px; }
.conn-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--priority-high);
}
.conn-dot.connected { background: var(--priority-low); }
.conn-label { font-size: 12px; color: var(--priority-high); font-weight: 500; }
.conn-label.connected { color: var(--priority-low); }
.model-name { font-size: 12px; color: var(--text-muted); margin-right: 8px; }
.btn-clear { color: var(--text-secondary); }

.chat-body { flex: 1; overflow-y: auto; padding: 20px 28px; }

.chat-empty {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; height: 100%; color: var(--text-muted);
}
.empty-icon { font-size: 32px; margin-bottom: 12px; opacity: 0.3; }
.chat-empty p { font-size: 14px; }

.typing-hint { padding: 12px 0; }
.typing-dots span {
  display: inline-block; animation: blink 1.4s infinite;
  color: var(--accent); font-size: 20px; margin: 0 2px;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
  0%, 60%, 100% { opacity: 0.2; }
  30% { opacity: 1; }
}

.chat-input {
  display: flex; align-items: flex-end; gap: 10px;
  padding: 16px 28px; border-top: 1px solid var(--border);
  background: var(--bg-card);
}
.input-area { flex: 1; }
.btn-send { flex-shrink: 0; }
</style>
