import _ from 'lodash'
import axios from 'axios'
import ga from '@/ga'
import moment from 'moment-timezone'
import store from '@/store'
import utils from '@/api/api-utils'

const $_track = action => ga.curated(action)

const $_onCreate = (group: any) => {
  store.commit('context/addMyCuratedGroup', group)
  store.commit('context/broadcast', 'my-curated-groups-updated', group.domain)
  $_track('create')
}

const $_onDelete = (domain: string, curatedGroupId: number) => {
  store.commit('context/removeMyCuratedGroup', curatedGroupId)
  store.commit('context/broadcast', {eventType: 'my-curated-groups-updated', data: domain})
  $_track('delete')
}

const $_onUpdate = (curatedGroup: any) => {
  store.commit('context/updateMyCuratedGroup', curatedGroup)
  store.commit('context/broadcast', {eventType: 'my-curated-groups-updated', data: curatedGroup.domain})
  $_track('update')
}

export function addStudentsToCuratedGroup(curatedGroupId: number, sids: string[], returnStudentProfiles?: boolean) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/students/add`, {
      curatedGroupId: curatedGroupId,
      sids: sids,
      returnStudentProfiles: returnStudentProfiles
    })
    .then(response => {
      const group = response.data
      $_onUpdate(group)
      return group
    })
}

export function createCuratedGroup(domain: string, name: string, sids: string[]) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/create`, {domain, name, sids})
    .then(function(response) {
      const group = response.data
      $_onCreate(group)
      return group
    })
}

export function deleteCuratedGroup(domain: string, curatedGroupId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/curated_group/delete/${curatedGroupId}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(() => {
      $_onDelete(domain, curatedGroupId)
      $_track('delete')
    })
    .catch(error => error)
}

export function downloadCuratedGroupCsv(curatedGroupId: number, name: string, csvColumnsSelected: any[]) {
  $_track('download')
  const fileDownload = require('js-file-download')
  const now = moment().format('YYYY-MM-DD_HH-mm-ss')
  const termId = store.getters['context/currentUser'].preferences.termId || store.getters['context/config'].currentEnrollmentTermId
  const url = `${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}/download_csv`
  return axios.post(url, {csvColumnsSelected, termId})
    .then(response => fileDownload(response.data, `${name}-students-${now}.csv`), () => null)
}

export function getCuratedGroup(
  curatedGroupId: number,
  limit: number,
  offset: number,
  orderBy: string,
  termId: string
) {
  $_track('view')
  const url = `${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}?orderBy=${orderBy}&termId=${termId}&offset=${offset}&limit${limit}`
  return axios.get(url).then(response => response.data, () => null)
}

export function getUsersWithCuratedGroups() {
  return axios.get(`${utils.apiBaseUrl()}/api/curated_groups/all`).then(response => response.data, () => null)
}

export function removeFromCuratedGroup(curatedGroupId: number, sid: any) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}/remove_student/${sid}`)
    .then(response => {
      const group = response.data
      $_onUpdate(group)
      if (group.students) {
        group.students = _.remove(group.students, student => sid === (student.sid || student.csEmplId))
      }
      return group
    })
}

export function renameCuratedGroup(curatedGroupId: number, name: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/curated_group/rename`, {id: curatedGroupId, name})
    .then(response => {
      const group = response.data
      $_onUpdate(group)
      return group
    })
    .catch(error => error)
}

export function getStudentsWithAlerts(curatedGroupId: number) {
  const url = `${utils.apiBaseUrl()}/api/curated_group/${curatedGroupId}/students_with_alerts`
  return axios.get(url).then(response => response.data, () => null)
}
