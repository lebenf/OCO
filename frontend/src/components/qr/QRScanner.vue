<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <Teleport to="body">
    <div class="qr-overlay">
      <div class="qr-topbar">
        <button class="qr-close" @click="$emit('close')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="20" height="20">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        <span class="qr-title">{{ $t('search.qr_scan') }}</span>
        <div style="width:36px"></div>
      </div>

      <div class="qr-viewport">
        <video ref="videoRef" autoplay playsinline muted class="qr-video"></video>
        <canvas ref="canvasRef" hidden></canvas>

        <!-- Corner frame -->
        <div class="qr-frame">
          <span class="corner tl"></span>
          <span class="corner tr"></span>
          <span class="corner bl"></span>
          <span class="corner br"></span>
          <div class="scan-line" :class="{ active: scanning }"></div>
        </div>

        <div v-if="error" class="qr-error">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ error }}
        </div>
      </div>

      <p class="qr-hint">{{ $t('search.qr_hint') }}</p>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import jsQR from 'jsqr'

const emit = defineEmits<{
  close: []
  scanned: [data: string]
}>()

const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const scanning = ref(false)
const error = ref('')
let stream: MediaStream | null = null
let animFrame: number | null = null

onMounted(async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      videoRef.value.addEventListener('loadedmetadata', () => {
        scanning.value = true
        scanLoop()
      })
    }
  } catch {
    error.value = 'Camera access denied'
  }
})

onUnmounted(stop)

function stop(): void {
  scanning.value = false
  if (animFrame !== null) { cancelAnimationFrame(animFrame); animFrame = null }
  if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null }
}

function scanLoop(): void {
  const video = videoRef.value
  const canvas = canvasRef.value
  if (!video || !canvas || !scanning.value) return

  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.drawImage(video, 0, 0)
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const code = jsQR(imageData.data, imageData.width, imageData.height)
      if (code?.data) {
        stop()
        emit('scanned', code.data)
        return
      }
    }
  }
  animFrame = requestAnimationFrame(scanLoop)
}
</script>

<style scoped>
.qr-overlay {
  position: fixed;
  inset: 0;
  background: #000;
  z-index: 500;
  display: flex;
  flex-direction: column;
  padding-top: max(env(safe-area-inset-top), 0px);
  padding-bottom: max(env(safe-area-inset-bottom), 0px);
}

.qr-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  color: white;
}

.qr-close {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255,255,255,0.15);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.qr-close:hover { background: rgba(255,255,255,0.25); }

.qr-title {
  font-size: 15px;
  font-weight: 600;
  color: white;
  font-family: var(--oco-font-sans);
}

.qr-viewport {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.qr-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Corner frame overlay */
.qr-frame {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.corner {
  position: absolute;
  width: 36px;
  height: 36px;
  border-color: white;
  border-style: solid;
  border-radius: 2px;
  opacity: 0.9;
}
.corner.tl { top: calc(50% - 100px); left: calc(50% - 100px); border-width: 3px 0 0 3px; }
.corner.tr { top: calc(50% - 100px); right: calc(50% - 100px); border-width: 3px 3px 0 0; }
.corner.bl { bottom: calc(50% - 100px); left: calc(50% - 100px); border-width: 0 0 3px 3px; }
.corner.br { bottom: calc(50% - 100px); right: calc(50% - 100px); border-width: 0 3px 3px 0; }

/* Scan line */
.scan-line {
  position: absolute;
  left: calc(50% - 100px);
  width: 200px;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, var(--oco-primary) 30%, var(--oco-primary) 70%, transparent 100%);
  top: calc(50% - 100px);
  opacity: 0;
}
.scan-line.active {
  opacity: 1;
  animation: scan-sweep 1.8s ease-in-out infinite;
}
@keyframes scan-sweep {
  0%   { top: calc(50% - 100px); }
  50%  { top: calc(50% + 98px); }
  100% { top: calc(50% - 100px); }
}

.qr-error {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(220, 50, 50, 0.9);
  color: white;
  font-size: 13px;
  padding: 10px 16px;
  border-radius: var(--oco-r-lg);
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  font-family: var(--oco-font-sans);
}

.qr-hint {
  text-align: center;
  color: rgba(255,255,255,0.55);
  font-size: 13px;
  padding: 16px;
  font-family: var(--oco-font-sans);
  margin: 0;
}
</style>
