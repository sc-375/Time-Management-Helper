<template>
  <el-container class="app-container">
    <el-aside width="64px" class="app-sidebar">
      <div class="nav-items">
        <router-link to="/tasks" class="nav-item" :class="{ active: $route.path.startsWith('/tasks') }">
          <el-icon :size="22"><List /></el-icon>
          <span class="nav-label">任务</span>
        </router-link>
        <router-link to="/calendar" class="nav-item" :class="{ active: $route.path === '/calendar' }">
          <el-icon :size="22"><Calendar /></el-icon>
          <span class="nav-label">日历</span>
        </router-link>
        <router-link to="/ai-chat" class="nav-item" :class="{ active: $route.path === '/ai-chat' }">
          <el-icon :size="22"><ChatDotRound /></el-icon>
          <span class="nav-label">AI</span>
        </router-link>
        <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
          <el-icon :size="22"><Setting /></el-icon>
          <span class="nav-label">设置</span>
        </router-link>
      </div>
    </el-aside>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { List, Calendar, ChatDotRound, Setting } from '@element-plus/icons-vue'
</script>

<style>
body { margin: 0; }
#app { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }
</style>

<style scoped>
.app-container { height: 100vh; }
.app-sidebar {
  background: #2c2c2c; display: flex; flex-direction: column;
  align-items: center; padding-top: 16px;
}
.nav-items { display: flex; flex-direction: column; gap: 8px; }
.nav-item {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 10px 0; width: 64px; color: #999; text-decoration: none;
  border-radius: 8px; transition: background 0.2s;
}
.nav-item:hover { background: #3a3a3a; color: #fff; }
.nav-item.active { color: #409eff; background: #3a3a3a; }
.nav-label { font-size: 10px; }
.app-main { padding: 0; overflow: hidden; }
</style>
