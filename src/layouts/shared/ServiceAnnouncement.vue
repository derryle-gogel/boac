<template>
  <h2 v-if="announcement && announcement.isPublished" id="service-announcement-label" class="sr-only">BOA Service Alert</h2>
  <div
    v-if="announcement && announcement.isPublished"
    ref="serviceAlert"
    aria-labelledby="service-announcement-label"
  >
    <v-expand-transition>
      <div v-if="!dismissedServiceAnnouncement" class="align-center bg-service-announcement d-flex font-weight-medium py-4 px-6">
        <div aria-live="polite" role="alert" class="d-inline-block pr-1 service-announcement-container w-100">
          <span
            id="service-announcement-banner"
            v-html="announcement.text"
          />
        </div>
        <v-btn
          id="dismiss-service-announcement"
          color="transparent"
          elevation="0"
          :icon="mdiClose"
          size="x-small"
          title="Dismiss BOA Service Alert"
          @click="toggle"
        />
      </div>
    </v-expand-transition>
    <v-btn
      v-if="dismissedServiceAnnouncement"
      id="restore-service-announcement"
      class="sr-only"
      @click="toggle"
    >
      Restore BOA Service Alert
    </v-btn>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {mdiClose} from '@mdi/js'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useTemplateRef} from 'vue'

const contextStore = useContextStore()
const {announcement, dismissedServiceAnnouncement} = storeToRefs(contextStore)
const serviceAlertRef = useTemplateRef('serviceAlert')

defineExpose({ref: serviceAlertRef})

const toggle = () => {
  if (dismissedServiceAnnouncement.value) {
    contextStore.restoreServiceAnnouncement()
    alertScreenReader('Alert restored')
    putFocusNextTick('dismiss-service-announcement', {scroll: false})
  } else {
    contextStore.dismissServiceAnnouncement()
    alertScreenReader('Dismissed')
    putFocusNextTick('restore-service-announcement', {scroll: false})
  }
}
</script>

<style>
#service-announcement-banner li {
  padding-right: 20px;
  overflow-wrap: break-word;
}
#service-announcement-banner ol {
  margin-left: 30px;
}
#service-announcement-banner p {
  padding-right: 20px;
  overflow-wrap: break-word;
}
#service-announcement-banner ul {
  margin-left: 30px;
}
</style>

<style scoped>
.service-announcement-container {
  width: 98% !important;
}
</style>
