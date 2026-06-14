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
.chat-msg { display: flex; margin-bottom: 16px; }
.chat-msg.assistant { justify-content: flex-start; }
.chat-msg.user { justify-content: flex-end; }
.msg-body { max-width: 75%; }
.chat-msg.user .msg-content {
  background: #409eff; color: #fff; border-radius: 12px 12px 4px 12px;
}
.chat-msg.assistant .msg-content {
  background: #f5f7fa; color: #303133; border-radius: 12px 12px 12px 4px;
}
.msg-content { padding: 12px 16px; font-size: 14px; line-height: 1.6; }
</style>
