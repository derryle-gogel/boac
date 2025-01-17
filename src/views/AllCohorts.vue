<template>
  <div v-if="!loading" class="default-margins">
    <div class="mb-6">
      <h1 id="page-header">Everyone's Cohorts</h1>
      <div v-if="includesAdmittedStudents" class="pl-1">
        <v-icon class="mr-1 vertical-bottom" color="warning" :icon="mdiStar" />
        <span class="sr-only">Star icon</span>denotes a cohort of admitted students.
      </div>
    </div>
    <div v-if="!rows.length">
      <div>There are no saved cohorts</div>
    </div>
    <div v-for="(row, index) in rows" :key="index" class="mt-4">
      <h2 :id="`cohorts-list-${index}-heading`" class="page-section-header-sub">
        <span class="sr-only">Cohorts of</span>
        <span v-if="row.user.name">{{ row.user.name }}</span>
        <span v-if="!row.user.name">UID: {{ row.user.uid }}</span>
      </h2>
      <ul :aria-labelledby="`cohorts-list-${index}-heading`">
        <li v-for="cohort in row.cohorts" :key="cohort.id" class="ml-8">
          <span v-if="cohort.domain === 'admitted_students'" class="mr-1">
            <v-icon class="vertical-bottom" color="warning" :icon="mdiStar" />
            <span class="sr-only">Star: Admitted Students cohort</span>
          </span>
          <router-link :to="`/cohort/${cohort.id}`">{{ cohort.name }}</router-link> ({{ cohort.totalStudentCount }}<span class="sr-only">students</span>)
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted} from 'vue'
import {filter as _filter, find, flatten, map} from 'lodash'
import {getUsersWithCohorts} from '@/api/cohort'
import {mdiStar} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const loading = computed(() => contextStore.loading)
let includesAdmittedStudents = undefined
let rows = []

contextStore.loadingStart()

onMounted(() => {
  getUsersWithCohorts().then(data => {
    rows = _filter(data, row => row.cohorts.length)
    includesAdmittedStudents = find(flatten(map(rows, 'cohorts')), g => g.domain === 'admitted_students')
    contextStore.loadingComplete('Everyone\'s Cohorts loaded')
  })
})
</script>
