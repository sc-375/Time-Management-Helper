<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="isEditing ? '编辑任务' : '创建任务'"
    width="560px"
    @close="resetForm"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="任务标题" maxlength="200" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="详细描述（可选）" />
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="优先级">
            <el-select v-model="form.priority">
              <el-option label="🔴 高" value="high" />
              <el-option label="🟡 中" value="medium" />
              <el-option label="🟢 低" value="low" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态">
            <el-select v-model="form.status">
              <el-option label="待办" value="todo" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="done" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="截止日期">
            <el-date-picker v-model="form.due_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="截止时间">
            <el-time-picker v-model="form.due_time" placeholder="选择时间" value-format="HH:mm:ss" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="预估耗时">
        <el-input-number v-model="form.estimated_minutes" :min="0" :step="15" placeholder="分钟" />
      </el-form-item>
      <el-form-item label="标签">
        <el-input v-model="form.tags" placeholder="用逗号分隔，如：项目,紧急" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { TaskData } from '@/api/tasks'
import { useTaskStore } from '@/stores/task'

const props = defineProps<{
  visible: boolean
  task?: TaskData | null
}>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
  saved: []
}>()

const store = useTaskStore()
const formRef = ref()
const isEditing = ref(false)

const form = reactive({
  title: '',
  description: '',
  priority: 'medium',
  status: 'todo',
  due_date: null as string | null,
  due_time: null as string | null,
  estimated_minutes: null as number | null,
  tags: '',
})

const rules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
}

watch(() => props.visible, (val) => {
  if (val && props.task) {
    isEditing.value = true
    Object.assign(form, {
      title: props.task.title,
      description: props.task.description || '',
      priority: props.task.priority,
      status: props.task.status,
      due_date: props.task.due_date || null,
      due_time: props.task.due_time || null,
      estimated_minutes: props.task.estimated_minutes || null,
      tags: props.task.tags || '',
    })
  } else if (val) {
    isEditing.value = false
    resetForm()
  }
})

function resetForm() {
  isEditing.value = false
  form.title = ''
  form.description = ''
  form.priority = 'medium'
  form.status = 'todo'
  form.due_date = null
  form.due_time = null
  form.estimated_minutes = null
  form.tags = ''
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  try {
    if (isEditing.value && props.task?.id) {
      await store.updateTask(props.task.id, { ...form })
      ElMessage.success('任务已更新')
    } else {
      await store.createTask({ ...form })
      ElMessage.success('任务已创建')
    }
    emit('saved')
  } catch { /* error handled by interceptor */ }
}
</script>
