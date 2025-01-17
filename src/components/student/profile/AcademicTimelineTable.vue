<template>
  <div v-if="isExpandAllAvailable" class="align-center d-flex flex-wrap font-size-14">
    <h3 class="sr-only">Quick Links</h3>
    <div class="pl-2 pb-2">
      <v-btn
        :id="`toggle-expand-all-${selectedFilter}s`"
        class="px-1"
        color="primary"
        density="compact"
        :disabled="!messagesVisible.length"
        variant="text"
        @click.prevent="toggleExpandAll"
      >
        <v-icon :icon="allExpanded ? mdiMenuDown : mdiMenuRight" />
        <span class="text-no-wrap">{{ allExpanded ? 'Collapse' : 'Expand' }} all {{ selectedFilter }}s</span>
      </v-btn>
    </div>
    <div v-if="showDownloadNotesLink" class="pl-3 pb-2" role="separator">|</div>
    <div v-if="showDownloadNotesLink" class="pl-3 pb-2">
      <a id="download-notes-link" :href="`${config.apiBaseUrl}/api/notes/${student.sid}/download?type=${selectedFilter}`">Download {{ selectedFilter }}s</a>
    </div>
    <div class="pl-3 pb-2" role="separator">|</div>
    <div class="align-center d-flex pl-3 pb-2">
      <label
        :id="`timeline-${selectedFilter}s-query-label`"
        :for="`timeline-${selectedFilter}s-query-input`"
        class="font-weight-bold mb-0 mr-1 text-no-wrap v-btn--variant-plain"
      >
        Search {{ selectedFilter === 'eForm' ? 'eForm' : capitalize(selectedFilter) }}s:
      </label>
      <v-text-field
        :id="`timeline-${selectedFilter}s-query-input`"
        v-model="timelineQuery"
        bg-color="pale-blue"
        class="academic-timeline-search-input"
        color="primary"
        flat
        hide-details
        type="search"
      />
    </div>
    <div v-if="showMyNotesToggle" class="pl-3 pb-2" role="separator">|</div>
    <div v-if="showMyNotesToggle" class="pl-3 pb-2">
      <div class="align-center d-flex font-weight-bold">
        <label for="toggle-my-notes-button" class="mr-3" :class="showMyNotesOnly ? 'text-medium-emphasis' : 'text-primary'">
          <span class="sr-only">Show </span>All {{ selectedFilter }}s
        </label>
        <div class="mr-3">
          <v-switch
            id="toggle-my-notes-button"
            v-model="showMyNotesOnly"
            aria-label="Show Only My Notes"
            density="compact"
            color="primary"
            hide-details
            role="switch"
          />
        </div>
        <label for="toggle-my-notes-button" :class="showMyNotesOnly ? 'text-primary' : 'text-medium-emphasis'">
          <span class="sr-only">Show only </span>My {{ selectedFilter }}s
        </label>
        <span aria-live="polite" class="sr-only">Showing {{ showMyNotesOnly ? 'only my notes' : 'all notes' }}</span>
      </div>
    </div>
  </div>
  <div
    v-if="!searchResults && !messagesVisible.length"
    id="zero-messages"
    aria-live="polite"
    class="font-size-16 font-weight-bold ml-6 my-4 text-medium-emphasis"
  >
    <span v-if="selectedFilter && showMyNotesOnly">No {{ filterTypes[selectedFilter].name.toLowerCase() }}s authored by you.</span>
    <span v-if="selectedFilter && !showMyNotesOnly">No {{ filterTypes[selectedFilter].name.toLowerCase() }}s</span>
    <span v-if="!selectedFilter">None</span>
  </div>
  <div v-if="searchResults" class="ml-3 my-2">
    <h3 id="search-results-header" class="messages-none">
      {{ pluralize(`advising ${selectedFilter}`, searchResults.length) }} for&nbsp;
      <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span>
      with '{{ timelineQuery }}'
    </h3>
  </div>
  <div v-if="countPerActiveTab">
    <table
      id="timeline-messages"
      :aria-rowcount="size(messages)"
      class="w-100"
    >
      <caption class="sr-only">Academic Timeline: {{ activeTab === 'all' ? 'All Messages' : `${capitalize(activeTab)}s` }}</caption>
      <colgroup>
        <col class="column-pill" />
        <col class="column-message" />
        <col class="column-details" />
        <col class="column-date" />
      </colgroup>
      <thead>
        <tr class="sr-only">
          <th>Type</th>
          <th>Summary</th>
          <th>Details</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="creatingNoteEvent" class="message-row-read message-row border-t-sm border-b-sm">
          <td class="column-pill">
            <v-chip
              :id="`timeline-tab-${activeTab}-pill-creating-note`"
              class="border pill-note font-weight-medium font-size-12 justify-center text-uppercase ma-2 px-1"
              color="category-note"
              density="compact"
              label
              variant="flat"
            >
              <span class="sr-only">Creating new</span> advising note
            </v-chip>
          </td>
          <td class="column-message">
            <div class="d-flex px-2">
              <div class="pr-2">
                <v-progress-circular indeterminate size="16" width="2" />
              </div>
              <div class="text-medium-emphasis">
                {{ creatingNoteEvent.subject }}
              </div>
            </div>
          </td>
          <td class="column-details"></td>
          <td class="column-date">
            <div class="pr-2 float-right text-no-wrap text-medium-emphasis">
              <TimelineDate
                :date="new Date()"
                :include-time-of-day="false"
              />
            </div>
          </td>
        </tr>
        <template v-for="(message, index) in messagesVisible" :key="index">
          <tr
            :id="`permalink-${message.type}-${message.id}`"
            :aria-labelledby="getRowAriaLabelledBy(message, index)"
            :aria-rowindex="index + 1"
            :class="{'message-row-read': message.read}"
            class="message-row border-t-sm border-b-sm"
            role="region"
          >
            <td class="column-pill">
              <v-chip
                :id="`timeline-tab-${activeTab}-pill-${message.type}-${message.id}`"
                :aria-label="filterTypes[message.type].name"
                class="border font-weight-medium font-size-12 justify-center text-uppercase ma-2 px-1"
                :class="isExpanded(message) ? `pill-${message.type} mt-3` : `pill-${message.type}`"
                :color="`category-${message.type}`"
                density="compact"
                label
                variant="flat"
              >
                {{ filterTypes[message.type].name }}
              </v-chip>
              <div
                v-if="isEditable(message) && !editModeNoteId && isExpanded(message)"
                class="d-flex flex-column note-actions px-2"
              >
                <v-btn
                  v-if="userCanEdit(message)"
                  :id="`edit-note-${message.id}-button`"
                  :aria-label="`Edit ${getButtonAriaLabel(message)}`"
                  class="mx-auto my-1"
                  color="primary"
                  density="compact"
                  :disabled="noteStore.disableNewNoteButton"
                  slim
                  :text="`Edit ${message.isDraft ? 'Draft' : 'Note'}`"
                  variant="text"
                  @click.stop="editNote(message)"
                />
                <v-btn
                  v-if="userCanDelete(message)"
                  :id="`delete-note-button-${message.id}`"
                  :aria-label="`Delete ${getButtonAriaLabel(message)}`"
                  class="mx-auto my-1"
                  color="primary"
                  density="compact"
                  :disabled="noteStore.disableNewNoteButton"
                  slim
                  :text="`Delete ${message.isDraft ? 'Draft' : 'Note'}`"
                  variant="text"
                  @click.stop="onClickDeleteNote(message)"
                />
              </div>
            </td>
            <td
              :class="{'font-weight-bold': !message.read, 'vertical-top': isExpanded(message)}"
              class="column-message"
            >
              <div class="d-flex flex-column-reverse">
                <template v-if="message.type === 'requirement'">
                  <div
                    :id="`timeline-tab-${activeTab}-message-${message.type}-${message.id}`"
                    class="d-flex flex-no-wrap"
                    tabindex="0"
                  >
                    <v-icon
                      v-if="message.status === 'Satisfied'"
                      :icon="mdiCheckBold"
                      class="requirements-icon"
                      color="success"
                    />
                    <v-icon
                      v-if="message.status === 'Not Satisfied'"
                      :icon="mdiExclamationThick"
                      class="requirements-icon"
                      color="warning"
                    />
                    <v-icon
                      v-if="message.status === 'In Progress'"
                      :icon="mdiClockOutline"
                      class="requirements-icon"
                      color="secondary"
                    />
                    <span :id="`${message.type}-${message.id}-is-closed`" class="truncate-with-ellipsis">
                      <span class="sr-only">{{ message.status }}: {{ message.name }}</span>
                      <span :aria-hidden="true">{{ message.message }}</span>
                    </span>
                  </div>
                </template>
                <template v-else>
                  <div
                    :id="`timeline-tab-${activeTab}-message-${message.type}-${message.id}`"
                    :aria-controls="'requirement' === message.type ? undefined : `${message.type}-${message.id}-outer`"
                    :aria-expanded="'requirement' === message.type ? undefined : isExpanded(message)"
                    :aria-label="'requirement' === message.type ? undefined : `Expand ${getButtonAriaLabel(message)}`"
                    class="pl-2"
                    :class="{
                      'message-open': isExpanded(message),
                      'img-blur': currentUser.inDemoMode && ['appointment', 'eForm', 'note'].includes(message.type)
                    }"
                    :role="'requirement' === message.type || isExpanded(message) ? undefined : 'button'"
                    :tabindex="0"
                    @keyup.enter="onClickOpenMessage(message)"
                    @click="onClickOpenMessage(message)"
                  >
                    <span :id="`${message.type}-${message.id}-message`" class="d-flex align-center w-100">
                      <span
                        v-if="!includes(['appointment', 'eForm', 'note'] , message.type)"
                        :id="`${message.type}-${message.id}-is-closed`"
                        :class="{
                          'mb-5': isExpanded(message),
                          'truncate-with-ellipsis': !isExpanded(message)
                        }"
                      >
                        {{ getMessageSummary(message) }}
                      </span>
                      <AdvisingNote
                        v-if="['eForm', 'note'].includes(message.type) && message.id !== editModeNoteId"
                        :after-saved="afterEditAdvisingNote"
                        :delete-note="onClickDeleteNote"
                        :edit-note="editNote"
                        :is-open="isExpanded(message)"
                        :message-summary="getMessageSummary(message)"
                        :note="message"
                      />
                      <EditAdvisingNote
                        v-if="['eForm', 'note'].includes(message.type) && message.id === editModeNoteId"
                        :after-cancel="afterNoteEditCancel"
                        :after-saved="afterEditAdvisingNote"
                        class="pt-2"
                        :note-id="message.id"
                      />
                      <AdvisingAppointment
                        v-if="message.type === 'appointment'"
                        :appointment="message"
                        :is-open="isExpanded(message)"
                        :message-summary="getMessageSummary(message)"
                        :student="student"
                      />
                    </span>
                  </div>
                  <span v-if="'requirement' !== message.type" aria-live="polite" class="sr-only">{{ isExpanded(message) ? 'Expanded' : 'Collapsed' }}</span>
                  <div
                    v-if="isExpanded(message) && (!editModeNoteId || message.id !== editModeNoteId)"
                    class="my-1 text-center"
                  >
                    <v-btn
                      :id="`${activeTab}-close-message-${message.id}`"
                      :aria-controls="`${message.type}-${message.id}-is-open`"
                      :aria-expanded="true"
                      :aria-label="`Close Message ${getButtonAriaLabel(message)}`"
                      color="primary"
                      :prepend-icon="mdiCloseCircle"
                      text="Close Message"
                      variant="text"
                      @click="onClickCloseMessage(message)"
                    />
                  </div>
                </template>
              </div>
            </td>
            <td class="column-details text-right" :class="{'vertical-top pt-2': isExpanded(message)}">
              <div
                v-if="!isExpanded(message) && isCancelledAppointment(message)"
                :id="`collapsed-${message.type}-${message.id}-status-cancelled`"
                class="collapsed-cancelled-icon float-right d-flex px-2 h-100 text-error text-no-wrap"
              >
                <v-icon :icon="mdiCalendarMinus" class="mr-1" />
                <div>
                  Canceled
                </div>
              </div>
              <div v-if="['appointment', 'eForm', 'note'].includes(message.type) && size(message.attachments)" class="px-2">
                <v-icon :aria-hidden="true" color="info" :icon="mdiPaperclip" />
              </div>
              <span v-if="['appointment', 'eForm', 'note'].includes(message.type)" class="sr-only">
                {{ size(message.attachments) ? 'Has attachments' : 'No attachments' }}
              </span>
            </td>
            <td class="column-date vertical-top text-right">
              <div
                :id="`timeline-tab-${activeTab}-date-${index}`"
                class="text-no-wrap py-2 pr-4"
              >
                <div v-if="!isExpanded(message) || !includes(['appointment', 'eForm', 'note'], message.type)">
                  <TimelineDate
                    :id="`collapsed-${message.type}-${message.id}-created-at`"
                    :date="message.setDate || message.updatedAt || message.createdAt"
                    :include-time-of-day="false"
                    :sr-prefix="message.type === 'appointment' ? 'Appointment date' : 'Last updated on'"
                  />
                </div>
                <div
                  v-if="isExpanded(message) && ['appointment', 'eForm', 'note'].includes(message.type)"
                  class="position-relative"
                  :class="{'td-note-timeline-expanded': displayUpdatedAt(message)}"
                >
                  <div class="expanded-timeline-container">
                    <div v-if="message.createdAt" :class="{'mb-2': !displayUpdatedAt(message)}">
                      <div :aria-hidden="true" class="text-medium-emphasis font-size-14">{{ message.type === 'appointment' ? 'Appt Date' : 'Created' }}:</div>
                      <TimelineDate
                        :id="`expanded-${message.type}-${message.id}-created-at`"
                        :date="message.createdAt"
                        :sr-prefix="message.type === 'appointment' ? 'Appointment date' : 'Created on'"
                        :include-time-of-day="(message.createdAt.length > 10) && (message.type !== 'appointment')"
                      />
                      <div
                        v-if="message.createdBy === 'YCBM' && message.endsAt"
                        :id="`expanded-${message.type}-${message.id}-appt-time-range`"
                      >
                        <span :aria-hidden="true">{{ getSameDayDate(message).visual }}</span>
                        <span class="sr-only">{{ getSameDayDate(message).screenReader }}</span>
                      </div>
                    </div>
                    <div v-if="displayUpdatedAt(message)">
                      <div :aria-hidden="true" class="mt-2 text-medium-emphasis font-size-14">Updated:</div>
                      <TimelineDate
                        :id="`expanded-${message.type}-${message.id}-updated-at`"
                        :date="message.updatedAt"
                        :include-time-of-day="message.updatedAt.length > 10"
                        class="mb-2"
                        sr-prefix="Last updated on"
                      />
                    </div>
                    <div v-if="message.setDate">
                      <div class="mt-2 text-medium-emphasis font-size-14">Set Date:</div>
                      <TimelineDate
                        :id="`expanded-${message.type}-${message.id}-set-date`"
                        :date="message.setDate"
                        class="mb-2"
                      />
                    </div>
                    <div class="text-medium-emphasis">
                      <router-link
                        v-if="['eForm', 'note'].includes(message.type) && message.id !== editModeNoteId"
                        :id="`advising-${message.type}-permalink-${message.id}`"
                        :to="`#permalink-${message.type}-${message.id}`"
                        @click.prevent="scrollToPermalink(message)"
                      >
                        Permalink <v-icon :icon="mdiLinkVariant" />
                      </router-link>
                    </div>
                  </div>
                </div>
                <span v-if="!message.updatedAt && !message.createdAt" class="sr-only">No last-updated date</span>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
  <div v-if="offerShowAll" class="text-center mb-4 mt-2">
    <v-btn
      :id="`timeline-tab-${activeTab}-previous-messages`"
      aria-controls="timeline-messages"
      :aria-expanded="isShowingAll"
      class="text-no-wrap"
      color="primary"
      density="comfortable"
      variant="text"
      @click="toggleShowAll"
    >
      <v-icon :icon="isShowingAll ? mdiMenuUp : mdiMenuRight" />
      {{ isShowingAll ? 'Hide' : 'Show' }} Previous Messages
    </v-btn>
  </div>
  <AreYouSureModal
    v-model="showDeleteConfirmModal"
    button-label-confirm="Delete"
    :function-cancel="cancelTheDelete"
    :function-confirm="deleteConfirmed"
    modal-header="Delete note"
  >
    Are you sure you want to delete the <span v-if="messageForDelete">"<b>{{ messageForDelete.subject }}</b>"</span> note?
  </AreYouSureModal>
</template>

<script setup>
import AdvisingAppointment from '@/components/appointment/AdvisingAppointment'
import AdvisingNote from '@/components/note/AdvisingNote'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import EditAdvisingNote from '@/components/note/EditAdvisingNote'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {alertScreenReader, decodeStudentUriAnchor, oxfordJoin, pluralize, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {
  capitalize,
  each,
  filter,
  find,
  get,
  includes,
  isEmpty,
  map,
  remove,
  size,
  slice,
  truncate
} from 'lodash'
import {computed, nextTick, onMounted, onUnmounted, ref, watch} from 'vue'
import {DateTime} from 'luxon'
import {deleteNote, getNote, markNoteRead} from '@/api/notes'
import {dismissStudentAlert} from '@/api/student'
import {isDirector} from '@/berkeley'
import {markAppointmentRead} from '@/api/appointments'
import {
  mdiCalendarMinus,
  mdiCheckBold,
  mdiClockOutline,
  mdiCloseCircle,
  mdiExclamationThick,
  mdiLinkVariant,
  mdiMenuDown,
  mdiMenuRight,
  mdiMenuUp,
  mdiPaperclip
} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session/index'

const props = defineProps({
  countPerActiveTab: {
    required: true,
    type: Number
  },
  selectedFilter: {
    default: undefined,
    required: false,
    type: String
  },
  filterTypes: {
    required: true,
    type: Object
  },
  messages: {
    required: true,
    type: Array
  },
  onCreateNewNote: {
    required: true,
    type: Function
  },
  student: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()

const allExpanded = ref(false)
const config = contextStore.config
const creatingNoteEvent = ref(undefined)
const currentUser = contextStore.currentUser
const defaultShowPerTab = ref(5)
const editModeNoteId = ref(undefined)
const eventHandlers = ref(undefined)
const isShowingAll = ref(false)
const messageForDelete = ref(undefined)
const openMessages = ref([])
const searchIndex = ref(undefined)
const searchResults = ref(undefined)
const showMyNotesOnly = ref(false)
const timelineQuery = ref('')

const activeTab = computed(() => props.selectedFilter || 'all')
const isExpandAllAvailable = computed(() => ['appointment', 'eForm', 'note'].includes(props.selectedFilter))
const messagesVisible = computed(() => {
  return (searchResults.value || (isShowingAll.value ? messagesPerType(props.selectedFilter) : slice(messagesPerType(props.selectedFilter), 0, defaultShowPerTab.value)))
})
const offerShowAll = computed(() => !searchResults.value && (props.countPerActiveTab > defaultShowPerTab.value))
const showDeleteConfirmModal = computed(() => !!messageForDelete.value)
const showDownloadNotesLink = computed(() => {
  const hasNonDrafts = () => {
    const notes = messagesPerType('note')
    return find(notes, n => !n.isDraft)
  }
  return ['eForm', 'note'].includes(props.selectedFilter)
    && (currentUser.isAdmin || isDirector(currentUser))
    && hasNonDrafts()
})
const showMyNotesToggle = computed(() => ['appointment', 'note'].includes(props.selectedFilter))

watch(() => props.selectedFilter, () => {
  allExpanded.value = false
  openMessages.value = []
  searchResults.value = null
  timelineQuery.value = ''
  alertScreenReader(describeTheActiveTab())
  refreshSearchIndex()
})

watch(timelineQuery, () => {
  if (timelineQuery.value) {
    const query = timelineQuery.value.replace(/\s/g, '').toLowerCase()
    const results = []
    each(searchIndex.value, entry => {
      if (entry.idx.indexOf(query) > -1) {
        results.push(entry.message)
      }
    })
    searchResults.value = results
  } else {
    searchResults.value = null
  }
})

const init = () => {
  refreshSearchIndex()
  if (currentUser.canAccessAdvisingData) {
    eventHandlers.value = {
      'note-creation-is-starting': onNoteCreateStartEvent,
      'note-created': afterNoteCreated,
      'note-updated': refreshNote,
      'notes-created': noteIdsBySid => {
        const noteId = noteIdsBySid[props.student.sid]
        if (noteId) {
          getNote(noteId).then(afterNoteCreated)
          refreshSearchIndex()
        }
      }
    }
    each(eventHandlers.value, (handler, eventType) => {
      contextStore.setEventHandler(eventType, handler)
    })
  }
}

onMounted(() => {
  const permalink = decodeStudentUriAnchor()
  if (permalink) {
    const obj = find(props.messages, function(m) {
      // Legacy advising notes have string IDs; BOA-created advising notes have integer IDs.
      if (m.id && m.id.toString() === permalink.messageId && m.type.toLowerCase() === permalink.messageType) {
        return true
      }
    })
    if (obj) {
      isShowingAll.value = true
      nextTick(() => {
        scrollToPermalink(obj)
      })
    }
  }
})

onUnmounted(() => {
  each(eventHandlers.value || {}, (handler, eventType) => {
    contextStore.removeEventHandler(eventType, handler)
  })
})

const afterEditAdvisingNote = (updatedNote, putFocusId) => {
  editModeNoteId.value = null
  putFocusNextTick(putFocusId || `edit-note-${updatedNote.id}-button`)
}

const afterNoteCreated = note => {
  creatingNoteEvent.value = null
  refreshNote(note)
  props.onCreateNewNote(note)
  refreshSearchIndex()
}

const afterNoteEditCancel = () => {
  putFocusNextTick(`edit-note-${editModeNoteId.value}-button`)
  editModeNoteId.value = null
}

const cancelTheDelete = () => {
  alertScreenReader('Canceled')
  putFocusNextTick(`delete-note-button-${messageForDelete.value.id}`)
  messageForDelete.value = undefined
}

const close = message => {
  if (editModeNoteId.value) {
    return false
  }
  if (isExpanded(message)) {
    openMessages.value = remove(
      openMessages.value,
      id => id !== message.transientId
    )
  }
  if (openMessages.value.length === 0) {
    allExpanded.value = false
  }
}

const deleteConfirmed = () => {
  const transientId = messageForDelete.value.transientId
  const predicate = ['transientId', transientId]
  const note = find(props.messages, predicate)
  remove(props.messages, predicate)
  remove(openMessages.value, value => transientId === value)
  messageForDelete.value = undefined
  deleteNote(note).then(() => {
    alertScreenReader('Note deleted')
    refreshSearchIndex()
  })
}

const describeTheActiveTab = () => {
  const inViewCount = isShowingAll.value || props.countPerActiveTab <= defaultShowPerTab.value ? props.countPerActiveTab : defaultShowPerTab.value
  const noun = props.selectedFilter ? props.filterTypes[props.selectedFilter].name.toLowerCase() : 'message'
  const pluralized = pluralize(noun, inViewCount)
  return isShowingAll.value && inViewCount > defaultShowPerTab.value
    ? `Showing all ${pluralized}`
    : `Showing ${props.countPerActiveTab > defaultShowPerTab.value ? 'the first' : ''} ${pluralized}`
}

const displayUpdatedAt = message => {
  return message.updatedAt && (message.updatedAt !== message.createdAt) && (message.type !== 'appointment')
}

const editNote = note => {
  editModeNoteId.value = note.id
  putFocusNextTick('edit-note-subject')
}

const formatDate = (isoDate, format) => DateTime.fromISO(isoDate).setZone(config.timezone).toFormat(format)

const getButtonAriaLabel = message => {
  const messageType = `${message.isDraft ? 'draft ' : ''}${isCancelledAppointment(message) ? 'cancelled ' : ''}${'eForm' === message.type ? '' : props.filterTypes[message.type].name}`
  return `${messageType} ${truncate(getMessageSummary(message), {length: 100, separator: '.'})}`
}

const getMessageSummary = message => {
  let summary = message.message
  if ('note' === message.type) {
    if (message.subject) {
      summary = message.subject
    } else if (size(message.message)) {
      summary = stripHtmlAndTrim(message.message).replace(/\n\r/g, ' ')
    } else if (message.category) {
      summary = `${message.category}${message.subcategory ? `, ${message.subcategory}` : ''}`
    } else {
      summary = `${!isEmpty(message.author.departments) ? message.author.departments[0].name : ''} advisor ${message.author.name || ''}`
      if (message.topics && size(message.topics)) {
        summary += `: ${oxfordJoin(message.topics)}`
      }
    }
  } else if ('eForm' === message.type) {
    summary = `eForm: ${message.eForm.action} – ${message.eForm.status}`
  } else if ('appointment' === message.type) {
    if (message.appointmentTitle && message.appointmentTitle.trim().length) {
      summary = message.appointmentTitle
    } else if (message.details && message.details.trim().length) {
      summary = stripHtmlAndTrim(message.details).replace(/\n\r/g, ' ')
    } else {
      summary = message.legacySource === 'SIS' ? 'Imported SIS Appt' : 'Advising Appt'
      if (get(message, 'advisor.name')) {
        summary = `${summary}: ${message.advisor.name}`
      }
    }
  }
  return summary
}

const getRowAriaLabelledBy = (message, index) => {
  const dateId = `timeline-tab-${activeTab.value}-date-${index}`
  const messageTypeId = 'eForm' === message.type ? '' : `timeline-tab-${activeTab.value}-pill-${message.type}-${message.id}`
  const messageSummaryId = 'requirement' === message.type ? `timeline-tab-${activeTab.value}-message-${message.type}-${message.id}` : `${message.type}-${message.id}-message`
  return `${messageTypeId} ${messageSummaryId} ${dateId}`
}

const getSameDayDate = message => {
  const format = 'h:mm a'
  return {
    visual: `${formatDate(message.createdAt, format)} - ${formatDate(message.endsAt, format)}`,
    screenReader: `${formatDate(message.createdAt, format)} to ${formatDate(message.endsAt, format)}`
  }
}

const isCancelledAppointment = message => {
  return (message.type === 'appointment' && message.createdBy === 'YCBM' && message.status === 'cancelled')
}

const isEditable = message => {
  return message.type === 'note' && !message.legacySource
}

const isExpanded = message => {
  return includes(openMessages.value, message.transientId)
}

const markRead = message => {
  if (!message.read) {
    message.read = true
    if (includes(['alert', 'hold'], message.type)) {
      dismissStudentAlert(message.id)
    } else if (['eForm', 'note'].includes(message.type)) {
      markNoteRead(message.id)
    } else if (message.type === 'appointment') {
      markAppointmentRead(message.id)
    }
  }
}

const messagesPerType = type => {
  if (!type) {
    return props.messages
  } else if (showMyNotesToggle.value && showMyNotesOnly.value) {
    return filter(props.messages, m => {
      const uid = (m.author && m.author.uid) || (m.advisor && m.advisor.uid)
      return m.type === type && uid === currentUser.uid
    })
  } else {
    return filter(props.messages, ['type', type])
  }
}

const onClickDeleteNote = message => {
  // The following opens the "Are you sure?" modal
  messageForDelete.value = message
}

const onClickCloseMessage = (message) => {
  putFocusNextTick(`timeline-tab-${activeTab.value}-message-${message.type}-${message.id}`, {scroll: false})
  close(message)
}

const onClickOpenMessage = message => {
  open(message)
  if (userCanEdit(message)) {
    putFocusNextTick(`edit-note-${message.id}-button`, {scroll: false})
  } else if (userCanDelete(message)) {
    putFocusNextTick(`delete-note-button-${message.id}`, {scroll: false})
  } else {
    putFocusNextTick(`timeline-tab-${activeTab.value}-message-${message.type}-${message.id}`, {scroll: false})
  }
}

const onNoteCreateStartEvent = event => {
  if (includes(event.completeSidSet, props.student.sid)) {
    creatingNoteEvent.value = event
  }
}

const open = message => {
  if ((['eForm', 'note'].includes(message.type) && message.id === editModeNoteId.value) || message.type === 'requirement') {
    return false
  }
  if (!isExpanded(message)) {
    openMessages.value.push(message.transientId)
  }
  markRead(message)
  if (isExpandAllAvailable.value && openMessages.value.length === messagesPerType(props.selectedFilter).length) {
    allExpanded.value = true
  }
}

const refreshNote = updatedNote => {
  const note = get(updatedNote, 'id') ? find(props.messages, ['id', updatedNote.id]) : null
  if (note) {
    note.attachments = updatedNote.attachments
    note.body = note.message = updatedNote.body
    note.contactType = updatedNote.contactType
    note.isDraft = updatedNote.isDraft
    note.isPrivate = updatedNote.isPrivate
    note.setDate = updatedNote.setDate
    note.subject = updatedNote.subject
    note.topics = updatedNote.topics
    note.updatedAt = updatedNote.updatedAt
    refreshSearchIndex()
  }
}

const refreshSearchIndex = () => {
  searchIndex.value = []
  const messages = ['appointment', 'eForm', 'note'].includes(props.selectedFilter) ? messagesPerType(props.selectedFilter) : []
  each(messages, m => {
    const advisor = m.author || m.advisor
    const idx = [
      advisor.name,
      (map(advisor.departments || [], 'name')).join(),
      advisor.email,
      m.body,
      m.category,
      m.createdBy,
      JSON.stringify(m.eForm || {}),
      m.legacySource,
      m.message,
      m.subcategory,
      m.subject,
      (m.topics || []).join()
    ].join().replace(/\s/g, '').toLowerCase()
    searchIndex.value.push({idx: idx.toLowerCase(), message: m})
  })
}

const scrollToPermalink = message => {
  isShowingAll.value = true
  open(message)
  putFocusNextTick(`permalink-${message.type}-${message.id}`, {scrollBlock: 'start'})
}

const toggleExpandAll = () => {
  isShowingAll.value = true
  allExpanded.value = !allExpanded.value
  if (allExpanded.value) {
    each(messagesPerType(props.selectedFilter), open)
    alertScreenReader(`All ${props.selectedFilter}s expanded`)
  } else {
    each(messagesPerType(props.selectedFilter), close)
    alertScreenReader(`All ${props.selectedFilter}s collapsed`)
  }
}

const toggleShowAll = () => {
  isShowingAll.value = !isShowingAll.value
  alertScreenReader(describeTheActiveTab())
}

const userCanDelete = message => {
  return isEditable(message) && message.type === 'note' && (currentUser.isAdmin || (message.isDraft && message.author.uid === currentUser.uid))
}

const userCanEdit = message => {
  return isEditable(message) && message.type === 'note' && (currentUser.uid === message.author.uid && (!message.isPrivate || currentUser.canAccessPrivateNotes))
}

init()

</script>

<style>
.academic-timeline-search-input input {
  max-height: 30px !important;
  min-height: 30px !important;
  padding: 0 10px;
}
</style>

<style scoped>
table {
  border-collapse: collapse;
  border-spacing: 0 0.05em;
  min-width: 500px;
  table-layout: fixed;
}
.academic-timeline-search-input {
  width: 200px;
}
.collapsed-cancelled-icon {
  font-size: 14px;
  text-transform: uppercase;
}
.column-date {
  width: 120px;
}
.column-details {
  width: 130px;
}
.column-message {
  min-width: 200px;
  width: 60%;
}
.column-pill {
  vertical-align: top;
  white-space: nowrap;
  width: 115px;
}
.expanded-timeline-container {
  position: absolute;
  right: 0;
}
.message-open {
  flex-flow: row wrap;
  display: flex;
  min-height: 40px;
  scroll-margin-top: 110px !important;
}
.message-row:active,
.message-row:focus,
.message-row:focus-within,
.message-row:hover {
  background-color: rgb(var(--v-theme-sky-blue));
}
.message-row-read {
  background-color: rgb(var(--v-theme-light-grey));
}
.note-actions {
  width: 116px;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.pill-alert {
  width: 60px;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.pill-appointment {
  width: 100px;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.pill-eForm {
  width: 60px;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.pill-hold {
  width: 60px;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.pill-note {
  width: 100px;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.pill-requirement {
  width: 100px;
}
.requirements-icon {
  padding: 0 4px 0 0;
  width: 20px;
}
.td-note-timeline-expanded {
  min-height: 180px;
  position: relative;
}
</style>
