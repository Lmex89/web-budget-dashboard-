<script setup lang="ts">
import Sidebar from '@/components/layout/Sidebar.vue'
import MobileHeader from '@/components/layout/MobileHeader.vue'
import BottomNav from '@/components/layout/BottomNav.vue'
</script>

<template>
  <div class="lg:flex min-h-screen bg-paper">
    <Sidebar />

    <div class="flex-1 min-w-0">
      <MobileHeader />
      <main class="px-5 lg:px-10 pt-6 lg:pt-10 pb-28 lg:pb-10 max-w-6xl mx-auto">
        <router-view />
      </main>
    </div>

    <BottomNav />
  </div>
</template>
