<script setup lang="ts">
import Sidebar from '@/components/layout/Sidebar.vue'
import Navbar from '@/components/layout/Navbar.vue'
</script>

<template>
  <div class="drawer lg:drawer-open">
    <input id="drawer" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content flex flex-col">
      <Navbar />
      <main class="flex-1 p-4 lg:p-6 bg-base-200 min-h-screen">
        <router-view />
      </main>
    </div>
    <Sidebar />
  </div>
</template>
