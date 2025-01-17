<template>
  <div v-if="!loading" class="default-margins">
    <div class="mb-6">
      <h1 id="page-header">Everyone's Groups</h1>
      <div v-if="find(flatten(map(rows, 'groups')), g => g.domain === 'admitted_students')" class="pl-1">
        <v-icon class="mr-1 vertical-bottom" color="warning" :icon="mdiStar" />
        <span class="sr-only">Star icon</span>denotes a group of admitted students.
      </div>
    </div>
    <div v-if="isEmpty(rows)">
      <div>There are no saved groups</div>
    </div>
    <div v-for="(row, index) in rows" :key="index" class="mt-4">
      <h2 :id="`groups-list-${index}-heading`" class="page-section-header-sub">
        <span class="sr-only">Curated Groups of</span>
        <span v-if="row.user.name">{{ row.user.name }}</span>
        <span v-if="!row.user.name">UID: {{ row.user.uid }}</span>
      </h2>
      <ul :aria-labelledby="`groups-list-${index}-heading`">
        <li v-for="group in row.groups" :key="group.id" class="ml-8">
          <span v-if="group.domain === 'admitted_students'" class="mr-1">
            <v-icon class="vertical-bottom" color="warning" :icon="mdiStar" />
            <span class="sr-only">Star: Admitted Students group</span>
          </span>
          <router-link :to="`/curated/${group.id}`">{{ group.name }}</router-link> ({{ group.totalStudentCount }}<span class="sr-only">students</span>)
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted} from 'vue'
import {filter, find, flatten, isEmpty, map, size} from 'lodash'
import {getUsersWithCuratedGroups} from '@/api/curated'
import {mdiStar} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const loading = computed(() => contextStore.loading)
let rows

contextStore.loadingStart()

onMounted(() => {getUsersWithCuratedGroups().then(data => {
  rows = filter(data, row => size(row.groups))
  contextStore.loadingComplete('Everyone\'s Groups has loaded')
})})
</script>
