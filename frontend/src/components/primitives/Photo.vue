<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="photo-wrap" :style="{ aspectRatio: ratio }">
    <img v-if="src" :src="src" :alt="alt" class="photo-img" />
    <div v-else class="photo-placeholder">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.35">
        <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
        <polyline points="21 15 16 10 5 21"/>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ src?: string | null; alt?: string; ratio?: string }>(), {
  alt: '',
  ratio: '4/3',
})
</script>

<style scoped>
.photo-wrap {
  overflow: hidden;
  border-radius: var(--oco-r-md);
  background: var(--oco-surface-3);
}
.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  /* diagonal stripe pattern */
  background-image: repeating-linear-gradient(
    -45deg,
    transparent,
    transparent 6px,
    var(--oco-line) 6px,
    var(--oco-line) 7px
  );
  color: var(--oco-ink-4);
}
</style>
