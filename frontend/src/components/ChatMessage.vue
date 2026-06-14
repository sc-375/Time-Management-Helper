<template>
  <div class="chat-msg" :class="role">
    <div class="msg-body">
      <div class="msg-content" v-html="renderedContent"></div>
      <TaskPreviewCard
        v-for="(task, i) in taskPreviews"
        :key="i"
        :task="task"
        @add="$emit('add-task', task)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import TaskPreviewCard from './TaskPreviewCard.vue'

const props = defineProps<{
  role: string
  content: string
  taskPreviews?: any[]
}>()
defineEmits<{ 'add-task': [task: any] }>()

const renderedContent = computed(() => {
  const cleaned = props.content.replace(/```task[\s\S]*?```/g, '')
  return marked(cleaned)
})
</script>

<style scoped>
.chat-msg { display: flex; margin-bottom: 20px; }
.chat-msg.assistant { justify-content: flex-start; }
.chat-msg.user { justify-content: flex-end; }
.msg-body { max-width: 72%; }

.msg-content {
  padding: 14px 18px; font-size: 14px; line-height: 1.65;
  border-radius: 14px;
}
.chat-msg.user .msg-content {
  background: var(--accent); color: #fff;
  border-bottom-right-radius: 4px;
}
.chat-msg.assistant .msg-content {
  background: var(--bg-card); color: var(--text-primary);
  border: 1px solid var(--border-light);
  border-bottom-left-radius: 4px;
}
</style>
