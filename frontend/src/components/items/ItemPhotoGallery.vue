<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="gallery">
    <div v-if="photos.length === 0" class="empty-gallery">{{ $t('item.gallery.empty') }}</div>
    <div v-else class="photos">
      <div
        v-for="(photo, i) in photos"
        :key="photo.id"
        class="thumb"
        :class="{ active: currentIndex === i }"
        @click="currentIndex = i"
      >
        <img :src="photo.url" :alt="`photo ${i + 1}`" />
      </div>
    </div>
    <div v-if="photos.length > 0" class="main-photo">
      <img :src="photos[currentIndex].url" :alt="`photo ${currentIndex + 1}`" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ItemPhotoOut } from '@/stores/items'

defineProps<{ photos: ItemPhotoOut[] }>()
const currentIndex = ref(0)
</script>

<style scoped>
.gallery { display: flex; flex-direction: column; gap: 0.5rem; }
.photos { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.thumb { width: 50px; height: 50px; cursor: pointer; border: 2px solid transparent; border-radius: 4px; overflow: hidden; }
.thumb.active { border-color: #4a90e2; }
.thumb img { width: 100%; height: 100%; object-fit: cover; }
.main-photo img { width: 100%; max-height: 300px; object-fit: contain; border-radius: 8px; background: #f4f6f9; }
.empty-gallery { color: #aaa; font-size: 0.875rem; text-align: center; padding: 1rem; }
</style>
