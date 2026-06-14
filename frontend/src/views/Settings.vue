<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>设置</h2>
    </div>

    <div class="settings-content">
      <!-- LLM Config Card -->
      <el-card class="config-card">
        <template #header>
          <div class="card-header-row">
            <span class="card-title">🤖 大模型配置</span>
            <el-button size="small" :loading="llmTesting" @click="testLLM">测试连接</el-button>
          </div>
        </template>
        <el-form :model="llmForm" label-width="100px">
          <el-form-item label="Provider">
            <el-select v-model="llmForm.provider">
              <el-option label="Ollama (本地)" value="ollama" />
              <el-option label="OpenAI" value="openai" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
          <el-form-item label="Base URL">
            <el-input v-model="llmForm.base_url" placeholder="http://localhost:11434" />
          </el-form-item>
          <el-form-item label="API Key" v-if="llmForm.provider !== 'ollama'">
            <el-input v-model="llmForm.api_key" type="password" show-password placeholder="sk-..." />
          </el-form-item>
          <el-form-item label="Model">
            <el-input v-model="llmForm.model" placeholder="deepseek-r1:7b" />
          </el-form-item>
          <el-form-item label="启用">
            <el-switch v-model="llmForm.enabled" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveLLM">保存 LLM 配置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Email Config Card -->
      <el-card class="config-card">
        <template #header>
          <div class="card-header-row">
            <span class="card-title">📧 邮件配置</span>
            <el-button size="small" :loading="emailTesting" @click="testEmail">发送测试邮件</el-button>
          </div>
        </template>
        <el-form :model="emailForm" label-width="120px">
          <el-form-item label="SMTP 服务器">
            <el-input v-model="emailForm.smtp_host" placeholder="smtp.qq.com" />
          </el-form-item>
          <el-form-item label="SMTP 端口">
            <el-input-number v-model="emailForm.smtp_port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="发件邮箱">
            <el-input v-model="emailForm.sender_email" placeholder="your@qq.com" />
          </el-form-item>
          <el-form-item label="授权码">
            <el-input v-model="emailForm.auth_code" type="password" show-password placeholder="QQ邮箱16位授权码" />
          </el-form-item>
          <el-form-item label="启用">
            <el-switch v-model="emailForm.enabled" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveEmail">保存邮件配置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { settingsApi } from '@/api/settings'
import { emailApi } from '@/api/email'

const llmTesting = ref(false)
const emailTesting = ref(false)

const llmForm = reactive({
  provider: 'ollama',
  base_url: 'http://localhost:11434',
  api_key: '',
  model: 'deepseek-r1:7b',
  enabled: false,
})

const emailForm = reactive({
  smtp_host: 'smtp.qq.com',
  smtp_port: 465,
  sender_email: '',
  auth_code: '',
  enabled: false,
})

onMounted(async () => {
  try {
    const llm = await settingsApi.getLLMConfig()
    Object.assign(llmForm, { ...llm, api_key: '' })
  } catch { /* use defaults */ }

  try {
    const email = await emailApi.getConfig()
    Object.assign(emailForm, { ...email, auth_code: '' })
  } catch { /* use defaults */ }
})

async function saveLLM() {
  await settingsApi.updateLLMConfig({ ...llmForm, api_key: llmForm.api_key || undefined })
  ElMessage.success('LLM 配置已保存')
}

async function testLLM() {
  llmTesting.value = true
  try {
    const res = await settingsApi.testLLM()
    ElMessage({ type: res.code === 0 ? 'success' : 'error', message: res.message })
  } finally { llmTesting.value = false }
}

async function saveEmail() {
  await emailApi.updateConfig({ ...emailForm })
  ElMessage.success('邮件配置已保存')
}

async function testEmail() {
  emailTesting.value = true
  try {
    const res = await emailApi.test()
    ElMessage({ type: res.code === 0 ? 'success' : 'error', message: res.message })
  } finally { emailTesting.value = false }
}
</script>

<style scoped>
.settings-page { height: 100%; display: flex; flex-direction: column; }
.page-header {
  display: flex; align-items: center; padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
}
.page-header h2 { margin: 0; }
.settings-content {
  flex: 1; overflow-y: auto; padding: 24px;
  display: flex; flex-direction: column; gap: 24px; max-width: 800px;
}
.config-card { }
.card-header-row { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-size: 16px; font-weight: 600; }
</style>
