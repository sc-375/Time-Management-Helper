<template>
  <el-container class="app-container">
    <nav class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-dot"></span>
      </div>
      <div class="nav-items">
        <router-link to="/tasks" class="nav-item" :class="{ active: $route.path.startsWith('/tasks') }">
          <div class="nav-icon-box">
            <el-icon :size="20"><List /></el-icon>
          </div>
          <span class="nav-label">任务</span>
        </router-link>
        <router-link to="/calendar" class="nav-item" :class="{ active: $route.path === '/calendar' }">
          <div class="nav-icon-box">
            <el-icon :size="20"><Calendar /></el-icon>
          </div>
          <span class="nav-label">日历</span>
        </router-link>
        <router-link to="/ai-chat" class="nav-item" :class="{ active: $route.path === '/ai-chat' }">
          <div class="nav-icon-box">
            <el-icon :size="20"><ChatDotRound /></el-icon>
          </div>
          <span class="nav-label">AI</span>
        </router-link>
        <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
          <div class="nav-icon-box">
            <el-icon :size="20"><Setting /></el-icon>
          </div>
          <span class="nav-label">设置</span>
        </router-link>
      </div>
    </nav>
    <main class="main-area">
      <TimeLightBar />
      <div class="main-content">
        <router-view />
      </div>
    </main>
  </el-container>
</template>

<script setup lang="ts">
import { List, Calendar, ChatDotRound, Setting } from '@element-plus/icons-vue'
import TimeLightBar from '@/components/TimeLightBar.vue'
</script>

<style scoped>
.app-container {
  height: 100vh;
  background: var(--bg-root);
}

.sidebar {
  width: 68px;
  background: var(--bg-sidebar);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 20px;
  flex-shrink: 0;
  gap: 4px;
  user-select: none;
}

.sidebar-brand {
  width: 36px;
  height: 36px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 10px;
}
.brand-dot {
  width: 8px;
  height: 8px;
  border-radius: 8px;
  background: var(--accent);
  box-shadow: 0 0 8px rgba(79, 110, 247, 0.5);
}

.nav-items {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  width: 52px;
  padding: 10px 0;
  color: var(--text-on-sidebar);
  text-decoration: none;
  border-radius: 10px;
  transition: all 0.2s ease;
  font-size: 10px;
  letter-spacing: 0.3px;
}
.nav-icon-box {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
}
.nav-item:hover {
  color: var(--text-on-sidebar-active);
}
.nav-item:hover .nav-icon-box {
  background: var(--bg-sidebar-hover);
  transform: scale(1.08);
}
.nav-item.active .nav-icon-box {
  background: var(--accent);
  color: #fff;
}
.nav-item.active {
  color: var(--text-on-sidebar-active);
}
.nav-label {
  font-weight: 500;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.main-content {
  flex: 1;
  overflow: hidden;
}
</style>
