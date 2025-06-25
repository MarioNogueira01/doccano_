<template>
  <v-dialog v-model="dialog" max-width="700">
    <v-card>
      <v-card-title>
        {{ $t('compare_annotations') || 'Multi-User Annotation Comparison' }}
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-select
                v-model="selectedUsers"
                :items="projectUsers"
                item-text="username"
                item-value="user"
                :label="$t('select_users') || 'Select Users to Compare'"
                multiple
                chips
                persistent-hint
                hint="Select 2 or more users to compare their annotations across all documents"
                required
                :disabled="loading"
              ></v-select>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="close" :disabled="loading">{{ $t('cancel') || 'Cancel' }}</v-btn>
        <v-btn
          color="primary"
          text
          @click="compare"
          :disabled="!isValid || loading"
          :loading="loading"
        >
          {{ $t('compare') || 'Compare' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    value: {
      type: Boolean,
      default: false
    },
    projectId: {
      type: [Number, String],
      required: true
    },
    documents: {
      type: Array,
      default: () => []
    },
    projectUsers: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      selectedUsers: []
    }
  },

  computed: {
    dialog: {
      get() {
        return this.value
      },
      set(val) {
        this.$emit('input', val)
      }
    },
    isValid() {
      return this.selectedUsers && this.selectedUsers.length >= 2
    }
  },

  methods: {
    close() {
      this.dialog = false
      this.selectedUsers = []
    },

    compare() {
      if (this.isValid) {
        console.log('FormCompareAnnotations - Selected users:', this.selectedUsers)
        console.log('FormCompareAnnotations - Emitting compare event with users:', this.selectedUsers)
        this.$emit('compare', {
          users: this.selectedUsers
        })
        // Don't close the dialog here - let the parent handle it after checking for errors
      }
    }
  }
})
</script>