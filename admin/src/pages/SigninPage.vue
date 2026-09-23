<template>
  <q-layout>
    <q-page-container>
      <q-page class="flex flex-center auth-page">
        <div class="background-container">
          <img src="/admin/PATTERN-VIOLET.svg" aria-hidden="true" class="background-pattern" />
          <div aria-hidden="true" class="background-dots"></div>
        </div>
        <q-card :style="$q.screen.lt.sm ? { width: '80%' } : { width: '400px' }">
          <q-card-actions class="flex justify-center q-mt-xl q-ml-xl q-mr-xl q-mb-xs">
            <img src="/admin/LOGO-VIOLET.svg" height="50px" />
          </q-card-actions>
          <q-card-actions class="flex justify-center q-mx-lg q-my-lg q-pa-none">
            <q-btn
              flat
              :label="t('signup')"
              :disable="!authStore.initialized"
              color="primary"
              to="/signup"
            />
            <q-space />
            <q-btn
              outline
              :label="t('signin')"
              :disable="!authStore.initialized"
              :loading="!authStore.initialized"
              color="primary"
              @click="onLogin"
            />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { notifyError } from '@/utils/notify'

const $q = useQuasar()
const { t } = useI18n()
const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
  await authStore.init()
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})

async function onLogin() {
  try {
    await authStore.login()
  } catch (error) {
    notifyError(error)
    return
  }
}
</script>

<style scoped lang="scss">
.q-card {
  background-color: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
}

.background-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;

  pointer-events: none;
  z-index: -1;
}

.background-pattern {
  position: absolute;

  top: -10rem;
  left: 15rem;
  width: 100rem;
  height: 200rem;

  object-fit: contain;
  rotate: -40deg;

  opacity: 0.05;
}

// Dot grid, same as the main layout: 3px dots on a 30px pitch, dissolving
// towards the left and right sides via a mask -- no image asset needed.
.background-dots {
  --dot-color: #{$brand-purple-200};
  --dot-fade: linear-gradient(90deg, transparent 0%, #000 45%, #000 55%, transparent 100%);

  position: absolute;
  inset: 0;

  background-image: radial-gradient(circle, var(--dot-color) 1.5px, transparent 1.5px);
  background-size: 30px 30px;
  opacity: 0.25;

  mask-image: var(--dot-fade);
  -webkit-mask-image: var(--dot-fade);
}

.body--dark .background-dots {
  --dot-color: #{$brand-purple-100};
}
</style>
