<template>
  <el-card
    class="task-card"
    :class="[`priority-${task.priority}`, { done: task.status === 'done' }]"
    shadow="hover"
  >
    <div class="card-header">
      <span class="priority-dot" :class="task.priority"></span>
      <span class="title" @click="$emit('click', task)">{{ task.title }}</span>
      <span class="card-actions">
        <el-tooltip content="标记完成" placement="top" v-if="task.status !== 'done'">
          <span class="action-btn check-btn" @click.stop="$emit('complete', task)">
            <el-icon :size="14"><Check /></el-icon>
          </span>
        </el-tooltip>
        <el-popconfirm
          title="确定删除此任务？"
          confirm-button-text="删除"
          cancel-button-text="取消"
          @confirm="$emit('delete', task)"
        >
          <template #reference>
            <span class="action-btn delete-btn" @click.stop>
              <el-icon :size="14"><Close /></el-icon>
            </span>
          </template>
        </el-popconfirm>
      </span>
    </div>
    <div class="card-meta" v-if="task.due_date || task.tags" @click="$emit('click', task)">
      <el-tag v-if="task.due_date" size="small" effect="plain">{{ task.due_date }}</el-tag>
      <el-tag v-for="tag in tagList" :key="tag" size="small" effect="plain" class="tag-item">{{ tag }}</el-tag>
    </div>
    <div class="card-footer" v-if="task.subtasks?.length" @click="$emit('click', task)">
      <span class="subtask-count">{{ task.subtasks.length }} 个子任务</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Check, Close } from '@element-plus/icons-vue'
import type { TaskData } from '@/api/tasks'

const props = defineProps<{ task: TaskData }>()
defineEmits<{
  click: [task: TaskData]
  delete: [task: TaskData]
  complete: [task: TaskData]
}>()

const tagList = computed(() => {
  return props.task.tags ? props.task.tags.split(',').filter(Boolean) : []
})
</script>

<style scoped>
.task-card {
  margin-bottom: 8px;
  cursor: default;
  border-left: none;
  border-radius: var(--radius-sm);
  transition: all 0.18s ease;
  border: 1px solid var(--border-light) !important;
  background: var(--bg-card);
  box-shadow: var(--shadow-sm);
  position: relative;
}
.task-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.task-card.done {
  opacity: 0.65;
}
.task-card.done .title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.priority-high { border-left: 3px solid var(--priority-high); }
.priority-medium { border-left: 3px solid var(--priority-medium); }
.priority-low { border-left: 3px solid var(--priority-low); }

.card-header {
  display: flex; align-items: center; gap: 8px;
}
.priority-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.priority-dot.high { background: var(--priority-high); }
.priority-dot.medium { background: var(--priority-medium); }
.priority-dot.low { background: var(--priority-low); }
.title {
  flex: 1; font-size: 14px; font-weight: 500; color: var(--text-primary);
  cursor: pointer; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.card-actions {
  display: flex; gap: 4px; opacity: 0; transition: opacity 0.15s;
}
.task-card:hover .card-actions { opacity: 1; }

.action-btn {
  width: 24px; height: 24px; display: flex; align-items: center;
  justify-content: center; border-radius: 4px; cursor: pointer;
  transition: all 0.15s;
}
.check-btn { color: var(--priority-low); }
.check-btn:hover { background: rgba(91, 158, 111, 0.1); }
.delete-btn { color: var(--text-muted); }
.delete-btn:hover { background: rgba(224, 85, 90, 0.08); color: var(--priority-high); }

.card-meta {
  margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; cursor: pointer;
}
.card-footer { margin-top: 8px; cursor: pointer; }
.subtask-count {
  font-size: 12px; color: var(--text-secondary);
}
.tag-item { margin-left: 4px; }
</style>
