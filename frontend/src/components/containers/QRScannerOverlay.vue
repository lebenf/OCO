<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <Teleport to="body">
    <div class="qr-overlay" @click.self="$emit('close')">
      <div class="qr-card">
        <div class="qr-header">
          <span class="qr-title">{{ $t('transfer.qr_scan.title') }}</span>
          <button class="qr-close" @click="$emit('close')">✕</button>
        </div>
        <div class="qr-viewport">
          <video ref="videoEl" class="qr-video" autoplay playsinline muted />
          <canvas ref="canvasEl" class="qr-canvas" />
          <div class="qr-frame">
            <div class="qr-corner tl" /><div class="qr-corner tr" />
            <div class="qr-corner bl" /><div class="qr-corner br" />
          </div>
          <div v-if="error" class="qr-error">{{ error }}</div>
          <div v-if="scanning" class="qr-scanning-line" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import jsQR from 'jsqr'

const emit = defineEmits<{
  close: []
  scanned: [code: string]
}>()

const videoEl = ref<HTMLVideoElement | null>(null)
const canvasEl = ref<HTMLCanvasElement | null>(null)
const error = ref('')
const scanning = ref(false)
let stream: MediaStream | null = null
let rafId = 0

function extractCode(text: string): string {
  // QR format: {APP_HOST}/containers/{code}
  const match = text.match(/\/containers\/([A-Z0-9-]+)$/i)
  return match ? match[1].toUpperCase() : text.trim().toUpperCase()
}

function tick(): void {
  const video = videoEl.value
  const canvas = canvasEl.value
  if (!video || !canvas || video.readyState !== video.HAVE_ENOUGH_DATA) {
    rafId = requestAnimationFrame(tick)
    return
  }

  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')!
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const result = jsQR(imageData.data, imageData.width, imageData.height)

  if (result?.data) {
    const code = extractCode(result.data)
    stopCamera()
    emit('scanned', code)
    return
  }

  rafId = requestAnimationFrame(tick)
}

function stopCamera(): void {
  cancelAnimationFrame(rafId)
  stream?.getTracks().forEach(t => t.stop())
  stream = null
}

onMounted(async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
    if (videoEl.value) {
      videoEl.value.srcObject = stream
      scanning.value = true
      rafId = requestAnimationFrame(tick)
    }
  } catch {
    error.value = 'Camera non disponibile'
  }
})

onBeforeUnmount(() => stopCamera())
</script>

<style scoped>
.qr-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.7);
  display: flex; align-items: flex-end; justify-content: center;
  z-index: 500;
}
@media (min-width: 600px) {
  .qr-overlay { align-items: center; }
}

.qr-card {
  background: var(--oco-surface);
  border-radius: var(--oco-r-xl) var(--oco-r-xl) 0 0;
  width: 100%; max-width: 420px;
  padding: var(--oco-s-4);
  display: flex; flex-direction: column; gap: var(--oco-s-3);
}
@media (min-width: 600px) {
  .qr-card { border-radius: var(--oco-r-xl); }
}

.qr-header { display: flex; justify-content: space-between; align-items: center; }
.qr-title { font-size: 15px; font-weight: 600; }
.qr-close {
  width: 28px; height: 28px; border: none; background: var(--oco-surface-2);
  border-radius: 50%; color: var(--oco-ink-3); cursor: pointer; font-size: 12px;
  display: flex; align-items: center; justify-content: center;
}

.qr-viewport {
  position: relative; border-radius: var(--oco-r-lg); overflow: hidden;
  background: #000; aspect-ratio: 1;
}
.qr-video { width: 100%; height: 100%; object-fit: cover; display: block; }
.qr-canvas { display: none; }

.qr-frame { position: absolute; inset: 0; }
.qr-corner {
  position: absolute; width: 24px; height: 24px;
  border-color: white; border-style: solid; border-width: 0;
}
.qr-corner.tl { top: 16px; left: 16px; border-top-width: 3px; border-left-width: 3px; border-radius: 3px 0 0 0; }
.qr-corner.tr { top: 16px; right: 16px; border-top-width: 3px; border-right-width: 3px; border-radius: 0 3px 0 0; }
.qr-corner.bl { bottom: 16px; left: 16px; border-bottom-width: 3px; border-left-width: 3px; border-radius: 0 0 0 3px; }
.qr-corner.br { bottom: 16px; right: 16px; border-bottom-width: 3px; border-right-width: 3px; border-radius: 0 0 3px 0; }

.qr-scanning-line {
  position: absolute; left: 16px; right: 16px; height: 2px;
  background: rgba(255,255,255,0.6);
  animation: scan 2s ease-in-out infinite;
}
@keyframes scan {
  0%, 100% { top: 20%; }
  50% { top: 80%; }
}

.qr-error {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.6); color: white; font-size: 14px; text-align: center; padding: 16px;
}
</style>
