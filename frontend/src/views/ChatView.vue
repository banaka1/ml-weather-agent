<template>
  <ChatLayout />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import ChatLayout from '@/layouts/ChatLayout.vue'

const sessionStore = useSessionStore()

onMounted(() => {
  sessionStore.fetchSessions()
})
</script>
