<template>
  <div class="light-bar" :class="timePhase"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const timePhase = computed(() => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 9) return 'dawn'     // 清晨
  if (hour >= 9 && hour < 14) return 'morning'   // 上午
  if (hour >= 14 && hour < 18) return 'afternoon' // 下午
  if (hour >= 18 && hour < 21) return 'dusk'      // 黄昏
  return 'night'                                   // 深夜
})
</script>

<style scoped>
.light-bar {
  height: 3px;
  width: 100%;
  flex-shrink: 0;
  transition: background 3s ease;
  border-radius: 0 0 2px 0;
}
.light-bar.dawn {
  background: linear-gradient(to right, #E8A95B, #F4CD89, #E8A95B);
}
.light-bar.morning {
  background: linear-gradient(to right, #93B8F5, #C4D9FA, #93B8F5);
}
.light-bar.afternoon {
  background: linear-gradient(to right, #6BA3EC, #93B8F5, #6BA3EC);
}
.light-bar.dusk {
  background: linear-gradient(to right, #E8956F, #F4B89E, #E8956F);
}
.light-bar.night {
  background: linear-gradient(to right, #4F6EF7, #8B9EF9, #4F6EF7);
}
</style>
