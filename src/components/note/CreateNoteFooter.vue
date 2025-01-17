<template>
  <v-card-actions class="modal-footer d-block px-6">
    <v-alert
      v-if="boaSessionExpired"
      id="uh-oh-session-time-out"
      aria-live="polite"
      class="mb-6"
    >
      <SessionExpired />
    </v-alert>
    <v-row v-if="!boaSessionExpired" class="d-flex flex-wrap" no-gutters>
      <v-col>
        <v-btn
          v-if="mode === 'editDraft'"
          id="create-note-cancel-draft"
          aria-label="Cancel Edit Draft"
          class="mr-2"
          color="error"
          :disabled="isSaving || isUpdatingDraft"
          text="Cancel"
          variant="outlined"
          @click="exit"
        />
        <ProgressButton
          v-if="!['editTemplate'].includes(mode)"
          id="btn-save-as-template"
          :action="saveTemplate"
          :disabled="isSaving || !trim(model.subject) || !!model.setDate || !!model.contactType"
          :in-progress="isSavingTemplate"
          text="Save as template"
          variant="text"
        />
      </v-col>
      <v-col class="d-flex justify-end">
        <ProgressButton
          v-if="model.isDraft"
          id="save-as-draft-button"
          :action="updateDraft"
          class="mr-3"
          :disabled="isSaving || isUpdatingDraft || (!trim(model.subject) && !trim(model.body))"
          :in-progress="isUpdatingDraft"
          text="Save and Close Draft"
          variant="text"
        />
        <ProgressButton
          v-if="mode === 'editTemplate'"
          id="btn-update-template"
          :action="updateTemplate"
          :disabled="isSaving || !model.subject"
          :in-progress="isSaving"
          text="Update Template"
        />
        <ProgressButton
          v-if="!['editTemplate'].includes(mode)"
          id="create-note-button"
          :action="publish"
          :disabled="isSaving || isEmpty(completeSidSet) || !trim(model.subject)"
          :in-progress="isPublishing"
          text="Publish Note"
        />
        <v-btn
          v-if="mode !== 'editDraft'"
          id="create-note-cancel"
          :aria-label="mode === 'editTemplate' ? 'Discard Template Edits' : 'Discard Note Edits'"
          class="ml-2"
          color="error"
          :disabled="isSaving || isUpdatingDraft"
          text="Discard"
          variant="outlined"
          @click="discard"
        />
      </v-col>
    </v-row>
  </v-card-actions>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
import SessionExpired from '@/components/note/SessionExpired'
import {alertScreenReader, invokeIfAuthenticated} from '@/lib/utils'
import {isEmpty, size, startsWith, trim} from 'lodash'
import {ref} from 'vue'
import {storeToRefs} from 'pinia'
import {updateAdvisingNote} from '@/stores/note-edit-session/utils'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  discard: {
    required: true,
    type: Function
  },
  exit: {
    required: true,
    type: Function
  },
  saveAsTemplate: {
    required: true,
    type: Function
  },
  showAlert: {
    required: true,
    type: Function
  },
  updateTemplate: {
    required: true,
    type: Function
  }
})

const noteStore = useNoteStore()
const {boaSessionExpired, completeSidSet, isSaving, mode, model} = storeToRefs(noteStore)
const isPublishing = ref(false)
const isSavingTemplate = ref(false)
const isUpdatingDraft = ref(false)

const publish = () => {
  noteStore.setIsDraft(false)
  isPublishing.value = true
  updateNote('Publishing note...').then(() => isPublishing.value = false)
}

const saveTemplate = () => {
  isSavingTemplate.value = true
  props.saveAsTemplate().then(() => isSavingTemplate.value = false)
}

const updateDraft = () => {
  isUpdatingDraft.value = true
  updateNote('Saving draft...').then(() => isUpdatingDraft.value = false)
}

const updateNote = (alert) => {
  alertScreenReader(alert)
  return new Promise(resolve => {
    noteStore.setIsSaving(true)
    const action = startsWith(mode.value, 'create') ? 'created' : 'updated'
    const ifAuthenticated = () => {
      if (model.value.isDraft || (model.value.subject && size(completeSidSet.value))) {
        props.showAlert(alert, 60)
        updateAdvisingNote().then(() => {
          alertScreenReader(model.value.isDraft ? `Draft note ${action}` : `Note ${action}`)
          noteStore.setIsSaving(false)
          props.exit(false)
          resolve()
        })
      } else {
        resolve()
      }
    }
    invokeIfAuthenticated(ifAuthenticated, () => {
      noteStore.onBoaSessionExpires()
      noteStore.setIsSaving(false)
      props.exit(true)
      resolve()
    })
  })
}
</script>
