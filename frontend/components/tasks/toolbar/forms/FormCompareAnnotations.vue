<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-card-title>
        {{ $t('compare_annotations') || 'Compare Annotations' }}
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-select
                v-model="selectedDocument"
                :items="documents"
                item-text="text"
                item-value="id"
                :label="$t('select_document') || 'Select Document'"
                required
              ></v-select>
            </v-col>
            <v-col cols="12">
              <v-select
                v-model="user1"
                :items="projectUsers"
                item-text="username"
                item-value="id"
                :label="$t('first_user') || 'First User'"
                required
              ></v-select>
            </v-col>
            <v-col cols="12">
              <v-select
                v-model="user2"
                :items="projectUsers"
                item-text="username"
                item-value="id"
                :label="$t('second_user') || 'Second User'"
                required
              ></v-select>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="close">{{ $t('cancel') || 'Cancel' }}</v-btn>
        <v-btn
          color="primary"
          text
          @click="compare"
          :disabled="!isValid"
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
    }
  },

  data() {
    return {
      selectedDocument: null,
      user1: null,
      user2: null
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
      return this.selectedDocument && this.user1 && this.user2 && this.user1 !== this.user2
    }
  },

  methods: {
    close() {
      this.dialog = false
      this.selectedDocument = null
      this.user1 = null
      this.user2 = null
    },

    compare() {
      if (this.isValid) {
        this.$emit('compare', {
          documentId: this.selectedDocument,
          user1: this.user1,
          user2: this.user2
        })
        this.close()
      }
    }
  }
})
</script>