<template>
  <v-data-table :headers="headers" :items="sortedItems" :search="search" :loading="isLoading"
    :loading-text="$t('generic.loading')" 
    :no-data-text="$t('vuetify.noDataAvailable')" 
    :footer-props="{
      showFirstLastPage: true,
      'items-per-page-options': [10, 50, 100],
      'items-per-page-text': $t('vuetify.itemsPerPageText'),
      'page-text': $t('dataset.pageText')
    }" item-key="id" show-select @input="$emit('input', $event)" @update:options="updateOptions">
    <template #top>
      <v-text-field v-model="search" 
      :prepend-inner-icon="mdiMagnify" 
      :label="$t('generic.search')" single-line
        hide-details filled />
    </template>

    <template #[`item.username`]="{ item }">
      <span>{{ item.username }}</span>
    </template>
    <template #[`item.email`]="{ item }">
      <span>{{ item.email }}</span>
    </template>
    <template #[`item.isSuperuser`]="{ item }">
      <span>{{ item.isSuperuser ? 'Yes' : 'No' }}</span>
    </template>
    <template #[`item.last_login`]="{ item }">
      <span>
        {{ item.last_login ? dateFormat(
          dateParse(
            item.last_login, 
            'YYYY-MM-DDTHH:mm:ss'), 
            'YYYY/MM/DD HH:mm') : '-' }}
      </span>
    </template>

    <!-- Actions column -->
    <template #[`item.actions`]="{ item }">
      <v-icon
        small
        class="mr-2 hoverable"
        :title="$t('generic.edit') || 'Edit'"
        @click="goEdit(item.id)"
      >{{ mdiPencil }}</v-icon>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { mdiMagnify, mdiPencil } from '@mdi/js'
import { dateFormat } from '@vuejs-community/vue-filter-date-format'
import { dateParse } from '@vuejs-community/vue-filter-date-parse'
import type { PropType } from 'vue'
import Vue from 'vue'
import { UserItem } from '~/domain/models/user/user'

export default Vue.extend({
  props: {
    isLoading: {
      type: Boolean,
      default: false,
      required: true
    },
    items: {
      type: Array as PropType<UserItem[]>,
      default: () => [],
      required: true
    }
  },

  data() {
    return {
      search: this.$route.query.q || '',
      sortBy: 'username',
      sortDesc: false,
      mdiMagnify,
      mdiPencil,
      dateFormat,
      dateParse
    }
  },

  computed: {
    headers() {
      return [
        { text: this.$t('username'), value: 'username', sortable: true },
        { text: this.$t('email'), value: 'email', sortable: true },
        { text: this.$t('SuperUser'), value: 'isSuperuser', sortable: true },
        { text: this.$t('last login'), value: 'last_login', sortable: true },
        { text: '', value: 'actions', sortable: false }
      ]
    },
    filteredItems() {
      if (!this.search) return this.items;
      const searchLower = this.search.toLowerCase();
      return this.items.filter(item =>
        item.username.toLowerCase().includes(searchLower) ||
        item.email.toLowerCase().includes(searchLower)
      );
    },
    sortedItems() {
      return [...this.filteredItems].sort((a, b) => {
        const modifier = this.sortDesc ? -1 : 1;
        if (a[this.sortBy] < b[this.sortBy]) return -1 * modifier;
        if (a[this.sortBy] > b[this.sortBy]) return 1 * modifier;
        return 0;
      });
    }
  },

  methods: {
    goEdit(id) {
      this.$router.push(`/users/${id}/edit`)
    },
    updateOptions(options) {
      this.sortBy = options.sortBy[0] || 'username';
      this.sortDesc = options.sortDesc[0] || false;
    }
  }
})
</script>

<style scoped>
::v-deep .v-data-table {
  width: 100%;
}
</style>