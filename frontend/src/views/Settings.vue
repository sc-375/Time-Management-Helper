<template>
  <div class="settings-page">
    <header class="page-header">
      <h2>设置</h2>
    </header>

    <div class="settings-content">
      <el-card class="config-card">
        <template #header>
          <div class="card-header-row">
            <span class="card-title">大模型配置</span>
            <div class="card-header-right">
              <span class="conn-dot" :class="{ connected: llmConnected }"></span>
              <el-button size="small" :loading="llmTesting" @click="testLLM">测试连接</el-button>
            </div>
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
            <el-input v-model="llmForm.api_key" type="password" show-password placeholder="sk-..." @input="llmKeyDirty = true" />
          </el-form-item>
          <el-form-item label="Model">
            <el-input v-model="llmForm.model" placeholder="deepseek-r1:7b" />
          </el-form-item>
          <el-form-item label="启用">
            <el-switch v-model="llmForm.enabled" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveLLM">保存配置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="config-card">
        <template #header>
          <div class="card-header-row">
            <span class="card-title">邮件提醒</span>
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
            <div style="display:flex;flex-direction:column;gap:4px;width:100%">
              <el-input v-model="emailForm.auth_code" type="password" show-password :placeholder="emailConfigured ? '已配置，留空不修改' : '请输入16位授权码'" @input="emailAuthDirty = true" />
              <span v-if="emailConfigured && !emailAuthDirty" style="font-size:11px;color:var(--priority-low)">&#10003; 已配置，无需重新输入</span>
            </div>
          </el-form-item>
          <el-form-item label="启用">
            <el-switch v-model="emailForm.enabled" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveEmail">保存配置</el-button>
          </el-form-item>
        </el-form>

        <el-collapse class="email-guide">
          <el-collapse-item title="如何获取 QQ 邮箱授权码？" name="1">
            <div class="guide-steps">
              <div class="step"><span class="step-num">1</span> 打开 <a href="https://mail.qq.com" target="_blank">mail.qq.com</a>，扫码或账号密码登录</div>
              <div class="step"><span class="step-num">2</span> 点击页面上方 <strong>设置</strong> → 切换到 <strong>帐户</strong> 标签</div>
              <div class="step"><span class="step-num">3</span> 向下滚动至 <strong>POP3/IMAP/SMTP 服务</strong> 区域</div>
              <div class="step"><span class="step-num">4</span> 点击 <strong>IMAP/SMTP 服务</strong> 后的 <strong>开启</strong> 按钮</div>
              <div class="step"><span class="step-num">5</span> 按弹窗提示发送短信验证 → 点击"我已发送"</div>
              <div class="step"><span class="step-num">6</span> 复制生成的 <strong>16 位授权码</strong>，填入上方「授权码」输入框</div>
            </div>
            <div class="guide-note">
              <span>📌 手机端如找不到 SMTP 选项，建议用 PC 浏览器操作。发件人即配置的 QQ 邮箱地址，会发送提醒给自己。每日上限约 100 封。授权码仅配置一次，自动加密存储。</span>
            </div>
          </el-collapse-item>
        </el-collapse>
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
const llmConnected = ref(false)
const emailAuthDirty = ref(false)
const llmKeyDirty = ref(false)
const emailConfigured = ref(false)

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
    const test = await settingsApi.testLLM()
    llmConnected.value = test.code === 0
  } catch { /* use defaults */ }

  try {
    const email = await emailApi.getConfig()
    emailConfigured.value = email.auth_code && email.auth_code.includes('****')
    Object.assign(emailForm, { ...email, auth_code: '' })
  } catch { /* use defaults */ }
})

async function saveLLM() {
  const payload: any = { ...llmForm }
  if (!llmKeyDirty.value) delete payload.api_key
  await settingsApi.updateLLMConfig(payload)
  llmKeyDirty.value = false
  ElMessage.success('LLM 配置已保存')
}

async function testLLM() {
  llmTesting.value = true
  try {
    const res = await settingsApi.testLLM()
    llmConnected.value = res.code === 0
    ElMessage({ type: res.code === 0 ? 'success' : 'error', message: res.message })
  } finally { llmTesting.value = false }
}

async function saveEmail() {
  const payload: any = { ...emailForm }
  if (!emailAuthDirty.value) delete payload.auth_code
  await emailApi.updateConfig(payload)
  emailAuthDirty.value = false
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
  display: flex; align-items: center; padding: 20px 28px;
  border-bottom: 1px solid var(--border);
}
.page-header h2 { margin: 0; font-size: 18px; font-weight: 600; color: var(--text-primary); }

.settings-content {
  flex: 1; overflow-y: auto; padding: 24px 28px;
  display: flex; flex-direction: column; gap: 20px; max-width: 760px;
}

.card-header-row { display: flex; justify-content: space-between; align-items: center; }
.card-header-right { display: flex; align-items: center; gap: 8px; }

.conn-dot {
  width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
  background: var(--priority-high);
}
.conn-dot.connected { background: var(--priority-low); }

.card-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }

.email-guide { margin-top: 16px; }
.email-guide :deep(.el-collapse-item__header) {
  font-size: 13px; color: var(--text-secondary); border: none;
}
.email-guide :deep(.el-collapse-item__wrap) {
  border: none; background: transparent;
}

.guide-section { margin-bottom: 12px; }
.guide-label {
  display: inline-block; font-size: 11px; font-weight: 600;
  color: var(--text-muted); text-transform: uppercase;
  letter-spacing: 0.5px; margin-bottom: 6px;
}

.guide-steps { display: flex; flex-direction: column; gap: 6px; padding: 4px 0 4px 4px; }
.step {
  display: flex; align-items: flex-start; gap: 10px;
  font-size: 13px; color: var(--text-primary); line-height: 1.6;
}
.step a { color: var(--accent); }
.step-num {
  width: 20px; height: 20px; border-radius: 50%;
  background: var(--bg-kanban-col); display: flex;
  align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; flex-shrink: 0;
  color: var(--text-secondary); margin-top: 1px;
}
.guide-note {
  margin-top: 12px; padding: 10px 12px; background: var(--bg-kanban-col);
  border-radius: var(--radius-sm); font-size: 12px; color: var(--text-secondary);
  line-height: 1.6;
}
</style>
